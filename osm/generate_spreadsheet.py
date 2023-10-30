from openpyxl import Workbook
from string import ascii_uppercase as col

from .config import *

def generate_spreadsheet(badge_type, section):
    print(f"Generating {badge_type.title()} Badge Records for {section.name.title()}...")
    xl = Workbook()
    sheet = xl.active
    badge_structure = section.get_badge_structure_by_type(BADGE_NAME[badge_type])['structure']
    
    for key, value in section.badges[badge_type].items():
        print(f"\nCapturing {key} badge detail...")
        if sheet.title != 'Sheet':
            sheet = xl.create_sheet()
        sheet.title = key.title()
        xlrow = 1
        xlcol = 0
        sheet[f"{col[xlcol]}{xlrow}"] = 'Scout'
        for scoutid, scout in section.scouts.items():
            if 'badges' in scout:
                xlrow += 1
                sheet[f"{col[xlcol]}{xlrow}"] = f"{scout['full_name']}"
        badge_id = value['identifier']
        
        for row in badge_structure[badge_id][1]['rows']:
            xlrow = 1
            sheet[f"{col[xlcol]}{xlrow}"] = row['name']
            xlrow += 1
            badge_completion = section.get_badge_record(value['id'],value['version'])['items']

            for scout in badge_completion:
                if row['field'] in scout.keys():
                    sheet[f"{col[xlcol]}{xlrow}"] = scout[row['field']]
                xlrow += 1
        
    print(f"Creating {badge_type.title()}.xlsx file")
    xl.save(f"{badge_type.title()}.xlsx")