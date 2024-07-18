import os
import json
import shutil

class Settings():
    def __init__(self, path:str):
        with open(path, 'r') as file:
            json_file = json.load(file)
            self.curse_api_key = json_file['curse_api_key']
            self.gworkbook_name = json_file['gworkbook_name']
            self.sheet_name = json_file['sheet_name']
            self.slug_blacklist = json_file['slug_blacklist']
            self.minecraft_version = json_file['minecraft_version']
            self.forge_version = json_file['forge_version']
            self.modpack_name = json_file['modpack_name']
            self.modpack_version = json_file['modpack_version']
            self.modpack_author = json_file['modpack_author']
            self.manual_files = json_file['manual_files']
            self.mode = json_file['mode']

def read_manifest() -> list:
    try:
        with open('resources/staging_folder/manifest.json') as file: # open up existing manifest
            return json.load(file)
    except Exception:
        exit("Trying to read from a manifest file that does not exist")

def export_json(manifest) -> dict:
    with open('resources/staging_folder/manifest.json', 'w') as file: # save our manifest to manifest.json
        json.dump(manifest, file, indent = 4)

def zip_manifest_file(name:str) -> None:
    if os.path.exists(f"resources/{name}.zip"):
        os.remove(f"resources/{name}.zip")
    shutil.make_archive(f"resources/{name}", 'zip', 'resources/staging_folder')
    
    return os.path.abspath(f"resources/{name}.zip")

if __name__ == '__main__':
    print("Manifest:\n", read_manifest())
    