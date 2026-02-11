from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from PyPDF2 import PdfReader, PdfWriter

router = APIRouter()

# Pfad zu deinem Template-Ordner (relativ zur main.py oder absolut)
TEMPLATE_DIR = "app/templates" 

@router.post("/admin/upload-pdf")
async def upload_admin_pdf(pdf: UploadFile = File(...)):
    if not pdf.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Datei muss eine PDF sein")

    try:
        # 1. Die hochgeladene Datei temporär lesen
        reader = PdfReader(pdf.file)
        
        if len(reader.pages) < 2:
            raise HTTPException(status_code=400, detail="Das PDF muss mindestens 2 Seiten haben")

        # 2. Seite 1 extrahieren (Index 0)
        writer1 = PdfWriter()
        writer1.add_page(reader.pages[0])
        path1 = os.path.join(TEMPLATE_DIR, "VV_Vorlage.pdf")
        with open(path1, "wb") as f:
            writer1.write(f)

        # 3. Seite 2 extrahieren (Index 1)
        writer2 = PdfWriter()
        writer2.add_page(reader.pages[1])
        path2 = os.path.join(TEMPLATE_DIR, "VV_2_Vorlage.pdf")
        with open(path2, "wb") as f:
            writer2.write(f)

        return {"message": "PDF erfolgreich gesplittet und Vorlagen aktualisiert"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))