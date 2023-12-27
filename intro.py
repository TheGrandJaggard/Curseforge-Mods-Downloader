# Import the CurseClient:

from cursepy import CurseClient

# Create the CurseClient:

with open("curse_api_key.txt", "r") as file:
    curse_api_key = file.read

curse = CurseClient(curse_api_key)

ADDON_ID = 1234

# Get the addon info:

addon = curse.addon(1234)

# Print the name of the addon:

print(addon.name)