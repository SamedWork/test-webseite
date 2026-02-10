from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from pathlib import Path
from reportlab.pdfbase.pdfmetrics import stringWidth

# services → app → template
BASE_DIR = Path(__file__).resolve().parents[1]   # backend/app
OL_TEMPLATE = BASE_DIR / "templates" / "OL_Vorlage_normalized.pdf"

if not OL_TEMPLATE.exists():
    raise FileNotFoundError(f"OL Template fehlt: {OL_TEMPLATE}")


def sum_vertrags_we(we_list: list[int]) -> int:
    return sum(we_list)

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

    for size in range(font_size, min_font_size - 1, -1):
        c.setFont(font, size)
        words = text.split(" ")
        lines = []
        current = ""

        for word in words:
            candidate = (current + " " + word).strip()
            if stringWidth(candidate, font, size) <= box_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

                # Wort ist breiter als Box → zeichenweise
                if stringWidth(current, font, size) > box_width:
                    parts = break_word_chars(current, size)
                    lines.extend(parts[:-1])
                    current = parts[-1]

        if current:
            lines.append(current)

        # Text darf NUR akzeptiert werden, wenn ALLES reinpasst
        if (
            len(lines) <= max_lines
            and all(stringWidth(line, font, size) <= box_width for line in lines)
        ):
            final_lines = lines
            final_size = size
            break
    else:
        # selbst min_font_size reicht nicht
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

def create_ol_pdf(
    objects: list[str],
    plz: str,
    ort: str,
    we_list: list[int],
    we_sum: int,
    index: int,
    workdir: str,
    start_lfd: int = 0
) -> str:

    overlay_path = f"{workdir}/ol_overlay_{index}.pdf"
    output_path = f"{workdir}/ol_filled_{index}.pdf"

    # Seitengröße aus Vorlage lesen
    base = PdfReader(str(OL_TEMPLATE))
    base_page = base.pages[0]

    page_width = float(base_page.mediabox.width)
    page_height = float(base_page.mediabox.height)

    # Overlay exakt gleich groß erzeugen
    c = canvas.Canvas(
        overlay_path,
        pagesize=(page_width, page_height)
    )

    # Tabellenlayout (deine Werte)
    start_y = 117 * mm
    row_height = 6.5 * mm

    
    y = start_y

    for i, address in enumerate(objects):
        lfd_nr = start_lfd + i + 1

        c.setFont("Helvetica", 8)

        we_value = we_list[i] if i < len(we_list) else 0

        col_x = {
            "lfd": 9.5 * mm if lfd_nr < 10 else 8.5 * mm,
            "str": 15 * mm,
            "plz": 68 * mm,
            "ort": 82 * mm,
            "we": (
                186.8 * mm if we_value < 10
                else 186.3 * mm if we_value < 100
                else 185.7 * mm
            ),
        }

        draw_text_in_box(
            c=c,
            text=str(lfd_nr),
            x=col_x["lfd"],
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )
        draw_text_in_box(
            c=c,
            text=address,
            x=col_x["str"],
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )
        draw_text_in_box(
            c=c,
            text=str(plz),
            x=col_x["plz"],
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )
        draw_text_in_box(
            c=c,
            text=str(ort),
            x=col_x["ort"],
            y_base=y,
            box_width=21 * mm,
            max_lines=2,
            font_size=8
        )
        draw_text_in_box(
            c=c,
            text=str(we_value),
            x=col_x["we"],
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )

        # GE:
        draw_text_in_box(
            c=c,
            text="0",
            x=198 * mm,
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )

        # Preise:
        draw_text_in_box(
            c=c,
            text="0.00 €",
            x=228 * mm,
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )
        draw_text_in_box(
            c=c,
            text="0.00 €",
            x=253 * mm,
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )
        draw_text_in_box(
            c=c,
            text="0.00 €",
            x=276 * mm,
            y_base=y,
            box_width=45 * mm,
            max_lines=2,
            font_size=8
        )

        y -= row_height

        if y < 25 * mm:
            c.showPage()
            y = start_y

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(
        page_width - 19 * mm,
        page_height - 53.5 * mm,
        str(we_sum)
    )

    c.save()

    # Overlay AUF Vorlage mergen
    overlay = PdfReader(overlay_path)
    writer = PdfWriter()

    for base_page in base.pages:
        page = base_page
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
