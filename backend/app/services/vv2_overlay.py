from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
import os

from app.services.vv_overlay import draw_text_in_box 

VV2_TEMPLATE = "app/templates/VV_2_Vorlage.pdf"

# Beispiel-Mapping für Seite 2
FIELD_MAPPING_VV2 = {
    "Unterschrift Vorname Nachname": (133 * mm, 114 * mm, 7, 100 * mm),  # Beispielposition
    "Unterschrift Datum": (133 * mm, 118.5 * mm, 7, 50 * mm),  # Beispielposition
}

def create_vv2_pdf(row: dict, index: int, workdir: str) -> str:
    overlay_path = f"{workdir}/vv2_overlay_{index}.pdf"
    output_path = f"{workdir}/vv2_filled_{index}.pdf"

    c = canvas.Canvas(overlay_path)
    
    for field, (x, y, font_size, box_width) in FIELD_MAPPING_VV2.items():
        value = row.get(field)
        if value:
            draw_text_in_box(c, str(value), x, y, box_width, font_size=font_size)

    c.save()

    base = PdfReader(VV2_TEMPLATE)
    overlay = PdfReader(overlay_path)
    writer = PdfWriter()

    page = base.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path