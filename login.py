from requests_oauth2client import OAuth2Client
from variables import TOKEN_URL, OSM_API_ID, OSM_API_SECRET

oauth2client = OAuth2Client(
   token_endpoint=TOKEN_URL,
   auth=(OSM_API_ID, OSM_API_SECRET)
)

headers = {
    "badge": {
        "Authorization": 'Bearer %s' % oauth2client.client_credentials(scope="section:badge:write")
    },
    "event": {
        "Authorization": 'Bearer %s' % oauth2client.client_credentials(scope="section:event:write")
    },
    "flexi": {
        "Authorization": 'Bearer %s' % oauth2client.client_credentials(scope="section:flexirecord:write")
    },
    "member": {
        "Authorization": 'Bearer %s' % oauth2client.client_credentials(scope="section:member:write")
    },
    "programme": {
        "Authorization": 'Bearer %s' % oauth2client.client_credentials(scope="section:programme:write")
    }
}

print("Authentication Headers Refreshed")