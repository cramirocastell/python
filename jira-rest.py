import requests
from requests.auth import HTTPBasicAuth

import json

from jira.client import JIRA

import rsa

protocol='https://'
server = 'jirapdi.tid.es'

restversion = '/rest/api/latest'
restapi = '/issue'
restresource = '/BVINTEGRATION-11412'

#payload = {'userAgent': 'samsungm0xxGT-I9300', 'version': '3.0'}
headers = {'content-type': 'application/json'}

user = 'cramiro'
pwd = 'panader0'

auth = HTTPBasicAuth(user,pwd)

jac = JIRA(options={'server': 'https://jirapdi.tid.es'}, basic_auth=('cramiro', 'panader0'))

request = ''.join([protocol,server,restversion,restapi,restresource])

#print '\n' + request + '\n'

try:
	r = requests.get(request,auth=auth,headers=headers,verify=False,timeout=5.001)
except ValueError, err:
	print 'REQUEST ERROR:', r.raise_for_status()
	
# Print methods available for each request
print dir (r)

print '\nStatus Code: ' + str(r.status_code) + '\n'
print '\nEncoding: ' + r.encoding + '\n'

print r.content

try:
	print json.dumps(r.json(), sort_keys=True, indent=2) + '\n'
except ValueError, err:
	print 'JSON PARSE ERROR:', err