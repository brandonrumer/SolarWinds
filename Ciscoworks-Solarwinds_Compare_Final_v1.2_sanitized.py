#!/usr/local/bin/python3
"""
Summary:
    Compares devices in a CSV to SolarWinds NCM and reports on devices
    not in SolarWinds NCM.

Description:
    When migrating from CiscoWorks NCM to Solarwinds NCM it can be
    a challenge to identify devices that have not been migrated to
    SolarWinds NCM.

    Unfortunately, there is no API or pythonic method to pull CiscoWorks
    inventory. To manually generate a report that is sufficient for this
    task:
        In CiscoWorks NCM generate a report:
            Click Report
            Click Single Report
            Select Date range: past month
            Generate
            Export CSV

Work to do on this script:
    Add functions, classes, comments ... a lot.
"""

"""  Importing built-in modules """
import csv
import socket
import argparse
import sys
import tempfile
import datetime
import time
import os
import getpass

"""  Import external modules """
import requests
from orionsdk import SwisClient

__author__ = "Brandon Rumer"
__version__ = "1.2"
__email__ = "brumer@cisco.com"
__status__ = "Production"

#  Defining date & time, because why not?
today_str = str(datetime.date.today())
timestamp = str(today_str + '-' + (time.strftime("%H%M")))

#  Clearing anything so we get a clean run
counter = 0
Results = []
csvExport = 'results-{}.csv'.format(timestamp)

#  Define solarwinds creds and connection settings
npm_server = ''
username = ''
password = ''

verify = False
if not verify:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
swis = SwisClient(npm_server, username, password)


#  Start polling solarwinds for data
print('Polling Solarwinds for devices')
node_results = swis.query("SELECT NodeName, IPAddress from Orion.Nodes n where n.Vendor = 'Cisco'")


#  Open the CiscoWorks CSV
Works = {}
with open('CiscoworksDevices.csv', 'r') as infile:
    reader = csv.reader(infile)
    Works = {rows[0]:rows[1] for rows in reader}
print("Here is what I have in my csv:")
print(Works)


#  Ask user if they want to do stuff to individual devices
print('')
CheckMemory = input('Do you want to check Solarwinds for devices that are in CiscoWorks NCM but are missing in SolarWinds? y/n  ').lower()
if CheckMemory == 'n':
    exit(0)
elif CheckMemory == 'y':
    print('OK!')
elif not (CheckMemory == 'y') or (CheckMemory == 'n'):
        print('Syntax error. Learn how to type. Exiting.')
        exit(0)

var = node_results['results']


def csv_search(var):
    for devices in node_results['results']:
            #print(devices['NodeName'])
            yield devices['NodeName']


writer = csv.writer(open(csvExport, 'w', newline=''))
writer.writerow(['NodeName', 'IPAddress', 'In Solarwinds?'])

for key, val in Works.items():
    if key in csv_search(var):
        #Results += [{key, val, True}]
        print("SolarWinds has:", key, "(", val, ")")
        writer.writerow([key, val, 'Yes'])
        continue
    elif key not in csv_search(var):
        #Results += [{key, val, False}]
        print("SolarWinds does not have:", key, "(", val, ")")
        writer.writerow([key, val, 'No'])
    else:
        print("SYNTAX ERROR")



print('')
print('Results saved at: ' , csvExport)


exit(0)
