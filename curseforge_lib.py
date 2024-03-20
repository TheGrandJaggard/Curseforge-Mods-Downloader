import requests

API_KEY = '$2a$10$4ndfysCyEi6FixpXato1AOOkikIL0ETgN5rkyYryKnjLJNcFNZLUW'

def get_forge_version(minecraft_version:str) -> str:
    url = 'https://api.curseforge.com/v1/minecraft/modloader'
    curseforge_headers = {'Accept': 'application/json', 'x-api-key': API_KEY}

    for version in requests.get(url, headers = curseforge_headers).json()['data']:
        if version['gameVersion'] == minecraft_version and version['recommended'] == True:
            return version['name']
        
    print(f"No forge version found for minecraft {minecraft_version}!"); exit()

def get_mod_URL(mod_id:int) -> str | None:
    try:
        url = (f'https://api.curseforge.com/v1/mods/{mod_id}')
        curseforge_headers = {'Accept': 'application/json', 'x-api-key': API_KEY}

        response = requests.get(url, headers = curseforge_headers).json()['data']
        return response['links']['websiteUrl']
    except Exception:
        # print("Could not find slug for:", mod_id)
        return None

def get_mod_id(slug:str) -> int | None:
    url = 'https://api.curseforge.com/v1/mods/search'
    params = {'gameId': '432', 'slug': slug, 'classId': '6'}
    curseforge_headers = {'Accept': 'application/json', 'x-api-key': API_KEY}
    try:
        response = requests.get(url, params = params, headers = curseforge_headers)
        response.raise_for_status()
        json_response = response.json()['data']
        return int(json_response[0]['id'])
    except Exception as e:
        # print(f'Could not fetch CurseForge ID for "{slug}": {repr(e)}')
        return None

def get_file_id(mod_id:int, minecraft_version:str) -> tuple[int, list] | tuple[None, None]:
    try:
        url = (f'https://api.curseforge.com/v1/mods/{mod_id}/files')
        params = {'gameVersion': str(minecraft_version), 'modLoaderType': 1}
        curseforge_headers = {'Accept': 'application/json', 'x-api-key': API_KEY}

        response = requests.get(url, params = params, headers = curseforge_headers).json()['data']
        desired_mod_version_file = list(file for file in response if (minecraft_version in file['gameVersions']))[0]
        file_id = int(desired_mod_version_file['id'])
        dependencies = list(dependency for dependency in desired_mod_version_file['dependencies'] if dependency['relationType'] == 3)
        return (file_id, dependencies)
    except Exception:
        # print(f'Could not find "{mod_id}" for forge {minecraft_version}')
        return (None, None)

if __name__ == '__main__':
    print(get_mod_URL(306612))