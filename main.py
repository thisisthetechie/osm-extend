''' Main Function. '''
from variables import *
from osm_functions import OSM
from activity_functions import (
    tally_completed_knots,
    tally_challenge_badge_completion,
    update_required_chief_scout_badge_count
)

'''
Configure Functions to run against your OSM Instance, and in what order.
'''
def main():
    for section, badge_count in SECTIONS.items():
        tally_completed_knots(OSM(section), BEAVERS_REQUIRED_KNOTS)
        tally_challenge_badge_completion(OSM(section))
        update_required_chief_scout_badge_count(OSM(section), badge_count)

if __name__=="__main__": 
    main() 