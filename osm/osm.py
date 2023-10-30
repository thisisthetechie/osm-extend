''' OSM Class. '''
import requests, json, time, logging
from datetime import datetime

from .config import *
from . import headers

class OSM:
    def __init__(self, section_name) -> None:
        self.name = section_name
        for role in self.get_user_roles():
            if role['section'] == section_name:
                self.id = role['sectionid']
                self.group = role['groupname'].replace(section_name.title(), '').strip()
        self.current_term = self.get_current_term()
        self.chief_scout_badge = self.get_chief_scout_badge()
        
        self.badges = dict()
        for badges in range(1,4):
            self.badges.update({BADGE_TYPE[badges]: {}})
            badge_details = self.get_badge_structure_by_type(badges)['details']

            for badge in badge_details:
                self.badges[BADGE_TYPE[badges]].update({
                    badge_details[badge]['name']: {
                        "id": badge_details[badge]['badge_id'],
                        "version": badge_details[badge]['badge_version'],
                        "identifier": badge_details[badge]['badge_identifier'],
                        "picture": badge_details[badge]['picture'],
                        "description": badge_details[badge]['description']
                    }
                })

        self.scouts = dict()
        self.size = 0
        for scout in self.get_scouts():
            self.scouts.update({str(scout['scoutid']): {
                "firstname": scout['firstname'],
                "lastname": scout['lastname'],
                "photo_guid": scout['photo_guid'],
                "patrolid": scout['patrolid'],
                "patrol": scout['patrol'],
                "patrol_role_level_label": scout['patrol_role_level_label'],
                "active": scout['active'],
                "full_name": scout['full_name']
            }})
            if int(scout['age'].split(' ')[0]) < 14:
                self.size += 1

        for badges in self.get_badge_records_by_member()['data']:
            self.scouts[str(badges['scoutid'])].update({'badges':badges['badges']})


    def __str__(self):
        return f"{self.group}"
    
    def post(self, url, scope, data = None, json_output = True):
        response = requests.post(url = url, headers = headers[scope], data = data)

        if int(response.headers._store['x-ratelimit-remaining'][1]) < 300:
            raise Exception(f"Rate limit dangerously low ({response.headers._store['x-ratelimit-remaining'][1]}), stopping")

        if response.status_code == 429:
            print("Too many requests, sleeping")
            time.sleep(int(response.headers._store['retry-after'][1])+2)
            response = requests.post(url = url, headers = headers[scope], data = data)

        if response.status_code != 200:
            raise Exception("OSM Request failed:", response.status_code, response.text)
        
        if json_output:
            response = json.loads(response.content)

        return response

    def get(self, url, scope, json_output = True):
        response = requests.get(url = url, headers = headers[scope])
        
        if int(response.headers._store['x-ratelimit-remaining'][1]) < 30:
            raise Exception(f"Rate limit dangerously low ({response.headers._store['x-ratelimit-remaining'][1]}), stopping")

        if response.status_code == 429:
            print("Too many requests, sleeping")
            time.sleep(int(response.headers._store['retry-after'][1])+2)
            response = requests.get(url = url, headers = headers[scope])

        if response.status_code != 200:
            raise Exception("OSM Request failed:", response.status_code, response.text)
        
        if json_output:
            response = json.loads(response.content)

        return response

    def get_scouts(self):
        url = f'{OSM_BASE_URL}/ext/members/contact/?action=getListOfMembers&sort=lastname&sectionid={self.id}&termid={self.current_term}&section={self.name}'
        return self.get(url = url, scope = 'member')['items']

    def get_terms(self):
        url = f'{OSM_BASE_URL}/api.php?action=getTerms&section_id={self.id}&section={self.name}'
        return self.get(url = url, scope = 'programme')
    
    def get_term(self, term_id):
        for term in self.get_terms()[self.id][::-1]:
            if term['termid'] == term_id:
                return term

    def get_current_term(self):
        terms = self.get_terms()[self.id]
        for term in terms[::-1]:
            startdate = [int(date) for date in term['startdate'].split('-')]
            enddate   = [int(date) for date in term['enddate'].split('-')]
            term_start = datetime(startdate[0], startdate[1], startdate[2])
            term_end   = datetime(enddate[0], enddate[1], enddate[2])
            if datetime.today() >= term_start and datetime.today() <= term_end:
                return term['termid']
        return terms[-1]['termid']

    def create_flexi_column(self, extraid, column_name):
        url = f'{OSM_BASE_URL}/ext/members/flexirecords/?action=addColumn&sectionid={self.id}&extraid={extraid}'
        data = {
            "columnName": column_name
        }
        column_config = self.post(url = url, scope = 'flexi', data = data)['config']
        return json.loads(column_config)[0]['id']

    def create_flexi_record(self, flexi_record_name, type = 'maths'):
        url = f'{OSM_BASE_URL}/ext/members/flexirecords/?action=addRecordSet&sectionid={self.id}'
        data = {
            "name":	flexi_record_name,
            "type": type
        }
        return self.post(url = url, scope = 'flexi', data = data)['id']

    def get_badges_flexi(self, flexi_record_name):
        url = f'{OSM_BASE_URL}/ext/members/flexirecords/?action=getFlexiRecords&sectionid={self.id}&archived=n'
        flexi_records = self.get(url = url, scope = 'flexi')
        
        # Create object to pass out
        badges_flexi_record = {'knots': {}}
        for flexi_record in flexi_records['items']:
            if flexi_record['name'] == flexi_record_name:
                badges_flexi_record.update({'extraid':flexi_record['extraid']})
                url = f"{OSM_BASE_URL}/ext/members/flexirecords/?action=getStructure&sectionid={self.id}&extraid={flexi_record['extraid']}"
                flexi_config = self.get(url = url, scope = 'flexi')['config']
                flexi_structure = json.loads(flexi_config)
                for col in flexi_structure:
                    if col['name'] == "Activity Badges":
                        badges_flexi_record.update({'activity_badges':col['id']})
                    elif col['name'] == "Staged Badges":
                        badges_flexi_record.update({'staged_badges':col['id']})
                    elif col['name'] == "Shoelace":
                        badges_flexi_record['knots'].update({'shoelace':col['id']})
                    elif col['name'] == "Reef Knot":
                        badges_flexi_record['knots'].update({'reef':col['id']})

        # Create the Flexi Record if it doesn't exist
        if len(badges_flexi_record) == 0:
            flexi_id = self.create_flexi_record(BADGE_FLEXI_NAME)
            badges_flexi_record = {
                'extraid': flexi_id,
                'activity_badges': self.create_flexi_column(self.id, flexi_id, "Activity Badges"),
                'staged_badges': self.create_flexi_column(self.id, flexi_id, "Staged Badges")
            }

        return badges_flexi_record
            
    def get_flexi_record_by_id(self, extraid):
        url = f'{OSM_BASE_URL}/ext/members/flexirecords/?action=getData&extraid={extraid}&sectionid={self.id}&termid={self.current_term}&nototal'
        flexi_record = {'extraid':extraid}
        flexi_record.update(self.get(url = url, scope = 'flexi'))
        flexi_record.update({'config':self.get_flexi_column_config(flexi_record['extraid'])})
        return flexi_record
    
    def get_flexi_record_by_name(self, name, create = False, type = 'maths'):
        for record in self.get_all_flexi_records():
            if record['name'] == name:
                return self.get_flexi_record_by_id(record['extraid'])
        if create:
            return self.get_flexi_record_by_id(self.create_flexi_record(name, type))
    
    def get_flexi_record_id(self, name, create = False, type = 'maths'):
        for record in self.get_all_flexi_records():
            if record['name'] == name:
                return record['extraid']
        if create:
            return self.create_flexi_record(name, type)
        
    def get_flexi_column_config(self, flexi_record):
        url = f"{OSM_BASE_URL}/ext/members/flexirecords/?action=getStructure&sectionid={self.id}&extraid={flexi_record}"
        return json.loads(self.get(url = url, scope = 'flexi')['config'])

    def get_all_flexi_records(self):
        url = f'https://www.onlinescoutmanager.co.uk/ext/members/flexirecords/?action=getFlexiRecords&sectionid={self.id}&archived=n'
        return self.get(url = url, scope = 'flexi')['items']

    def get_badge_records_by_member(self):
        url = f'{OSM_BASE_URL}/ext/badges/badgesbyperson/?action=loadBadgesByMember&section={self.name}&sectionid={self.id}&term_id={self.current_term}'
        return self.get(url = url, scope = 'badge')

    def get_badge_record(self, badge_id, badge_version):
        url = f'{OSM_BASE_URL}/ext/badges/records/?action=getBadgeRecords&term_id={self.current_term}&section={self.name}&badge_id={badge_id}&section_id={self.id}&badge_version={badge_version}'
        return self.get(url = url, scope = 'badge')
    
    def get_badge_record_by_identifier(self, badge_identifier):
        badge_id = badge_identifier.split('_')[0]
        badge_version = badge_identifier.split('_')[1]

        url = f'{OSM_BASE_URL}/ext/badges/records/?action=getBadgeRecords&term_id={self.current_term}&section={self.name}&badge_id={badge_id}&section_id={self.id}&badge_version={badge_version}'
        return self.get(url = url, scope = 'badge')

    def get_user_roles(self):
        return self.get(url = ROLES_URL, scope = 'programme')

    def get_badge_structure_by_type(self, type_id):
        url = f'{OSM_BASE_URL}/ext/badges/records/?action=getBadgeStructureByType&a=1&section={self.name}&type_id={type_id}&term_id={self.current_term}&section_id={self.id}'
        return self.get(url = url, scope = 'badge')

    def get_chief_scout_badge(self):    
        # Get badges
        url = f'{OSM_BASE_URL}/ext/badges/records/?action=getBadgeStructureByType&a=1&section={self.name}&type_id=1&term_id={self.current_term}&section_id={self.id}'
        badge_structure = self.get(url = url, scope = 'badge')
        badge_id = badge_structure['badgeOrder'].split(',')[0]
        field = badge_structure['structure'][badge_id][1]['rows'][-1]['field']

        chief_scout_badge = {
            "id": badge_id.split('_')[0],
            "version": badge_id.split('_')[1],
            "identifier": badge_id,
            "badges_count_field": field,
        }
        return chief_scout_badge

    def update_flexi_record(self, extraid, scout, column, value):
        data = {
            "extraid": extraid,
            "termid": self.current_term,
            "section": self.name,
            "sectionid": self.id,
            "scoutid": scout,
            "column": column,
            "value": value
        }
        return self.post(url = FLEXI_URL, scope = 'flexi', data = data)

    def update_badge_record(self, data):
        return self.post(url = BADGE_URL, scope = 'badge', data = data)

