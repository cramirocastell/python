# Using JIRA CLIENT from http://readthedocs.org/docs/jira-python/
# Modified the client.py in C:\Software\cygwin\lib\python2.7\site-packages\jira to bypass the private certifificate from jirapdi.tid.es

from jira.client import JIRA

number = 'NEOSDP-197033'

jac = JIRA(options={'server': 'https://jirapdi.tid.es'}, basic_auth=('cramiro', 'panader0'))


issue = jac.issue(number, fields='summary,status')

print issue.key + ' ' + issue.fields.summary + '\n'

# Summaries of my last 3 reported issues
print [issue.fields.summary for issue in jac.search_issues('reporter = currentUser() order by created desc', maxResults=3)]


