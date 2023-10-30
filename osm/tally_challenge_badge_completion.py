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

from tabulate import tabulate

from .config import *

def tally_challenge_badge_completion(section):
    challenge_badges = section.get_badge_structure_by_type(BADGE_NAME['challenge'])['structure']
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
        