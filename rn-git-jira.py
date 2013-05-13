# Using JIRA CLIENT from http://readthedocs.org/docs/jira-python/
# Modified the client.py in C:\Software\cygwin\lib\python2.7\site-packages\jira to bypass the private certifificate from jirapdi.tid.es

from jira.client import JIRA
from subprocess import Popen, PIPE
import re

def gitLog(initTag, endTag, repoDir):
	ref = '..'.join([initTag,endTag])
	cmd = ['git', 'log', '--oneline', ref]	
	gitlog = Popen(cmd, cwd=repoDir, stdout=PIPE)
	grep = Popen(['grep', 'Merge pull request'], stdin=gitlog.stdout, stdout=PIPE, stderr=PIPE)
	grep.wait()
	out = grep.stdout.read()
	#out, err = grep.communicate()
	return out

#subprocess.call(args, *, stdin=None, stdout=None, stderr=None, shell=False)

logList = gitLog('2.0.4/CC','release/2.0.4','C:\Users\cramiro\pdihub\wallet-nfc-gui')

print logList

p = re.compile('\w*-\d+')
issueNumbers = p.findall(logList)

print issueNumbers

# Remove duplicated issues by list conversion to set and then to list again
issueNumbers = list(set(issueNumbers))

print issueNumbers

#git_command = ['/usr/bin/git', 'status']
#repository = path.dirname('/path/to/dir/')
 
#git_query = Popen(git_command, cwd=repository, stdout=PIPE, stderr=PIPE)
#(git_status, error) = git_query.communicate()
#if git_query.poll() == 0:
# Do stuff



#import git
#import os, os.path
#g = git.Git(os.path.expanduser("~/git/GitPython"))
#result = g.execute(["git", "commit", "-m", "'message'"])

#git log --oneline 2.0.4/CC..release/2.0.4 | grep "Merge pull"

###########################

number = 'NEOSDP-197033'

jac = JIRA(options={'server': 'https://jirapdi.tid.es'}, basic_auth=('cramiro', 'panader0'))


issue = jac.issue(number, fields='summary,status')

print issue.key + ' ' + issue.fields.summary + '\n'

# Summaries of my last 3 reported issues
print [issue.fields.summary for issue in jac.search_issues('reporter = currentUser() order by created desc', maxResults=3)]


