from cursepy import CurseClient

with open("curse_api_key.txt", "r") as file:
    curse_api_key = file.read

client = CurseClient(curse_api_key)

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

print(client.GAME)
print(client.GAME)