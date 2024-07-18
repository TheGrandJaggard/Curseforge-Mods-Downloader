import file_lib as fl
import googlesheets_lib as gs
import curseforge_lib as cf

def create_manifest(gsheet_mod_slugs:list[str], settings:fl.Settings):
    manifest = load_manifest(settings)
    original_slugs = list(manifest_mod['slug'] for manifest_mod in manifest['files'])
    
    json_mods:list[dict] = manifest['files'].copy() # this will get updated to contain all added mods
    json_slugs:list[str] = list(json_mod['slug'] for json_mod in json_mods) # this will too, through mutilation
    json_ids:list[str] = list(json_mod['projectID'] for json_mod in json_mods) # this will too, through mutilation

    for gsheet_slug in gsheet_mod_slugs:
        if gsheet_slug in settings.slug_blacklist: continue
        json_mods.extend(get_mod_data(gsheet_slug, json_slugs, json_ids, settings))
    
    for file in settings.manual_files:
        if file['projectID'] not in json_ids:
            json_mods.append({
            'slug': file['hyperlink'].split('/')[-1],
            'projectID': file['projectID'],
            'fileID': file['fileID'],
            'required': True
        })
    
    print("\nChanges:")
    for mod in json_mods.copy():
        if 'problem' in mod:
            print(f"  Problem with {mod['slug']}, id : {mod['projectID']}")
            json_mods.remove(mod)
            original_slugs.append(mod['slug']) # to remove 'Added' message for this mod
    
    for gsheet_slug in gsheet_mod_slugs:
        if gsheet_slug not in original_slugs and gsheet_slug not in settings.slug_blacklist:
            print(f"  Added {gsheet_slug}")

    for mod in json_mods.copy():
        if ((mod['slug'] not in gsheet_mod_slugs)
            and (mod['slug'] not in (file['hyperlink'].split('/')[-1] for file in settings.manual_files))
            and (not is_depended_on(mod, json_mods))):

            print(f"  Removed {mod['slug']}")
            json_mods.remove(mod)

    manifest['files'] = json_mods # here we put the mod data into our manifest
    fl.export_json(manifest)

def load_manifest(settings:fl.Settings):
    manifest = (dict() if (settings.mode == 'NEW') else fl.read_manifest())

    manifest['minecraft'] = dict()
    manifest['minecraft']['version'] = settings.minecraft_version
    manifest['minecraft']['modLoaders'] = [{'id': f'forge-{settings.forge_version}', 'primary': True}]
    manifest['manifestType'] = 'minecraftModpack'
    manifest['manifestVersion'] = 1
    manifest['name'] = settings.modpack_name
    manifest['version'] = settings.modpack_version
    manifest['author'] = settings.modpack_author
    manifest['overrides'] = 'overrides'
    if 'files' not in manifest: manifest['files'] = list()
    return manifest

def is_depended_on(mod_to_check:dict, json_mods:list[dict]) -> bool:
    for json_mod in json_mods:
        if 'dependencies' in json_mod.keys():
            for dependency in json_mod['dependencies']:
                if mod_to_check['projectID'] == dependency: return True
    return False

def get_mod_data(mod_slug_or_id:str|int, json_slugs:list[str], json_ids:list[int], settings:fl.Settings) -> list[dict]:
    '''Returns list of added mods'''

    if isinstance(mod_slug_or_id, int):
        mod_slug = f"{mod_slug_or_id}"
        mod_id = mod_slug_or_id
    else:
        mod_slug = mod_slug_or_id
        mod_id = 0

    if mod_slug in json_slugs: print(f"Slugs already contains {mod_slug}");return [] # if this mod is already on our slug list make no changes
    if mod_id == 0: mod_id = cf.get_mod_id(mod_slug, settings.curse_api_key)
    if mod_id in json_ids: print(f"J ids already contains {mod_id}");return[] # if this mod is already on our id list make no changes
    else: print(f"Adding {mod_slug}")
    
    (file_id, file_dependencies) = cf.get_file_id(mod_id, settings.minecraft_version, settings.curse_api_key)
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
    json_ids.append(mod_id)
    for mod_dependency in file_dependencies: # if there is a dependency then get its info and add it to the mod list
        added_mods_list.extend(get_mod_data(mod_dependency['modId'], json_slugs, json_ids, settings))
    
    return added_mods_list

if __name__ == '__main__':
    settings = fl.Settings('resources/settings.json')
    sheet = gs.sheet(settings.gworkbook_name, settings.sheet_name)
    mod_slugs = sheet.get_mod_slugs()

    create_manifest(mod_slugs, settings)

    for non_mod_hyperlink in sheet.get_non_mod_hyperlinks():
        if non_mod_hyperlink in (file['hyperlink'] for file in settings.manual_files): continue
        print(f"  {non_mod_hyperlink} must be added manually")
    output_path = fl.zip_manifest_file(settings.modpack_name)

    print(f"Modpack output to: '{output_path}'")
    