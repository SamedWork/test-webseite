from pypdf import PdfReader, PdfWriter

def merge_pdfs(pdfs: list[str], output: str) -> str:
    writer = PdfWriter()

    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)

    with open(output, "wb") as f:
        writer.write(f)

    return output
