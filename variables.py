import os
from dotenv import load_dotenv

load_dotenv()

OSM_API_ID     = os.environ.get("OSM_API_ID")
OSM_API_SECRET = os.environ.get("OSM_API_SECRET")
OSM_BASE_URL   = os.environ.get("OSM_BASE_URL")
TOKEN_URL = '{0}/oauth/token'.format(OSM_BASE_URL)
FLEXI_URL = '{0}/ext/members/flexirecords/?action=updateScout&nototal'.format(OSM_BASE_URL)
BADGE_URL = '{0}/ext/badges/records/?action=updateSingleRecord'.format(OSM_BASE_URL)
ROLES_URL = '{0}/api.php?action=getUserRoles'.format(OSM_BASE_URL)

BADGE_TYPE = {
    1:'challenge', 
    2:'activity', 
    3:'staged'
}
BADGE_NAME = dict([(value, key) for key, value in BADGE_TYPE.items()])

BADGE_FLEXI_NAME = os.environ.get("BADGE_FLEXI_NAME")

SECTIONS = {
    # Sections to process, and the number of required activity + staging badges to complete
    'beavers': 4,
    'scouts': 6
}

BEAVERS_REQUIRED_KNOTS = 3
