from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation

# ─────────────────────────────
# Pfade korrekt auflösen
# ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parent        # backend/app
TEMPLATE_DIR = BASE_DIR / "templates"

INPUT = TEMPLATE_DIR / "OL_Vorlage.pdf"
OUTPUT = TEMPLATE_DIR / "OL_Vorlage_normalized.pdf"

if not INPUT.exists():
    raise FileNotFoundError(f"Nicht gefunden: {INPUT}")

# ─────────────────────────────
# PDF normalisieren (Rotation entfernen)
# ─────────────────────────────
reader = PdfReader(str(INPUT))
writer = PdfWriter()

for page in reader.pages:
    rotation = page.get("/Rotate") or 0

    if rotation != 0:
        page.add_transformation(Transformation().rotate(-rotation))
        page.rotate = 0

    writer.add_page(page)

with open(OUTPUT, "wb") as f:
    writer.write(f)

print("✅ OL_Vorlage normalisiert:")
print("   ", OUTPUT)
