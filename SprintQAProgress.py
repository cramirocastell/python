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

#def user_tasks(x):

#def user_time(x):

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
#assigneeIDs=['pbg352','ac266','pfg352']
#assigneeIDs=['pbg352','ac266','pfg352','EMPTY']
#assigneeNames=['Pablo Bermejo','Alex','Patricia']
#assigneeNames=['Pablo Bermejo','Alex','Patricia','Unassigned']
#focusFactor=[70,70,70,0]
#vacationDays=[0,0,2,0]
#sprintDays=10
#ongoingSprintDay=1
#sprintid='\'Sprint_36=3_Services\''

# GRETA
assigneeIDs=['njg273', 'laura266', 'cramiro','EMPTY']
assigneeNames=['Nelson','Laura','Cristina','Unassigned']
focusFactor=[70,70,50,0]
vacationDays=[0,0,2,0]
sprintDays=10
ongoingSprintDay=6
fixVersion='\'Release 2_3\'' 

totalSprintSec=sprintDays*28800
remainingSprintSec = (sprintDays-ongoingSprintDay)*28800
# 4h (14400sec) - Work Load tolerance
toleranceWork = 14400 #4h
toleranceEstimation = 28800 #1d


# Al terminar el with el fichero se cierra automáticamente, no es necesario añadir un close

#with open(newfile, 'w') as outfile, open(oldfile, 'r', encoding='utf-8') as infile:
#    for line in infile:
#        if line.startswith(txt):
#            line = line[0:len(txt)] + ' - Truly a great person!\n'
#        outfile.write(line)

			
for assignee in assigneeIDs:
	### USER INFO ###
	# All TASKS
	#JQL = 'assignee = ' + str(assignee) + ' AND sprint = ' + str(sprintid)  + ' AND issuetype in (Task,Sub-task)'
	JQL = 'assignee = ' + str(assignee) + ' AND fixVersion = ' + str(fixVersion)  + ' AND issuetype in (Task,Sub-task)'
	# Ongoing TASKS
	#JQLOngoing = 'assignee = ' + str(assignee) + ' AND sprint=' + str(sprintid) + ' AND issuetype in (Task,Sub-task) AND status not in (Impeded,Closed)'
	JQLOngoing = 'assignee = ' + str(assignee) + ' AND fixVersion = ' + str(fixVersion) + ' AND issuetype in (Task,Sub-task) AND status not in (Impeded,Closed)'
	# Impeded TASKS
	#JQLImpeded = 'assignee = ' + str(assignee) + ' AND sprint=' + str(sprintid) + ' AND issuetype in (Task,Sub-task) AND status = Impeded'
	JQLImpeded = 'assignee = ' + str(assignee) + ' AND fixVersion = ' + str(fixVersion) + ' AND issuetype in (Task,Sub-task) AND status = Impeded'
	# Closed TASKS
	#JQLClosed = 'assignee = ' + str(assignee) + ' AND sprint=' + str(sprintid) + ' AND issuetype in (Task,Sub-task) AND status = Closed'
	JQLClosed = 'assignee = ' + str(assignee) + ' AND fixVersion = ' + str(fixVersion) + ' AND issuetype in (Task,Sub-task) AND status = Closed'
	
	id = assigneeIDs.index(assignee)
	assigneeName = assigneeNames[id]
	print '\n*** ' + assigneeName + ' ***'
	print JQL

	assigneeSprintDays = sprintDays - vacationDays[id]
	effectiveTime = (focusFactor[id]*assigneeSprintDays)/100
	effectiveTimeSec = effectiveTime*28800
	print 'Effective Sprint Days (' + str(vacationDays[id]) + ' vacation days and ' + str(focusFactor[id]) + '% of Focus Factor): ' + str(effectiveTime) + 'd'
	
	#print [issue.key for issue in jac.search_issues(JQL)]

	### ASSIGNED TASKS INFO ###
	print '  TASKS'
	# Estimations for all tasks in the JQL query
	originalEstimate = [issue.fields.timeoriginalestimate for issue in jac.search_issues(JQL)]
	
	NoneTasksNo = originalEstimate.count(None)
	
	# Only time estimated tasks in the JQL query is required (Non estimated tasks are filtered)
	originalEstimate[:] = list(ifilter(check_item, originalEstimate))
	
	estimatedTasksNo = len(originalEstimate)
	print '    Assigned: ' + str(estimatedTasksNo+NoneTasksNo)
	
	if NoneTasksNo != 0:
		print '    (WARN) Tasks without estimation: ' + str(NoneTasksNo)
	
	# ONGOING TASKS
	ongoingTasks = [issue.key for issue in jac.search_issues(JQLOngoing)]
	ongoingTasksNo = len(ongoingTasks)
	if ongoingTasksNo !=0:
		ongoingIssues=[]
		for issue in ongoingTasks:
			ongoingIssues.append(str(issue))
		print '    Ongoing: ' + str(ongoingTasksNo) + ' -> ' + str(ongoingIssues)
	else:
		print '    Ongoing: ' + str(ongoingTasksNo)
		
	# IMPEDED TASKS
	impededTasks = [issue.key for issue in jac.search_issues(JQLImpeded)]
	impededTasksNo = len(impededTasks)
	if impededTasksNo !=0:
		impededIssues=[]
		for issue in impededTasks:
			impededIssues.append(str(issue))
		print '    Impeded: ' + str(impededTasksNo) + ' -> ' + str(impededIssues)
	else:
		print '    Impeded: ' + str(impededTasksNo)
		
	# CLOSED TASKS
	closedTasks = [issue.key for issue in jac.search_issues(JQLClosed)]
	closedTasksNo = len(closedTasks)
	if closedTasksNo !=0:
		closedIssues=[]
		for issue in closedTasks:
			closedIssues.append(str(issue))
		print '    Closed: ' + str(closedTasksNo) + ' -> ' + str(closedIssues)
	else:
		print '    Closed: ' + str(closedTasksNo)
	
	### ESTIMATED WORK TIME ###
	print '  TIME'
	# Total time in seconds for the estimated tasks
	originalEstimateSec = sum(originalEstimate)
	estimatedTime = days_hours(originalEstimateSec)
	
	if ((effectiveTimeSec - toleranceWork) > originalEstimateSec) and assigneeName is not 'Unassigned':
		print '    Estimated Work Time: {0}d {1}h (Low Work Load)'.format(str(estimatedTime[0]), str(estimatedTime[1]))
	elif ((effectiveTimeSec + toleranceWork) < originalEstimateSec) and assigneeName is not 'Unassigned':
		print '    Estimated Work Time: {0}d {1}h (High Work Load)'.format(str(estimatedTime[0]), str(estimatedTime[1]))
	else:
		print '    Estimated Work Time: {0}d {1}h'.format(str(estimatedTime[0]), str(estimatedTime[1]))

	timeSpent = [issue.fields.timespent for issue in jac.search_issues(JQL)]
	timeSpent[:] = list(ifilter(check_item, timeSpent))
	timeSpentSec = sum(timeSpent)
	timeSpent = days_hours(timeSpentSec)
	print '    Logged Time: {0}d {1}h'.format(str(timeSpent[0]), str(timeSpent[1]))
	
	### ESTIMATED REMAINING TIME ###
	remainingEstimate = [issue.fields.timeestimate for issue in jac.search_issues(JQL)]
	remainingEstimate[:] = list(ifilter(check_item, remainingEstimate))
	remainingEstimateSec = sum(remainingEstimate)
	remainingTime = days_hours(remainingEstimateSec)	
	
	if (remainingSprintSec > remainingEstimateSec) and assigneeName is not 'Unassigned':
		print '    Remaining Work Time: {0}d {1}h (On Time)'.format(str(remainingTime[0]), str(remainingTime[1]))
	elif (remainingSprintSec < remainingEstimateSec) and assigneeName is not 'Unassigned':
		print '    Remaining Work Time: {0}d {1}h (Danger)'.format(str(remainingTime[0]), str(remainingTime[1]))
	else:
		print '    Remaining Work Time: {0}d {1}h'.format(str(remainingTime[0]), str(remainingTime[1]))
	
	workTimeSec = timeSpentSec + remainingEstimateSec
	workTime = days_hours(workTimeSec)
	
	if (workTimeSec - toleranceEstimation > originalEstimateSec) and assigneeName is not 'Unassigned':
		print '    Real Work Time: {0}d {1}h (Under Estimated)'.format(str(workTime[0]), str(workTime[1]))
	elif (workTimeSec  + toleranceEstimation < originalEstimateSec) and assigneeName is not 'Unassigned':
		print '    Real Work Time: {0}d {1}h (Over Estimated)'.format(str(workTime[0]), str(workTime[1]))
	else:
		print '    Real Work Time: {0}d {1}h'.format(str(workTime[0]), str(workTime[1]))


