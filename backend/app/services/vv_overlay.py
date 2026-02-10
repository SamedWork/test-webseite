from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
import re
from collections import OrderedDict
from datetime import date

VV_TEMPLATE = "app/templates/VV_Vorlage.pdf"
FONT_SIZE = 6
FIELD_MAPPING = {

    # OBJEKT / HAUS
    "Objekt Str + Hnr": (38 * mm, 210 * mm, FONT_SIZE, 45 * mm), # Wird getrennt verarbeitet
    "Objekt PLZ":       (38 * mm, 205.5 * mm, FONT_SIZE, 45 * mm),
    "Objekt Ort":       (58 * mm, 205.5 * mm, FONT_SIZE, 45 * mm),
    "Anzahl WE":        (55 * mm, 201 * mm, FONT_SIZE, 45 * mm),
    "Datum":        (65 * mm, 167 * mm, FONT_SIZE, 45 * mm),
    "__MULTI_OBJECT_CHECK__": (71 * mm, 201 * mm, 10, 45 * mm),

    # BEVOLLMÄCHTIGTE
    "Bevollm. Firma":           (122 * mm, 228.5 * mm, FONT_SIZE, 70 * mm),
    "Bevollm. Name":            (122 * mm, 223.5 * mm, FONT_SIZE, 70 * mm),
    "Bevollm. Vorname":         (127 * mm, 218.5 * mm, FONT_SIZE, 65 * mm), 
    "Bevollm. Str. Hnr":        (1 * mm, 1 * mm, FONT_SIZE, 45 * mm), # Wird getrennt verarbeitet
    "Bevollm. PLZ":             (122 * mm, 208.5 * mm, FONT_SIZE, 45 * mm),
    "Bevollm. Ort":             (142 * mm, 208.5 * mm, FONT_SIZE, 50 * mm),

    # VERTRAGSPARTNER
    "Vertragsp. Firma":           (38 * mm, 75.5 * mm, FONT_SIZE, 70 * mm),
    "Vertragsp. Name":            (38 * mm, 70.5 * mm, FONT_SIZE, 70 * mm),
    "Vertragsp. Vorname":         (42 * mm, 66.5 * mm, FONT_SIZE, 65 * mm),
    "Vertragsp. Str + Hnr":       (1 * mm, 1 * mm, FONT_SIZE, 45 * mm),  # Wird getrennt verarbeitet
    "Vertragsp. PLZ":             (38 * mm, 58 * mm, FONT_SIZE, 45 * mm),
    "Vertragsp. Ort":             (58 * mm, 58 * mm, FONT_SIZE, 50 * mm),
}

# HILFSFUNKTION
def split_strasse_hausnummer(text: str):
    if not text:
        return None, None

    parts = [p.strip() for p in text.split(",") if p.strip()]

    main_street = None
    house_numbers = []

    for part in parts:
        match = re.match(r"(.+?)\s+(\d+[a-zA-Z]?(?:/\d+)?)$", part)
        if not match:
            continue

        street, number = match.groups()

        if main_street is None:
            main_street = street

        if street == main_street:
            house_numbers.append(number)

    if not main_street:
        return None, None

    return main_street, ",".join(house_numbers)
def parse_anzahl_we(value):
    if value is None:
        return None

    value = str(value).strip()

    if "," in value:
        total = 0
        for part in value.split(","):
            part = part.strip()
            if part.isdigit():
                total += int(part)
        return total if total > 0 else None

    if value.isdigit():
        return int(value)

    return None
def split_multiple_objects(value: str) -> list[str]:
    if not value:
        return []

    return [v.strip() for v in value.split(",") if v.strip()]
def draw_text_in_box(
    c: canvas.Canvas,
    text: str,
    x: float,
    y_base: float,
    box_width: float,
    max_lines: int = 2,
    font: str = "Helvetica",
    font_size: int = 8,
    min_font_size: int = 5,
    line_spacing: float = 1.2,
):
    if not text:
        return

    text = str(text)

    def break_word_chars(word: str, size: int) -> list[str]:
        parts, current = [], ""
        for ch in word:
            if stringWidth(current + ch, font, size) <= box_width:
                current += ch
            else:
                parts.append(current)
                current = ch
        if current:
            parts.append(current)
        return parts

    def split_word(word: str) -> list[str]:
        parts = []
        current = ""
        for ch in word:
            current += ch
            if ch == "-":
                parts.append(current)
                current = ""
        if current:
            parts.append(current)
        return parts

    # Tokens erzeugen (Bindestrich = Umbruchstelle)
    tokens = []
    for w in text.split(" "):
        tokens.extend(split_word(w))

    for size in range(font_size, min_font_size - 1, -1):
        c.setFont(font, size)
        lines = []
        current = ""

        for token in tokens:
            # kein Leerzeichen wenn current mit "-" endet
            sep = "" if current.endswith("-") or not current else " "
            candidate = current + sep + token

            if stringWidth(candidate, font, size) <= box_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = token

                if stringWidth(current, font, size) > box_width:
                    parts = break_word_chars(current, size)
                    lines.extend(parts[:-1])
                    current = parts[-1]

        if current:
            lines.append(current)

        effective_size = size - 1 if len(lines) > 1 else size
        if effective_size < min_font_size:
            continue

        c.setFont(font, effective_size)

        if (
            len(lines) <= max_lines
            and all(stringWidth(line, font, effective_size) <= box_width for line in lines)
        ):
            final_lines = lines
            final_size = effective_size
            break
    else:
        c.setFont(font, min_font_size)
        parts = break_word_chars(text, min_font_size)
        final_lines = parts[:max_lines]
        final_size = min_font_size

    # Vertikal zentrieren
    c.setFont(font, final_size)
    line_height = final_size * line_spacing
    total_height = len(final_lines) * line_height
    start_y = y_base + (total_height - line_height) / 2

    y = start_y
    for line in final_lines:
        c.drawString(x, y, line)
        y -= line_height
def is_empty(v):
    return (
        v is None
        or (isinstance(v, float) and v != v)  # NaN
        or str(v).strip() == ""
    )
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
def split_word(word: str):
    # trennt an "-" UND behält den Bindestrich
    parts = []
    current = ""
    for ch in word:
        current += ch
        if ch == "-":
            parts.append(current)
            current = ""
    if current:
        parts.append(current)
    return parts
def split_strasse_hausnummer_lexico(text: str):
    if not text:
        return None, None

    parts = [p.strip() for p in text.split(",") if p.strip()]
    pairs = []

    for part in parts:
        match = re.match(r"(.+?)\s+(\d+[a-zA-Z]?(?:/\d+)?)$", part)
        if not match:
            continue

        street, number = match.groups()
        pairs.append((street, number))

    if not pairs:
        return None, None

    # kleinste Hausnummer
    smallest_number = min(number for _, number in pairs)

    # alle Straßen mit dieser Hausnummer
    candidates = [(street, number) for street, number in pairs if number == smallest_number]

    # lexikografisch kleinste Straße
    chosen_street, chosen_number = min(candidates, key=lambda x: x[0])

    return chosen_street, chosen_number

def create_vv_pdf(row: dict, index: int, workdir: str) -> str:
    overlay_path = f"{workdir}/vv_overlay_{index}.pdf"
    output_path = f"{workdir}/vv_filled_{index}.pdf"

    c = canvas.Canvas(overlay_path)

    objects = split_multiple_objects(row.get("Objekt Str + Hnr", ""))
    multi_object = len(objects) > 1


    # Kosten
    draw_text_in_box(
        c=c,
        text="8.39",
        x=36 * mm,
        y_base=95.5 * mm,
        box_width=50*mm,
        max_lines=2,
        font_size=6
    )
    draw_text_in_box(
        c=c,
        text="9.99",
        x=93.5 * mm,
        y_base=95.5 * mm,
        box_width=50*mm,
        max_lines=2,
        font_size=6
    )
    # -------------------------------------------- Kreuz handeling --------------------------------------------
    # Kreuz bei mehreren Objekten
    if multi_object:
        x, y, font_size, box_width = FIELD_MAPPING["__MULTI_OBJECT_CHECK__"]
        c.setFont("Helvetica", 9)
        c.drawString(x, y, "X")

    # Kreuz bei Bevollmächtigten
    firma = row.get("Bevollm. Firma")
    geschlecht = str(row.get("Bevollm. Herr/Frau (H/F)") or "").strip().lower()

    if not is_empty(firma):
        #Firma hat IMMER Vorrang
        c.setFont("Helvetica", 9)
        c.drawString(141.5 * mm, 238 * mm, "X")

    else:
        if geschlecht in ("h", "herr"):
            c.setFont("Helvetica", 9)
            c.drawString(115 * mm, 238 * mm, "X")

        elif geschlecht in ("f", "frau"):
            c.setFont("Helvetica", 9)
            c.drawString(128.5 * mm, 238 * mm, "X")

    # Kreuz bei Vertragspartner
    firma = row.get("Vertragsp. Firma")
    geschlecht = str(row.get("Vertragsp. Herr/Frau (H/F)") or "").strip().lower()

    if not is_empty(firma):
        #Firma hat IMMER Vorrang
        c.setFont("Helvetica", 9)
        c.drawString(57.5 * mm, 83.5 * mm, "X")

    else:
        if geschlecht in ("h", "herr"):
            c.setFont("Helvetica", 9)
            c.drawString(31 * mm, 83.5 * mm, "X")

        elif geschlecht in ("f", "frau"):
            c.setFont("Helvetica", 9)
            c.drawString(44.5 * mm, 83.5 * mm, "X")
        else:
            c.setFont("Helvetica", 9)
            c.drawString(57.5 * mm, 83.5 * mm, "X")
    
    # -------------------------------------------- Felder handeling --------------------------------------------
    for field, (x, y, font_size, box_width) in FIELD_MAPPING.items():

        # DIREKTZUGRIFF auf ROW
        value = row.get(field)

        # Adresse komplett überspringen bei mehreren Objekten
        if multi_object and field in {
            "Objekt Str + Hnr",
            "Objekt PLZ",
            "Objekt Ort",
        }:
            continue
        


        # Sonderlogik Straße + Hausnr (nur bei EINEM Objekt)
        if field == "Objekt Str + Hnr" and not multi_object:
            first_object = objects[0]
            street, house_number = split_strasse_hausnummer(first_object)

            c.setFont("Helvetica", font_size)
            if street:
                draw_text_in_box(
                    c=c,
                    text=street,
                    x=38 * mm,
                    y_base=210 * mm,
                    box_width=50*mm,
                    max_lines=2,
                    font_size=font_size
                )
            if house_number:
                draw_text_in_box(
                    c=c,
                    text=house_number,
                    x=94 * mm,
                    y_base=210 * mm,
                    box_width=box_width,
                    max_lines=2,
                    font_size=font_size
                )
            continue
        if field == "Bevollm. Str. Hnr" and not is_empty(value):
            kombination = row.get("Bevollm. Str. Hnr")
            street, house_number = split_strasse_hausnummer(kombination)

            c.setFont("Helvetica", font_size)
            if street:
                draw_text_in_box(
                    c=c,
                    text=street,
                    x=122 * mm,
                    y_base=213.5 * mm,
                    box_width=50*mm,
                    max_lines=2,
                    font_size=font_size
                )
            if house_number:
                draw_text_in_box(
                    c=c,
                    text=house_number,
                    x=178 * mm,
                    y_base=213.5 * mm,
                    box_width=box_width,
                    max_lines=2,
                    font_size=font_size
                )
            continue
        if field == "Vertragsp. Str + Hnr" and not is_empty(value):
            kombination = row.get("Vertragsp. Str + Hnr")
            street, house_number = split_strasse_hausnummer(kombination)

            c.setFont("Helvetica", font_size)
            if street:
                draw_text_in_box(
                    c=c,
                    text=street,
                    x=38 * mm,
                    y_base=62.5 * mm,
                    box_width=50*mm,
                    max_lines=2,
                    font_size=font_size
                )
            if house_number:
                draw_text_in_box(
                    c=c,
                    text=house_number,
                    x=94 * mm,
                    y_base=62.5 * mm,
                    box_width=20*mm,
                    max_lines=2,
                    font_size=font_size
                )
            continue
        if field == "Vertragsp. Str + Hnr" and is_empty(value):
            kombination = row.get("Objekt Str + Hnr")
            street, house_number = split_strasse_hausnummer_lexico(kombination)

            c.setFont("Helvetica", font_size)
            if street:
                draw_text_in_box(
                    c=c,
                    text=street,
                    x=38 * mm,
                    y_base=62.5 * mm,
                    box_width=50*mm,
                    max_lines=2,
                    font_size=font_size
                )
            if house_number:
                draw_text_in_box(
                    c=c,
                    text=house_number,
                    x=93 * mm,
                    y_base=62.5 * mm,
                    box_width=12*mm,
                    max_lines=2,
                    font_size=font_size
                )
            continue
        # Ort:
        if field == "Objekt Ort":
            draw_text_in_box(
                c=c,
                text=value,
                x=x,
                y_base=y,
                box_width=box_width,
                max_lines=2,
                font_size=font_size
            )
            continue

        # PLZ:
        if field == "Objekt PLZ":
            draw_text_in_box(
                c=c,
                text=str(value) if value is not None else "",
                x=x,
                y_base=y,
                box_width=box_width,
                max_lines=2,
                font_size=font_size
            )
            continue

        # Sonderlogik Anzahl WE (IMMER schreiben)
        if field == "Anzahl WE":
            total = parse_anzahl_we(value)
            if total is not None:
                c.setFont("Helvetica", font_size)
                c.drawString(x, y, str(total))
            continue

        if field == "Datum":
            heute = date.today()

            if heute.day < 20:
                monat = heute.month + 1
                jahr = heute.year
            else:
                monat = heute.month + 2
                jahr = heute.year

            if monat > 12:
                monat -= 12
                jahr += 1

            draw_text_in_box(
                c=c,
                text=f"01.{monat:02d}.{jahr}",
                x=x,
                y_base=y,
                box_width=box_width,
                max_lines=2,
                font_size=font_size
            )
            continue

        # Sonderlogik (Bei nicht-Eingaben):
        if is_empty(value) and field == "Vertragsp. Firma" and is_empty(row.get("Vertragsp. Name")):
            draw_text_in_box(
                c=c,
                text= f"WEG {shorten_streets(row.get("Objekt Str + Hnr"))}, {str(row.get("Objekt PLZ"))} {row.get("Objekt Ort")}",
                x=x,
                y_base=y,
                box_width= 70*mm,
                max_lines=2,
                font_size=font_size
            )
            continue
        if is_empty(value) and field == "Vertragsp. PLZ":
            draw_text_in_box(
                c=c,
                text=str(row.get("Objekt PLZ") or ""),
                x=x,
                y_base=y,
                box_width=70*mm,
                max_lines=2,
                font_size=font_size
            )
            continue
        if is_empty(value) and field == "Vertragsp. Ort":
            draw_text_in_box(
                c=c,
                text= f"{row.get("Objekt Ort")}",
                x=x,
                y_base=y,
                box_width= 70*mm,
                max_lines=2,
                font_size=font_size
            )
            continue

        # Allgemeine felder:
        if not is_empty(value):
            draw_text_in_box(
                c=c,
                text=str(value),
                x=x,
                y_base=y,
                box_width=box_width,
                max_lines=2,
                font_size=font_size
            )
        
        
    c.save()

    base = PdfReader(VV_TEMPLATE)
    overlay = PdfReader(overlay_path)

    writer = PdfWriter()
    page = base.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
