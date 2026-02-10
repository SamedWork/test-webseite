import uuid
import os
import shutil
import tempfile
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from collections import OrderedDict
from app.services.excel import read_excel
from app.services.vv_overlay import create_vv_pdf
from app.services.ol_overlay import create_ol_pdf
from app.services.pdf_merge import merge_pdfs
from app.services.zip import zip_files
from app.services.vv_overlay import split_multiple_objects

def parse_we_list(value: str) -> list[int]:
    if not value:
        return []

    parts = [p.strip() for p in str(value).split(",")]
    return [int(p) for p in parts if p.isdigit()]

def cleanup(path: str):
    shutil.rmtree(path, ignore_errors=True)

def sum_vertrags_we(we_list: list[int]) -> int:
    return sum(we_list)

def sanitize_value(v):
    if isinstance(v, float):
        if v != v:  # Check auf NaN
            return ""
        if v.is_integer():
            v = int(v)
    
    if isinstance(v, (str, int)):
        v = str(v)
        return (
            v.replace("\u00a0", " ")   # NBSP
             .replace("\u200b", "")    # Zero-width space
             .replace("\u2011", "-")   # non-breaking hyphen
             .strip()
        )
    return v

def safe_filename(value: str, max_len: int = 80) -> str:
    if not value:
        return "objekt"

    name = (
        value
        .replace("/", "-")
        .replace(",", ",")
    )

    name = re.sub(r"[^\w\-, ]+", "", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name[:max_len]

def normalize_street_list(value: str) -> str:
    if not value or not isinstance(value, str):
        return value

    parts = [p.strip() for p in value.split(",") if p.strip()]
    result = []

    current_street = None
    street_re = re.compile(r"^(.+?)\s+(\d.*)$")

    for part in parts:
        m = street_re.match(part)
        if m:
            # volle Straße + Nummer
            street, number = m.groups()
            current_street = street
            result.append(f"{street} {number}")
        else:
            # letzte Straße verwenden
            if current_street:
                result.append(f"{current_street} {part}")
            else:
                # Fallback: nichts ableitbar
                result.append(part)

    return ", ".join(result)

def is_empty(v):
    return (
        v is None
        or (isinstance(v, float) and v != v)  # NaN
        or str(v).strip() == ""
    )

def is_weg(row: dict) -> bool:
    return is_empty(row.get("Vertragsp. Firma")) and is_empty(row.get("Vertragsp. Name"))

def shorten_streets(street_str: str) -> str:
    parts = [p.strip() for p in street_str.split(",") if p.strip()]
    streets = OrderedDict()

    for part in parts:
        match = re.match(r"(.+?)\s+(\d+.*)", part)
        if not match:
            streets.setdefault(part, [])
            continue

        name, number = match.groups()
        streets.setdefault(name, []).append(number)

    result = []
    for name, numbers in streets.items():
        if numbers:
            result.append(f"{name} {','.join(numbers)}")
        else:
            result.append(name)

    return ", ".join(result)

router = APIRouter(prefix="/upload")

@router.post("/")
async def upload_excel(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Nur Excel-Dateien erlaubt")

    # --- Isolierter Temp-Ordner ---
    workdir = tempfile.mkdtemp(prefix="vv_")

    rows = []

    for row in read_excel(file):
        row = {k: sanitize_value(v) for k, v in row.items()}

        for col in (
            "Objekt Str + Hnr",
            "Bevollm. Str. Hnr",
            "Vertragsp. Str + Hnr",
        ):
            if col in row:
                row[col] = normalize_street_list(row[col])

        rows.append(row)

    final_pdfs = []

    for i, row in enumerate(rows):
        # VV immer erzeugen
        vv_pdf = create_vv_pdf(row, i, workdir)
        pdfs_to_merge = [vv_pdf]

        # Mehrere Objekte?
        objects = split_multiple_objects(row.get("Objekt Str + Hnr", ""))
        we_list = parse_we_list(row.get("Anzahl WE"))

        if len(objects) > 1:
            CHUNK_SIZE = 12

            for chunk_idx in range(0, len(objects), CHUNK_SIZE):
                obj_chunk = objects[chunk_idx:chunk_idx + CHUNK_SIZE]
                we_chunk = we_list[chunk_idx:chunk_idx + CHUNK_SIZE]

                ol_pdf = create_ol_pdf(
                    objects=obj_chunk,
                    plz=row.get("Objekt PLZ", ""),
                    ort=row.get("Objekt Ort", ""),
                    we_list=we_chunk,
                    we_sum=sum_vertrags_we(we_list),
                    index=f"{i}_{chunk_idx // CHUNK_SIZE}",
                    workdir=workdir,
                    start_lfd=chunk_idx
                )
                pdfs_to_merge.append(ol_pdf)

        # VV (+ OL) zusammenfügen
        if is_weg(row):
            weg_name = f"WEG {shorten_streets(row.get('Objekt Str + Hnr'))}, {row.get('Objekt PLZ')} {row.get('Objekt Ort')}"
            filename = safe_filename(weg_name)
        else:
            filename = safe_filename(f"{shorten_streets(row.get('Objekt Str + Hnr'))}, {row.get('Objekt PLZ')} {row.get('Objekt Ort')}")

        final_pdf = merge_pdfs(
            pdfs_to_merge,
            f"{workdir}/{filename}.pdf"
)

        final_pdfs.append(final_pdf)

    zip_path = zip_files(final_pdfs, workdir)
    zip_path = os.path.abspath(zip_path)

    # --- Cleanup nach Download ---
    background_tasks.add_task(cleanup, workdir)

    return FileResponse(
        path=zip_path,
        filename="Versorgungsvereinbarungen.zip",
        media_type="application/zip"
    )
