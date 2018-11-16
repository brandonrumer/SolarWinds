#!/usr/local/bin/python3
"""
Summary:
    Reads a CSV of IPs and checks to see if they are managed by
    Solarwinds NCM.

Description:
    In many cases Network shops maintain an IP spreadsheet. These IPs are
    issued to devices, but the devices are not always entered into
    SolarWinds NCM.
    
    This script imports a CSV of IP Adresses and checks to see if the
    devices respond to a ping. If the device responds, the script checks
    to see if the IP exists within SolarWinds NCM. It is important to
    note the script checks if the IP in the CSV exists in Solarwinds NCM,
    not just if it is the Solarwinds NCM polling IP (this reduces false
    positives).

Work to do on this script:
    Ask the user if they want to use a CSV of IPs or specified IP range. 
"""

"""  Importing built-in modules """
import subprocess
import os
import csv
import sys
import datetime
import time
import threading
from queue import Queue
from multiprocessing.pool import ThreadPool

"""  Import external modules """
import requests
from orionsdk import SwisClient

__author__ = "Brandon Rumer"
__version__ = "1.12"
__email__ = "brumer@cisco.com"
__status__ = "Production"


def check_ping(host):
    response = os.system("ping -n 1 " + host)
    if response == 0:
        pingstatus = "Active"
        #print(host , "is active")
    else:
        pingstatus = "Offline"
        #print(host , "is OFFLINE")
    return pingstatus


def solarwinds_query(npm_server, username, password):
    verify = False
    if not verify:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    swis = SwisClient(npm_server, username, password)
    node_results = swis.query("SELECT n.NodeName, ni.IPAddress from Orion.Nodes n join Orion.NodeIPAddresses ni ON n.nodeid=ni.nodeid where n.Vendor = 'Cisco'")
    return node_results


def SolarwindsIP(var):
    for devices in node_results['results']:
            yield devices['IPAddress']


def WorkIt(host, output_q):
    output_list = []
    #if host not in node_results['results']:
    try:
        if host not in SolarwindsIP(var):
            #print("Host NOT in SolarWinds")
            status = 'NOT in SolarWinds'
            pingstatus = check_ping(host)
        elif host in SolarwindsIP(var):
            #print("Host is in SolarWinds")
            status = 'IN SolarWinds'
            pingstatus = "Not Tested"
        else:
            status = 'ERROR'
            pingstatus = 'ERROR'

        output_list = [host, status, pingstatus]
        output_q.put([output_list])
    except KeyboardInterrupt:
        print('\n Fine. Exiting')
        exit(0)
    finally:
        threadLimiter.release()


if __name__ == "__main__":

    #  Clearing anything so we get a clean run
    counter = 0
    output_q = Queue()
    my_dict = []

    threadLimiter = threading.BoundedSemaphore(20) #  Max 20 threads
    
    #  Define solarwinds creds and connection settings
    npm_server = ''
    username = ''
    password = ''

    #  Defining date & time
    today_str = str(datetime.date.today())
    timestamp = str(today_str + '-' + (time.strftime("%H%M")))

    csvExport = 'results-{}.csv'.format(timestamp)
    writer = csv.writer(open(csvExport, 'w', newline=''))
    writer.writerow(['IPAddress', 'In Solarwinds?', 'Respond to Ping?'])

    #  Poll SolarWinds for data
    node_results = solarwinds_query(npm_server, username, password)
    var = node_results['results']
    SolarwindsIPs = SolarwindsIP(var)

    #  Open the CSV
    IPs = {}
    with open('IP_Addresses.csv', 'r') as infile:
        reader = csv.reader(infile)
        IPs = {rows[0] for rows in reader}

    #  Do the work, while limiting the number of threads
    for host in IPs:
        threadLimiter.acquire()
        my_thread = threading.Thread(target=WorkIt, args=(host, output_q))
        my_thread.start()


    #  Wait for threads to complete
    main_thread = threading.currentThread()
    for some_thread in threading.enumerate():
        if some_thread != main_thread:
            some_thread.join()

    #  Get everything from the queue
    while not output_q.empty():
        my_dict = output_q.get()
        for datastuff in my_dict:
            writer.writerow(datastuff)
            
    print('')
    print('Results saved at: ' , csvExport)

