import gspread

class sheet():
    def __init__(self, workbook_name:str, sheet_name:str):
        print(f"Getting sheet '{sheet_name}' from '{workbook_name}'")
        self.workbook_name = workbook_name
        self.sheet_name = sheet_name
        self.service = gspread.service_account()
        self.workbook = self.service.open(self.workbook_name)
        self.sheet = self.workbook.worksheet(sheet_name)
        self.headers = self.sheet.row_values(1)

    def get_all_hyperlinks(self) -> list[str]:
        hyperlinks = list(self.sheet.col_values(self.headers.index('URL')+1))
        hyperlinks.remove(hyperlinks[0]) # remove header column
        hyperlinks = filter(None, hyperlinks) # filter out blank values
        
        return hyperlinks
    
    def get_mod_hyperlinks(self) -> list[str]:
        hyperlinks = self.get_all_hyperlinks()
        hyperlinks = list(h for h in hyperlinks if h.split('/')[-2] == 'mc-mods')
        
        return hyperlinks
    
    def get_non_mod_hyperlinks(self) -> list[str]:
        hyperlinks = self.get_all_hyperlinks()
        hyperlinks = list(h for h in hyperlinks if h.split('/')[-2] != 'mc-mods')
        
        return hyperlinks
    
    def get_mod_slugs(self) -> list[str]:
        hyperlinks = self.get_mod_hyperlinks()
        slugs = list(hyperlink.split('/')[-1] for hyperlink in hyperlinks)

        return slugs
    
    def get_non_mod_slugs(self) -> list[str]:
        hyperlinks = self.get_non_mod_hyperlinks()
        slugs = list(hyperlink.split('/')[-1] for hyperlink in hyperlinks)

        return slugs

if __name__ == '__main__':
    slug_list = sheet('Minecraft Modpack Lists', 'Realisticraft (2023-4)').get_mod_slugs()
    print("\n".join(slug_list))
    