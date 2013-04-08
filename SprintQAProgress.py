# http://jira-python.readthedocs.org/en/latest/index.html
# se suman: el spent + remaining stimate
# Siempre hay 4 tiempos:
# tiempo estimacion (independiente)
# tiempo trabajo (Current Work Time): SUM(tiempo gastado) + tiempo restante
# (esta ultima al final siempre da lo que ha sido realmente)

from optparse import OptionParser
from jira.client import JIRA
from itertools import ifilter

### ARGUMENTS PROCESSING ###

parserArg = OptionParser(usage="usage: %prog [options]")
parserArg.add_option("-u", "--user", dest="user_progress", help="User progress")
parserArg.add_option("-s", "--sprint", dest="ongoing_sprint", help="Ongoing Sprint")
#parserArg.add_option("-f", "--filename", dest="filename", help="filename that contains users list")

opts, args = parserArg.parse_args()

assigneeid = opts.user_progress
sprintid = opts.ongoing_sprint

#if opts.user_progress:
	
### CONNECTION TO JIRA ###

user = 'cramiro'
pwd = 'panader0'

jac = JIRA(options={'server': 'https://jirapdi.tid.es'}, basic_auth=('cramiro', 'panader0'))

### USED FUNCTIONS ###
def check_item(x):
	return (x!=None)
	
def days_hours(x):
	time = []
	days,seconds = divmod(x, 28800)
	time.append(days)
	hours,seconds = divmod(seconds, 3600)
	time.append(hours)
	return(time)

# Usar diccionarios !!!!!

### INPUT DATA ###
	
# OPENTEL
#assigneeIDs=['jlav432','EMPTY']
#assigneeNames=['Apuy','Unassigned']
#focusFactor=[70,0]
#vacationDays=[0,0]
#sprintDays=10
#ongoingSprintDay=1
#sprintid=337 #(Sprint 44)

# NEOSDP (PLATFORM)
#assigneeIDs=['jjmf39','aas352','ngm352','sdmt','jfr39','slt245','ful002','anab07','ppc','EMPTY']
#assigneeNames=['JJoseM','Ana Acebal','Noe','Santi','JaviF','Silvia','Ana G Velicia','Ana Belen','Pablo Perez','Unassigned']
#focusFactor=[70,70,70,70,70,70,70,61,61,0]
#vacationDays=[0,0,0,0,0,0,0,0,0,0]
#sprintDays=10
#ongoingSprintDay=1
#sprintid=312 #(Sprint_35=2_Platform)

# NEOSDP (SERVICES)
assigneeIDs=['pbg352','ac266','pfg352','EMPTY']
assigneeNames=['Pablo Bermejo','Alex','Patricia','Unassigned']
focusFactor=[70,70,70,0]
vacationDays=[0,0,2,0]
sprintDays=10
ongoingSprintDay=1
sprintid=338 #(Sprint_36=3_Services)

# GRETA
#assigneeIDs=['njg273', 'laura266', 'cramiro','EMPTY']
#assigneeNames=['Nelson','Laura','Cristina','Unassigned']
#focusFactor=[70,70,50,0]
#vacationDays=[0,0,2,0]
#sprintDays=10
#ongoingSprintDay=1
#fixVersionid=34098 #(Release 2.3)

totalSprintSec=sprintDays*28800
remainingSprintSec = (sprintDays-ongoingSprintDay)*28800
# 4h (14400sec) - Work Load tolerance
tolerance = 14400
	
for assignee in assigneeIDs:
	### USER INFO ###
	JQL = 'assignee = ' + str(assignee) + ' AND sprint = ' + str(sprintid)
	#JQL = 'assignee = ' + str(assignee) + ' AND fixVersion=' + str(fixVersionid) + ' AND status not in (Closed)'
	id = assigneeIDs.index(assignee)
	assigneeName = assigneeNames[id]
	print '\n' + assigneeName + ': ' + JQL
	
	assigneeSprintDays = sprintDays - vacationDays[id]
	effectiveTime = (focusFactor[id]*assigneeSprintDays)/100
	effectiveTimeSec = effectiveTime*28800
	print 'Effective Sprint Days (' + str(vacationDays[id]) + ' vacation days and ' + str(focusFactor[id]) + '% of Focus Factor): ' + str(effectiveTime) + 'd'
	
	#print [issue.key for issue in jac.search_issues(JQL)]

	### ASSIGNED TASKS INFO ###
	# Estimations for all tasks in the JQL query
	originalEstimate = [issue.fields.timeoriginalestimate for issue in jac.search_issues(JQL)]
	
	NoneTasks = originalEstimate.count(None)
	print 'Tasks without estimation: ' + str(NoneTasks)
	
	# Only time estimated tasks in the JQL query is required (Non estimated tasks are filtered)
	originalEstimate[:] = list(ifilter(check_item, originalEstimate))
	
	estimatedTasks = len(originalEstimate)
	print 'Estimated Tasks: ' + str(estimatedTasks)
	
	### ESTIMATED WORK TIME ###
	# Total time in seconds for the estimated tasks
	originalEstimateSec = sum(originalEstimate)
	estimatedTime = days_hours(originalEstimateSec)
	
	if ((effectiveTimeSec - tolerance) > originalEstimateSec) and assigneeName is not 'Unassigned':
		print '  Estimated Work Time: ' + str(estimatedTime[0]) + 'd ' + str(estimatedTime[1]) + 'h (Low Work Load)'
	elif ((effectiveTimeSec + tolerance) < originalEstimateSec) and assigneeName is not 'Unassigned':
		print '  Estimated Work Time: ' + str(estimatedTime[0]) + 'd ' + str(estimatedTime[1]) + 'h (High Work Load)'
	else:
		print '  Estimated Work Time: ' + str(estimatedTime[0]) + 'd ' + str(estimatedTime[1]) + 'h'

	#timeSpent = [issue.fields.timespent for issue in jac.search_issues(JQL)]
	#timeSpentSum = sum(timeSpent)
	#print 'Time Spent (sec): ' + str(timeSpentSum)

	
	### ESTIMATED REMAINING TIME ###
	remainingEstimate = [issue.fields.timeestimate for issue in jac.search_issues(JQL)]
	remainingEstimate[:] = list(ifilter(check_item, remainingEstimate))
	remainingEstimateSec = sum(remainingEstimate)
	remainingTime = days_hours(remainingEstimateSec)	
	
	if (remainingSprintSec > remainingEstimateSec) and assigneeName is not 'Unassigned':
		print '  Remaining Work Time: ' + str(remainingTime[0]) + 'd ' + str(remainingTime[1]) + 'h (On Time)'
	elif (remainingSprintSec < remainingEstimateSec) and assigneeName is not 'Unassigned':
		print '  Remaining Work Time: ' + str(remainingTime[0]) + 'd ' + str(remainingTime[1]) + 'h (Danger)'
	else:
		print '  Remaining Work Time: ' + str(remainingTime[0]) + 'd ' + str(remainingTime[1]) + 'h'


