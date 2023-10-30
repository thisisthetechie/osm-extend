''' Main Function. '''
from osm import (
    OSM, 
    generate_spreadsheet,
    tally_completed_knots, 
    tally_challenge_badge_completion, 
    update_required_chief_scout_badge_count
)

'''
Configure Functions to run against your OSM Instance, and in what order.
'''
def main():
    #section = OSM('cubs')
    #print(section.group)
    update_required_chief_scout_badge_count(OSM('beavers'))
    # for badge_type in ["challenge"]:
    #     generate_spreadsheet(badge_type = badge_type, section = section)

    # for section, badge_count in SECTIONS.items():
    #     tally_completed_knots(OSM(section), BEAVERS_REQUIRED_KNOTS)
    #     tally_challenge_badge_completion(OSM(section))
    #     update_required_chief_scout_badge_count(OSM(section), badge_count)

if __name__=="__main__": 
    main() 
    #section = OSM('beavers')
    #section.start(port=int('3000'))