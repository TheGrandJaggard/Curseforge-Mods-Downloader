import json
from typing import List
import requests
import gspread
import zipfile


def create_manifest(hyperlinks:List[str], lookup_modloader_version:bool, add_to_existing_manifest:bool):
    if add_to_existing_manifest:
        with open('output-manifest.json') as file: # open up existing manifest
            manifest = json.load(file)
    else:
        with open('manifest-template.json') as file: # open up our manifest template
            manifest = json.load(file)

    with open("curse_api_key.txt", "r") as file: # get our curse api key from its file
        curse_api_key = file.read()

    minecraft_version = manifest['minecraft']['version'] # grab the version of minecraft that we are using from the manifest template
    if lookup_modloader_version:
        modloader_version = get_modloader_version(curse_api_key, minecraft_version) # get the correct version of forge for our minecraft version
    
    problem_mods:List[dict] = []
    json_mods:List[dict] = manifest['files']
    for hyperlink in hyperlinks: # for every hyperlink we extract the data we need
        (json_mods, problem_mods) = get_mod_data(hyperlink, curse_api_key, minecraft_version, json_mods, problem_mods)
        
    manifest['files'] = json_mods # here we put the mod data into our manifest template
    if lookup_modloader_version:
        manifest['minecraft']['modLoaders'] = [{'id': modloader_version, 'primary': True}]

    if problem_mods: # if there are any mods that threw errors, list them
        print("\nThere are problems with the following mods:")
        for problem_mod in problem_mods:
            print("   ", problem_mod['slug'].capitalize())

    with open('output-manifest.json', 'w') as o: # save our manifest to manifest.json
        json.dump(manifest, o, indent = 4)

def get_mod_data(hyperlink:str, curse_api_key:str, minecraft_version:str, json_mods:List[dict], problem_mods:List[dict]):
    mod_slug = get_slug(hyperlink)
    if any(json_mod['slug'] == mod_slug for json_mod in json_mods):
        print("   ", mod_slug.capitalize(), "has already been added")
        return (json_mods, problem_mods)

    mod_id = get_mod_id(mod_slug, curse_api_key)
    (file_id, mod_dependencies) = get_file_id(mod_id, minecraft_version, curse_api_key)
    
    mod = {}
    mod['slug'] = mod_slug
    mod['projectID'] = mod_id
    mod['fileID'] = file_id
    mod['required'] = True
    
    if file_id == None:
        problem_mods.append(mod)
    else:
        json_mods.append(mod)
        for mod_dependency in mod_dependencies:
            if mod_dependency['relationType'] == 3:
                (json_mods, problem_mods) = get_mod_data(get_mod_URL(mod_dependency['modId'], curse_api_key), curse_api_key, minecraft_version, json_mods, problem_mods)
    
    return (json_mods, problem_mods)

def get_modloader_version(curse_api_key, minecraft_version):
    curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}
    for version in requests.get('https://api.curseforge.com/v1/minecraft/modloader', headers = curseforge_header).json()['data']:
        if version['gameVersion'] == minecraft_version and version['recommended'] == True:
            modloader_version = version['name']
            print(modloader_version)
    return modloader_version

def get_mod_URL(mod_id:int, curse_api_key:str):
    try:
        url = (f'https://api.curseforge.com/v1/mods/{mod_id}')
        params = {}
        curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}

        response = requests.get(url, params = params, headers = curseforge_header).json()['data']
        return response['slug']
    except Exception as e:
        print(f'    Could not find slug for "{mod_id}".')
        return None

def get_mod_id(slug:str, curse_api_key:str) -> int | None:
    url = 'https://api.curseforge.com/v1/mods/search'
    params = {'gameId': '432', 'slug': slug, 'classId': '6'}
    curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}
    try:
        response = requests.get(url, params, headers = curseforge_header).json()['data']
        mod_id = int(response[0]['id'])
        print("    Mod id:", mod_id)
        return mod_id
    except Exception as e:
        print(f'    Could not fetch CurseForge ID for "{slug}": {repr(e)}')
        return None

def get_file_id(mod_id:int, minecraft_version:str, curse_api_key:str) -> int | None:
    try:
        url = (f'https://api.curseforge.com/v1/mods/{mod_id}/files')
        params = {'gameVersion': str(minecraft_version), 'modLoaderType': 1}
        curseforge_header = {'Accept': 'application/json', 'x-api-key': curse_api_key}

        response = requests.get(url, params = params, headers = curseforge_header).json()['data']
        desired_mod_version_file = list(file for file in response if minecraft_version in file['gameVersions'])[0]
        file_id = int(desired_mod_version_file['id'])
        dependencies = desired_mod_version_file['dependencies']
        print("    File id:", file_id)
        return (file_id, dependencies)
    except Exception as e:
        print(f'    Could not find "{mod_id}" for forge {minecraft_version}. https://www.curseforge.com/minecraft/mc-mods/{mod_id}')
        return (None, None)

def get_slug(hyperlink:str) -> str:
    slug = hyperlink.split("/")[-1]
    print("Slug:", slug.capitalize())
    return slug

def get_hyperlinks_from_gspread(workbook_name:str, sheet_name:str):
    print("Fetching mod URLs from:", workbook_name + ",", sheet_name)
    gs = gspread.service_account()
    wb = gs.open(workbook_name)
    sh = wb.worksheet(sheet_name)
    hyperlinks = list(filter(None, sh.col_values(6)))
    hyperlinks.remove("Hyperlinks")
    
    return hyperlinks

def zip_manifest_file():
    # Open a zip file at the given filepath. If it doesn't exist, create one.
    # If the directory does not exist, it fails with FileNotFoundError
    with zipfile.ZipFile('Output modpack.zip', 'a') as zipf:
        # Add a file located at the source_path to the destination within the zip
        # file. It will overwrite existing files if the names collide, but it
        # will give a warning
        source_path = 'output-manifest.json'
        destination = 'manifest.json'
        zipf.write(source_path, destination)

if __name__ == "__main__":
    lookup_modloader_version = False
    add_to_existing_manifest = True

    hyperlink_list = get_hyperlinks_from_gspread("Minecraft modpack lists", "Realisticraft (2023-4)")

    create_manifest(hyperlink_list, lookup_modloader_version, add_to_existing_manifest)

    zip_manifest_file()