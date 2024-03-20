import os
import json
import shutil

def read_curse_api_key() -> str:
    with open("resources/curse_api_key.txt", "r") as file: # get our curse api key from its file
        curse_api_key = file.read()
        if curse_api_key is None: print("No Curseforge API key found!"); exit()
        else: return curse_api_key

def read_manifest() -> list:
    try:
        with open('resources/Staging Folder/manifest.json') as file: # open up existing manifest
            return json.load(file)
    except Exception:
        exit("Trying to read from a manifest file that does not exist")

def export_json(manifest):
    with open('resources/Staging Folder/manifest.json', 'w') as file: # save our manifest to manifest.json
        json.dump(manifest, file, indent = 4)

def zip_manifest_file(name:str) -> None:
    if os.path.exists(f"resources/{name}.zip"):
        os.remove("resources/{name}.zip")
    
    shutil.make_archive(f"resources/{name}", 'zip', 'resources/Staging Folder')