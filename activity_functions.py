''' Activity Functions. '''
from variables import *
from tabulate import tabulate

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
def tally_completed_knots(section, knots_required):
    if section.name == 'beavers':
        badges_flexi = section.get_badges_flexi('Knots')
        badge_flexi_records = section.get_flexi_record_by_name('Knots')['items']

        challenge_badges = section.get_badge_structure(1)
        badges = {
            'Outdoors': section.get_badge_record_by_identifier(section.badges['challenge']['Outdoors']['identifier']),
            'Skills': section.get_badge_record_by_identifier(section.badges['challenge']['Skills']['identifier'])
        }

        shoelace_field = None
        knots_field = None

        print("Starting update of Beavers Knots")
        for badge in badges:
            for row in challenge_badges['structure'][section.badges['challenge'][badge]['identifier']][1]['rows']:
                if row['name'] == 'Shoe laces':
                    shoelace_field = row['field']
                elif row['name'] == 'Knots':
                    knots_field = row['field']

        for record in badge_flexi_records:

            # Check and update Outdoors Badge if knots learned is met
            if int(record['total']) >= knots_required:
                for item in badges['Outdoors']['items']:
                    if str(item['scoutid']) == record['scoutid']:
                        if (knots_field not in item) or (item[knots_field][0] == 'x'):
                            data = {
                                "badge_id": section.badges['challenge']['Outdoors']['id'],
                                "badge_version": section.badges['challenge']['Outdoors']['version'],
                                "field": knots_field,
                                "value": "[YES]",
                                "section.id": section.section.id,
                                "scoutid": str(item['scoutid'])
                            }
                            print(section.scouts[str(item['scoutid'])],"has satisfied knot count requirements, updating...")
                            update = section.update_badge_record(data)

            # Check and update Skills Badge if the beaver can tie shoelace knot
            if record[badges_flexi['shoelace']] != '':
                for item in badges['Skills']['items']:
                    if str(item['scoutid']) == record['scoutid']:
                        if (shoelace_field not in item) or (item[shoelace_field][0] == 'x'):
                            data = {
                                "badge_id": section.badges['challenge']['Skills']['id'],
                                "badge_version": section.badges['challenge']['Skills']['version'],
                                "field": shoelace_field,
                                "value": "[YES]",
                                "section.id": section.section.id,
                                "scoutid": item['scoutid']
                            }
                            print(section.scouts[str(item['scoutid'])],"has satisfied demonstrated shoelace tying, updating...")
                            update = section.update_badge_record(data)
        print("Completed update of Beavers Knots")

'''
#######################################
Update Required Chief Scout Badge Count

Inputs:
   * OSM Object
   * Number of badges required

Description:
   Counts the number of Activity and Staged badges the Scout has earned.
   If the total is greater than or equal to the requirement for the Chief Scout Award
   then update the Chief Scout badge record.
#######################################
'''
def update_required_chief_scout_badge_count(section, badges_required):
    badge_count = [["Name","Activity","Staged","CS-Minimum"]]

    badge_flexi = section.get_badges_flexi(BADGE_FLEXI_NAME)
    badge_flexi_records = section.get_flexi_record_by_name(BADGE_FLEXI_NAME)['items']
    chief_scout_badge_record = section.get_badge_record(badge_id=section.chief_scout_badge['id'], badge_version=section.chief_scout_badge['version'])['items']

    print("\nBeginning update of Chief Scout Badge Count for", section.name)
    for scout_id, scout_data in section.scouts.items():
        if 'badges' in scout_data:
            activity_count = 0
            staged_count   = 0
            badge_tally = [scout_data['full_name']]
            for badge in scout_data['badges']:
                if badge['completed'] != '0':
                    if badge['badge_group'] == '2':
                        activity_count += 1
                    elif badge['badge_group'] == '3':
                        staged_count += 1
        
            # Update Badge Flexi-Record for Activity Badges
            badge_tally.append(activity_count)
            badge_tally.append(staged_count)

            # Update Badge Flexi Record
            for record in badge_flexi_records:
                if record['scoutid'] == scout_id:
                    if record[badge_flexi['activity_badges']] != activity_count:
                        update = section.update_flexi_record(badge_flexi['extraid'], scout_id, badge_flexi['activity_badges'], str(activity_count))
                    if record[badge_flexi['staged_badges']] != staged_count:
                        update = section.update_flexi_record(badge_flexi['extraid'], scout_id, badge_flexi['staged_badges'], str(staged_count))

            # Update the Chief Scouts Minimum Badge Criteria (if met)
            if (staged_count + activity_count) >= badges_required:
                badge_tally.append("Yes")

                # Create Badge Update Data
                data = {
                    'badge_id': section.chief_scout_badge['id'],
                    'badge_version': section.chief_scout_badge['version'],
                    'field': section.chief_scout_badge['badges_count_field'],
                    'scoutid': scout_id,
                    'section_id': section.id,
                    'term': section.current_term,
                    'value': '[YES]'
                }
                for record in chief_scout_badge_record:
                    if record['scoutid'] == scout_id:
                        if (data['field'] not in record) or (record[data['field']] != data['value']):
                            print(scout_data['full_name'],"has satisfied badge requirements, updating...")
                            update = section.update_badge_record(data)
            
            badge_count.append(badge_tally)

    print("\n\nBadge Count for", section.name)
    print(tabulate(badge_count, headers='firstrow'))
    print("Finished update of Chief Scout Badge Count for", section.name)

'''
#######################################
Tally Challenge Badge Completions

Inputs:
   * OSM Object

Description:
   Processes the completion state of the Challenge Badges in the section.
   Outputs data as table in console, as well as a new Flexi Record called 'Challenge Badges'
   which is created if it doesn't exist.
   For completion status of multiple requirements (such as Adventurous Activity) will
   calculate the least number completed assuming requirements are completed in OSM left-to-right
   (which is OSM default).
#######################################
'''
def tally_challenge_badge_completion(section):
    challenge_badges = section.get_badge_structure(BADGE_NAME['challenge'])['structure']
    challenge_flexi_record = section.get_flexi_record_by_name('Challenge Badges', create = True, type = 'badge')

    for badge_name, badge_data in section.badges['challenge'].items():
        record = section.get_badge_record_by_identifier(badge_data['identifier'])['items']
        completion = [['Activity','Status']]
        for row in challenge_badges[badge_data['identifier']][1]['rows']:
            column_name = f"({badge_name}) {row['name']}"
            column_id = ''
            for column in challenge_flexi_record['config']:
                if column['name'] == column_name:
                    column_id = column['id']
                    break
            if column_id == '':
                column_id = section.create_flexi_column(challenge_flexi_record['extraid'], column_name)
                challenge_flexi_record['config'].append({'id':column_id, 'name':column_name, 'width':'150'}) 
            count = 0
            for activity in record:
                if (row['field'] in activity) and (activity[row['field']][0] != 'x'):
                    count += 1
                    update_value = '[YES]'
                else:
                    update_value = ''
                for scout in challenge_flexi_record['items']:
                    if (scout['scoutid'] == str(activity['scoutid'])) and (scout[column_id] != update_value):
                        scout[column_id] = update_value
                        section.update_flexi_record(challenge_flexi_record['extraid'], scout['scoutid'],column_id, update_value)
                        break
            completion.append([row['name'],f'{count} ({round((count / section.size) * 100 )}%)'])

        print("\n{}\n{}\n".format(badge_name, '=' * len(badge_name)))
        print(tabulate(completion, headers='firstrow'))
        