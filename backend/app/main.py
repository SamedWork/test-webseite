from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.api.upload import router as upload_router
from app.api import admin

app = FastAPI()

# Ersetze die lokalen URLs durch deine echte Frontend-URL
allow_origins = [
    "http://localhost:5173",
    "https://test-webseite.vercel.app" # Deine neue Vercel-URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Upload API
app.include_router(upload_router)
app.include_router(admin.router)

# Excel Template Download
@app.get("/template")
def download_template():
    return FileResponse(
        path="app/templates/Versorgungsvereinbarung Template.xlsx",
        filename="Versorgungsvereinbarung Template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# venv\Scripts\activate
# uvicorn app.main:app --reload
# Produktiv: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
# bash gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app