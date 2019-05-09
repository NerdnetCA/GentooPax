#!/usr/bin/python

# This is a script to assist in updating software packages
# in Gentoo Linux.
#
# It produces a list of all packages that are still installed,
# with a merge date prior to a specified timeframe.

import sys
import portage
import operator 
import datetime
import subprocess
from dateutil.relativedelta import relativedelta

# Default 1 year cutoff date
MONTHSPAST = 12

# Read a number of months as an argument, if given
if len(sys.argv) > 1:
    MONTHSPAST = int(sys.argv[1])

# Get a handle to the portage database. (Portage is the system package manager)
portdb = portage.db[portage.root]['vartree'].dbapi

# Get the merge history - all packages merged, in order, with the merge date.
# "qlop" is a commandline tool that produces the merge log.
qloplist = subprocess.run(['qlop','-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')
data = qloplist

# Break it into lines. 
lines = data.split('\n')

# Initialize a dictionary to track the packages
packages = {}

# Iterate over the lines of the merge history
for line in lines:
    # Split each line on the >>> marker, separating datestamp from package atom
    item = line.split('>>>')
    # If we didn't get two elements, ignore this line of input
    if len(item) > 1:
        # Check if this package atom is still installed
        installed = portdb.match(item[1].strip())
        if len(installed) > 0:
            # Insert package into the package dictionary with a datetime object.
            # If the package is already present, the date of merge will be replaced.
            mykey = portage.catpkgsplit(installed[0])[0] + '/' + portage.catpkgsplit(installed[0])[1]
            dt = datetime.datetime.strptime(item[0].strip()[4:], '%b %d %H:%M:%S %Y')
            packages[mykey] = dt
    
# Now we have a dictionary of all installed package atoms, with the
# most recent date on which they were merged.
    
# Create a sorted list from the packages dictionary.
done = sorted(packages.items(), key=operator.itemgetter(1))

# Determine cutoff date, and print all package atoms merged prior to this.
cutoff = datetime.datetime.today() + relativedelta(months=-MONTHSPAST)
for x in done:
    if x[1] < cutoff: 
        print(x[0])
        
        
