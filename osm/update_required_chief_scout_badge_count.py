'''
#######################################
Update Required Chief Scout Badge Count

Inputs:
   * OSM Object

Description:
   Counts the number of Activity and Staged badges the Scout has earned.
   If the total is greater than or equal to the requirement for the Chief Scout Award
   then update the Chief Scout badge record.
#######################################
'''

from tabulate import tabulate

from .config import *

def update_required_chief_scout_badge_count(section):
    badges_required = SECTIONS[section.name]
    badge_count = [["Name","Activity","Staged","Completed"]]

    badge_flexi = section.get_badges_flexi(BADGE_FLEXI_NAME)
    badge_flexi_records = section.get_flexi_record_by_name(BADGE_FLEXI_NAME)['items']
    chief_scout_badge_record = section.get_badge_record(badge_id=section.chief_scout_badge['id'], badge_version=section.chief_scout_badge['version'])['items']

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
                        section.update_flexi_record(badge_flexi['extraid'], scout_id, badge_flexi['activity_badges'], str(activity_count))
                    if record[badge_flexi['staged_badges']] != staged_count:
                        section.update_flexi_record(badge_flexi['extraid'], scout_id, badge_flexi['staged_badges'], str(staged_count))

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
                            section.update_badge_record(data)
            
            badge_count.append(badge_tally)

    print(f"\nChief Scout Badge Count for {section.group} {section.name.title()}:\n")
    print(tabulate(badge_count, headers='firstrow'))
