# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
import random
import mysql.connector
import time
import matplotlib.pyplot as plt
import numpy

#vars for counting
issueCount = 0
sevIssues1Min = 0
sevIssues3Min = 0
sevIssues5Min = 0

ticketDB = mysql.connector.connect(
    host="localhost",
    user="root2",
    password="password",
    database="jiratickettracking"
)
dbCursor = ticketDB.cursor()
#create issues until we reach desired number
while issueCount < 1:
    print(" -- next ticket -- ")

#call issue Create api endpoint
    url = "https://bryanrockwood.atlassian.net/rest/api/3/issue"

    # make sure this is our api
    auth = HTTPBasicAuth("bryanprockwood@gmail.com", "*****************")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = json.dumps({

     "fields": {
       "summary": "We made this in a while loop",
         "issuetype" : {
           "id": "10001"
         },
       "project": {
          "id": "10000"
                    },
         "priority": {
          "id": random.choice(["1", "2", "3", "4", "5"])
             }
        }
    })
    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    issueCount += 1
#save the id from the ticket we just made
    jiraID = json.loads(response.text)
    latestTicket = jiraID["key"]
#get info to check priority

    urlGet = "https://bryanrockwood.atlassian.net/rest/api/3/issue/"+latestTicket+"?fields=priority"

    authGet = HTTPBasicAuth("bryanprockwood@gmail.com", "**********")

    headersGet = {
        "Accept": "application/json"
    }

    responseGet = requests.request(
        "GET",
        urlGet,
        headers=headersGet,
        auth=authGet
    )
    checkPrio = json.loads(responseGet.text)
    sevJiraID = checkPrio["id"]
    sevJiraKey = checkPrio["key"]
    sevJiraPrio = checkPrio["fields"]["priority"]["id"]
    sqlInsert = "INSERT INTO tickets (ticketID, ticketKey, ticketPriority) VALUES (%s, %s, %s)"
    sqlVals = (sevJiraID, sevJiraKey, sevJiraPrio)

#    print(checkPrio)
    if sevJiraPrio == "1" or  sevJiraPrio == "2":
        print(sevJiraPrio + " is a critical ticket value ")
        print("Jira ID: " + sevJiraID + ", Jira Key: " + sevJiraKey)
        if time.perf_counter() > 300:
            sevIssues5Min += 1
        elif time.perf_counter() > 180:
            sevIssues3Min += 1
        else:
            sevIssues1Min += 1
 # send high prio tickets to DB
        print("sending ticket info to dB for tracking")
        dbCursor.execute(sqlInsert, sqlVals)
        ticketDB.commit()

    else:
        print("Jira ID: " + sevJiraID + ", Jira Key: " + sevJiraKey)
        print("all good here. low urgency ticket")

#close the cursor of the db when we are done
ticketDB.close()

#get how long it took to run process
print(time.perf_counter())
#make the chart for visualization
ticketCreated = [sevIssues1Min, sevIssues3Min, sevIssues5Min]
timeFrame = ["1 Min", "3 Min", "5 Min"]
plt.bar(timeFrame, ticketCreated)
plt.title('Tickets Created over Time')
plt.xlabel('Time')
plt.ylabel('Tickets')

plt.show()

#end of script
