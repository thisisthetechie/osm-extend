'''
#######################################
Tally Completed Knots (Beavers only)

Inputs:
   * OSM Object
   * Number of knots required to fulfil the Outdoors 'Knots' requirement

Description:
   Reads a Flexi Record called 'Knots'.
   If the total column is greater than or equal to the requirement for the Outdoors 'Knots' 
   then update the Outdoors badge record.
   If the Beaver Scout has demonstrated they can tie a shoelace, update the Skills 'Shoelace' 
   badge record.
#######################################
'''

from .config import *

def tally_completed_knots(section, knots_required):
    if section.name == 'beavers':
        badges_flexi = section.get_badges_flexi('Knots')
        badge_flexi_records = section.get_flexi_record_by_name('Knots')['items']

        badge_collection = {
            'challenge':section.get_badge_structure_by_type(BADGE_NAME['challenge']),
            'activity': section.get_badge_structure_by_type(BADGE_NAME['activity'])
        }
        badges = {
            'Outdoors': section.get_badge_record_by_identifier(section.badges['challenge']['Outdoors']['identifier']),
            'Skills': section.get_badge_record_by_identifier(section.badges['challenge']['Skills']['identifier']),
            'Camp Craft': section.get_badge_record_by_identifier(section.badges['activity']['Camp Craft']['identifier'])
        }

        knot_collection = {
            'shoelace': {},
            'knots': {},
            'reef': {}
        }

        print("Starting update of Beavers Knots")
        for badge_type, badge_data in badge_collection.items():
            for badge_id, badge_ref in badge_data['details'].items():
                if badge_ref['name'] in badges:
                    for row in badge_data['structure'][badge_id][1]['rows']:
                        if row['name'] == 'Shoe laces':
                            knot_collection['shoelace'].update({'badge_id':badge_id})
                            knot_collection['shoelace'].update({'field':row['field']})
                        elif row['name'] == 'Knots':
                            knot_collection['knots'].update({'badge_id':badge_id})
                            knot_collection['knots'].update({'field':row['field']})
                        elif row['name'] == 'Reef knot':
                            knot_collection['reef'].update({'badge_id':badge_id})
                            knot_collection['reef'].update({'field':row['field']})

        for record in badge_flexi_records:

            # Check and update Outdoors Badge if knots learned is met
            if int(record['total']) >= knots_required:
                for item in badges['Outdoors']['items']:
                    if str(item['scoutid']) == record['scoutid']:
                        if (knot_collection['knots']['field'] not in item) or (item[knot_collection['knots']['field']][0] == 'x'):
                            data = {
                                "badge_id": knot_collection['knots']['badge_id'].split('_')[0],
                                "badge_version": knot_collection['knots']['badge_id'].split('_')[1],
                                "field": knot_collection['knots']['field'],
                                "value": "[YES]",
                                "section.id": section.section.id,
                                "scoutid": str(item['scoutid'])
                            }
                            print(section.scouts[str(item['scoutid'])],"has satisfied knot count requirements, updating...")
                            update = section.update_badge_record(data)

            for knot_name, knot_data in knot_collection.items():
                if (knot_name != 'knots') and (record[badges_flexi['knots'][knot_name]] != ''):
                    for badge_name, badge_data in badges.items():
                        for item in badge_data['items']:
                            if str(item['scoutid']) == record['scoutid']:
                                if (knot_data['field'] not in item) or (item[knot_data['field']][0] == 'x'):
                                    data = {
                                        "badge_id": knot_data['badge_id'].split('_')[0],
                                        "badge_version": knot_data['badge_id'].split('_')[1],
                                        "field": knot_data['field'],
                                        "value": "[YES]",
                                        "section.id": section.id,
                                        "scoutid": item['scoutid']
                                    }
                                    print(f"{section.scouts[str(item['scoutid'])]['full_name']} has demonstrated tying the {knot_name.title()} Knot, updating...")
                                    update = section.update_badge_record(data)
        print("Completed update of Beavers Knots")