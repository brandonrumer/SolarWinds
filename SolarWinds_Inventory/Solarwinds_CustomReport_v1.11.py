#!/usr/local/bin/python3
"""
Summary:
    Queries SolarWinds Orion for specific values and exports results
    to CSV.

Decription:
    Queries for Cisco devices' NodeName, IPAddress, SWVersion, SN, 
    CardName, CardDescr, CardSerial, Slot

Work to do on this script:
    Functions, and a whole lot more.
"""

"""  Importing built-in modules """
import csv
import sys
import datetime
import time

"""  Import external modules """
import requests
from orionsdk import SwisClient

__author__ = "Brandon Rumer"
__version__ = "1.11"
__email__ = "brumer@cisco.com"
__status__ = "Production"

#  Define solarwinds creds and connection settings
npm_server = ''
username = ''
password = ''

Works = {}

#  Defining date & time, because why not?
today_str = str(datetime.date.today())
timestamp = str(today_str + '-' + (time.strftime("%H%M")))

#  Clearing anything so we get a clean run
counter = 0
Results = []
csvExport = 'results-{}.csv'.format(timestamp)

verify = False
if not verify:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
swis = SwisClient(npm_server, username, password)

#  Start polling solarwinds for data
print('Polling Solarwinds for devices')

#working:
#node_results = swis.query("SELECT n.NodeName, n.IPAddress, n.Vendor, n.MachineType, c.ChassisID, c.ChassisSerialNumberString FROM Orion.Nodes n INNER JOIN NCM.Nodes AS x ON n.NodeID = x.CoreNodeID RIGHT JOIN NCM.CiscoChassis AS c ON x.NodeId = c.NodeID WHERE n.Vendor = 'Cisco'")

node_results = swis.query("SELECT a.NodeID, a.CardIndex, a.CardName, a.CardDescr, a.CardSerial, a.HWVersion, a.SWVersion, a.Slot, a.DisplayName, a.Description, c.NodeName, c.IPAddress, z.ChassisID FROM NCM.CiscoCards a \
    JOIN NCM.CiscoChassis AS z ON a.NodeID = z.NodeID \
    JOIN NCM.Nodes AS b ON a.NodeID = b.NodeID \
    JOIN Orion.Nodes AS c ON b.CoreNodeID = c.NodeID")


print(node_results)


#time.sleep(1)
writer = csv.writer(open(csvExport, 'w', newline=''))
writer.writerow(['NodeName', 'IPAddress', 'SWVersion', 'ChassisSN', 'CardName', 'CardDescr', 'CardSerial', 'Slot'])
for devices in node_results['results']:
    NodeName = ("{NodeName}".format(**devices))
    IP = ("{IPAddress}".format(**devices))
    SWVersion = ("{SWVersion}".format(**devices))
    ChassisID = ("{ChassisID}".format(**devices))
    CardName = ("{CardName}".format(**devices))   
    CardDescr = ("{CardDescr}".format(**devices))
    CardSerial = ("{CardSerial}".format(**devices))    
    Slot = ("{Slot}".format(**devices))
    writer.writerow([NodeName,IP,SWVersion,ChassisID,CardName,CardDescr,CardSerial,Slot])


print('')
print('Results saved at: ' , csvExport)

exit(0)
