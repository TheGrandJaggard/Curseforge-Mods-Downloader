import file_lib as fl
import googlesheets_lib as gs
import curseforge_lib as cf

# Google Sheet Settings
GWORKBOOK_NAME = 'Minecraft Modpack Lists'
SHEET_NAME = 'Create Magic 4 (2023&24)'
# Manifest Settings
MINECRAFT_VERSION = '1.18.2'
FORGE_VERSION = '40.2.14' # https://files.minecraftforge.net
MODPACK_NAME = 'Create & Magic 4'
MODPACK_VERSION = '1.4.0'
MODPACK_AUTHOR = 'Jaggard'
# MODE options: 'EDIT', 'NEW'
MODE = 'EDIT'

def create_manifest(gsheet_mod_slugs:list[str]):
    manifest = load_manifest()
    
    json_mods:list[dict] = manifest['files'].copy()
    json_slugs:list[str] = list(json_mod['slug'] for json_mod in json_mods)
    print("json slugs:", "\n".join(json_mods))

    for gsheet_slug in gsheet_mod_slugs:
        json_mods.extend(get_mod_data(gsheet_slug, json_slugs))
    

    print("\nChanges:")
    for gsheet_slug in gsheet_mod_slugs:
        if gsheet_slug not in list(mod['slug'] for mod in manifest['files']):
            print(f"  Added {gsheet_slug}")
    
    for mod in json_mods.copy():
        if 'problem' in mod:
            print(f"  Problem with {mod['slug']}, id : {mod['projectID']}")
            json_mods.remove(mod)
    
    for mod in json_mods.copy():
        if (mod['slug'] not in gsheet_mod_slugs) and (not is_depended_on(mod, json_mods)):
            print(f"  Removed {mod['slug']}")
            json_mods.remove(mod)

    manifest['files'] = json_mods # here we put the mod data into our manifest
    fl.export_json(manifest)

def load_manifest():
    manifest = (dict() if (MODE == 'NEW') else fl.read_manifest())

    manifest['minecraft'] = dict()
    manifest['minecraft']['version'] = MINECRAFT_VERSION
    manifest['minecraft']['modLoaders'] = [{'id': f'forge-{FORGE_VERSION}', 'primary': True}]
    manifest['manifestType'] = 'minecraftModpack'
    manifest['manifestVersion'] = 1
    manifest['name'] = MODPACK_NAME
    manifest['version'] = MODPACK_VERSION
    manifest['author'] = MODPACK_AUTHOR
    manifest['overrides'] = 'overrides'
    manifest['files'] = list()
    return manifest

def is_depended_on(mod_to_check:dict, json_mods:list[dict]) -> bool:
    for json_mod in json_mods:
        if 'dependencies' in json_mod.keys():
            for dependency in json_mod['dependencies']:
                if mod_to_check['projectID'] == dependency: return True
    return False

def get_mod_data(mod_slug_or_id:str|int, json_slugs:list[str]) -> list[dict]:
    '''Returns list of added mods'''

    if isinstance(mod_slug_or_id, int):
        mod_slug = f"{mod_slug_or_id}"
        mod_id = mod_slug_or_id
    else:
        mod_slug = mod_slug_or_id
        mod_id = 0

    if  mod_slug in json_slugs: # if this mod is already on our list
        return # make no changes
    print("        CHANGES BEING MADE")    
    
    if mod_id == 0: mod_id = cf.get_mod_id(mod_slug)

    (file_id, file_dependencies) = cf.get_file_id(mod_id, MINECRAFT_VERSION)
    if file_dependencies:
        file_dependencies = list(dependency for dependency in file_dependencies if dependency['relationType'] == 3)
    
    mod = {
        'slug': mod_slug,
        'projectID': mod_id,
        'fileID': file_id,
        'required': True,
    }
    if file_dependencies:
        mod['dependencies'] = list(mod_dependency['modId'] for mod_dependency in file_dependencies)
    
    if file_id == None:
        mod['problem'] = True
        return [mod]
    
    added_mods_list = [mod]
    json_slugs.append(mod_slug)
    for mod_dependency in file_dependencies: # if there is a dependency then get its info and add it to the mod list
        added_mods_list.extend(get_mod_data(mod_dependency['modId'], json_slugs))
    
    return added_mods_list

if __name__ == '__main__':
    sheet = gs.sheet(GWORKBOOK_NAME, SHEET_NAME)
    mod_slugs = sheet.get_mod_slugs()

    create_manifest(mod_slugs)

    output_path = fl.zip_manifest_file(MODPACK_NAME)

    print(f"Modpack output to: '{output_path}'")
    