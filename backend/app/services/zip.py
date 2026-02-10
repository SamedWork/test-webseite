import zipfile
import os

def zip_files(files: list[str], workdir: str) -> str:
    zip_path = f"{workdir}/result.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in files:
            zipf.write(f, os.path.basename(f))

    return zip_path
