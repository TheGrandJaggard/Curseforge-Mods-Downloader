import json
from typing import List
import requests

def create_manifest(hyperlink_list:List[str]):
    with open('manifest-template.json') as m:
        manifest = json.load(m)

    with open("curse_api_key.txt", "r") as file:
        curse_api_key = file.read()

    minecraft_version = manifest['minecraft']['version']

    curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}
    for version in requests.get('https://api.curseforge.com/v1/minecraft/modloader', headers = curseforge_header).json()['data']:
        if version['gameVersion'] == minecraft_version and version['recommended'] == True:
            modloader_version = version['name']
            print(modloader_version)
    
    mods = { 'files': [] }
    for hyperlink in hyperlink_list:
        mod_id = get_mod_id(hyperlink, curse_api_key)
        file_id = get_file_id(mod_id, minecraft_version, curse_api_key)

        mod = {}
        mod['projectID'] = mod_id
        mod['fileID'] = file_id
        mod['required'] = True

        mods['files'].append(mod)
    
    manifest['files'] = mods['files']
    manifest['minecraft']['modLoaders'] = [{'id': modloader_version, 'primary': True}]

    with open('manifest.json', 'w') as o:
        json.dump(manifest, o, indent=4)

def get_mod_id(hyperlink:str, curse_api_key:str) -> int | None:
    url = 'https://api.curseforge.com/v1/mods/search'
    params = {'gameId': '432', 'slug': parse_slug(hyperlink), 'classId': '6'}
    curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}
    try:
        response = requests.get(url, params, headers = curseforge_header).json()['data']
        mod_id = int(response[0]['id'])
        print("mod id:", mod_id)
        return mod_id
    except Exception as e:
        print(f'Could not fetch CurseForge ID for "{parse_slug(hyperlink)}": {repr(e)}')
        return None

def get_file_id(mod_id:int, minecraft_version:str, curse_api_key:str) -> int | None:
    try:
        url = (f'https://api.curseforge.com/v1/mods/{mod_id}/files')
        params = {'gameVersion': str(minecraft_version), 'modLoaderType': 1}
        curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}

        response = requests.get(url, params = params, headers = curseforge_header).json()['data']
        desired_mod_version_file = list(file for file in response if minecraft_version in file['gameVersions'])[0]
        file_id = int(desired_mod_version_file['id'])
        print("file id:", file_id)
        return file_id
    except Exception as e:
        print(f'Could not find "{mod_id}" for forge {minecraft_version}. https://www.curseforge.com/minecraft/mc-mods/{mod_id}')
        return None
    
def parse_slug(hyperlink:str) -> str:
    sections = hyperlink.split("/")
    return sections[-1]

if __name__ == "__main__":
    hyperlink_list = ["https://www.curseforge.com/minecraft/mc-mods/bucketlib",
        "https://www.curseforge.com/minecraft/mc-mods/quark"]
    create_manifest(hyperlink_list)