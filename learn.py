from cursepy import CurseClient

with open("curse_api_key.txt", "r") as file:
    curse_api_key = file.read

client = CurseClient(curse_api_key)

# CURSECLIENT BASICS

# [0]: LIST_GAMES - Gets a list of all valid games
# [1]: GAME - Get information on a specific game
# [2]: LIST_CATEGORY - Gets a list of all valid categories
# [3]: CATEGORY - Get information on a specific category
# [4]: SUB_CATEGORY - Get all sub-categories for the given category
# [5]: ADDON - Get information on a specific addon
# [6]: ADDON_SEARCH - Searches the game for addons
# [7]: ADDON_DESC - Get description for a specific addon
# [8]: ADDON_LIST_FILE - Gets a tuple of all files associated with an addon
# [9]: ADDON_FILE - Get information on a specific file for an addon
# [10]: FILE_DESCRIPTION - Description of a file
print(client.GAME)

# this is low level so we probably won't need to use it
# inst = client.handle(client.ADDON, 1234)

# To get info on a specific game, you can use the ‘game’ method:
# game = client.game(GAME_ID)
# To get a tuple of all valid games on CurseForge, you can use the ‘games’ method:
games = client.games()

# # First, you can get info on a specific addon using the ‘addon’ method:
# addon = client.addon(ADDON_ID)
# # However, this information is incomplete! Another call must be made to retrieve the addon description. You can use the ‘addon_description’ method for this:
# desc = client.addon_description(ADDON_ID)
# # You can also search for addons using the ‘search’ method:
# result = client.search(GAME_ID, search=search_param)
# # Users can optionally provide a search object to fine tune the search operation. You can get a search object using the ‘get_search’ method:
# search_param = client.get_search()

# # The ‘SearchParam’ objects contains the following values for fine-tuning the search operation:
#     # gameId - Game ID to search under
#     # rootCategoryId - Search by root category ID
#     # categoryId - Search by category ID
#     # gameVersion - Game version to search under
#     # searchFilter - Value to search for
#     # sortField - Filter results in a certain way (featured, popularity, total downloads, ect.), use constants for defining this!
#     # sortOrder - Order the of the results (ascending or descending), use constants for defining this!
#     # modLoaderType - Filter mods associated by modloader
#     # gameVersionTypeId - Only show results tagged with a certain game version
#     # slug - Filter by slug
#     # index - Page index to search under
#     # pageSize - Number of items to display per page
# # ‘slug’ allows you to sort items by their slug.
# # I might want to use slug, because that is in the url that I have

# # First things first, you can get a list of all files associated with an addon:
# files = client.addon_files(ADDON_ID, search)
# # To get info on a specific file, you can use the ‘addon_file’ method:
# file = client.addon_files(ADDON_ID, FILE_ID)
# # Like the addon methods documented earlier, this info is incomplete! You can get the file description like so:
# desc = client.file_description(ADDON_ID, FILE_ID)

# CURSE INSTANCE TUTORIAL
