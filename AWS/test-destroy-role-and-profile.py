#!/usr/bin/python

from json import dumps
from access import InstanceProfileRole

irp = InstanceProfileRole()

# The output of this goes to STDERR
response = irp.destroy( 'Baseline' )

# This goes to STDOUT, so redirect it to a file (e.g., stdout.json), then
# view it later using JQ (e.g., "jq -SC < stdout.json | less -RXi".
#
print( dumps( response, default = str ) )
