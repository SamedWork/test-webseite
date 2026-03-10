import zipfile
import os

def zip_files(files: list[str], workdir: str) -> str:
    zip_path = os.path.join(workdir, "Versorgungsvereinbarungen.zip")
    
    with zipfile.ZipFile(zip_path, "w") as zipf:
        used_names = {} # Speichert, wie oft ein Name schon vorkam

        for f in files:
            base_name = os.path.basename(f)
            name, ext = os.path.splitext(base_name)
            
            # Prüfen, ob der Name schon existiert
            if base_name in used_names:
                used_names[base_name] += 1
                # Neuen Namen generieren: "Name_1.pdf"
                new_name = f"{name}_{used_names[base_name]}{ext}"
            else:
                used_names[base_name] = 0
                new_name = base_name

            zipf.write(f, new_name)

    return zip_path
