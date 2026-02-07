#!/usr/bin/python

from json import dumps
from access import InstanceProfileRole

ipr = InstanceProfileRole()

# The output of this goes to STDERR
response = ipr.create(
    'Baseline',
    'minmal set of permissions that should be associated with any instance in our environment' )

# This goes to STDOUT, so redirect it to a file (e.g., stdout.json), then
# view it later using JQ (e.g., "jq -SC < stdout.json | less -RXi".
#
print( dumps( response, default = str ) )
