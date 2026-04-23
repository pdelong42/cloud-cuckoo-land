#!/usr/bin/python

# Example:
#
#   ./test-image-lookup.py 2> stderr.json
#
# It prints results to STDOUT.  To troubleshoot problems:
#
#   jq -SC < stderr.json | less -RXi

import sys

from json import dumps
from amiuniq import UniqueMachineImage

# The idea here is to specify enough fitler tokens that only one
# result is returned.  Zero matches is considered a fatal error, and
# more than one match is met with a non-fatal warning.
#
# To make the response deterministic, use a time period that is no
# longer in flux.  For example: pick a month that just ended, and not
# the month that you are currently in the middle of.  The same goes
# for any time period, whether it's the year or the day).

umi = UniqueMachineImage( {
    'architecture': 'x86_64',
    'creation-date': '2026-02-*',
    'name': 'RHEL-*',
    'owner-id': '309956199498'
} )

# Note about Amazon Linux: the year of release (2023, in this case),
# is part of the name.  Don't let that confuse you; they've updated it
# since then.
#
#umi = UniqueMachineImage( {
#    'architecture': 'arm64',
#    'creation-date': '2026-01-22T*',
#    'name': 'al2023-ami-minimal-2023.10.*-kernel-6.12-*',
#    'owner-id': '137112412989'
#} )

#umi = UniqueMachineImage( {
#    'architecture': 'x86_64',
#    'creation-date': '2026-02-*',
#    'name': 'Fedora-Cloud-Base-AmazonEC2.x86_64-43-*',
#    'owner-id': '125523088429'
#} )

if 1 > umi.size:
    print( "ABORT: no match found" )
    sys.exit( 1 )

if 0 < umi.size:
    print( f'first match:\nAMI = {umi.ID}; name = {umi.name}' )

if not 1 < umi.size:
    sys.exit( 0 )

print( dumps( umi.images, default = str ), file = sys.stderr )

print( "extra matches:" )

for i in umi.images:
    AMI = i[ 'ImageId' ]
    name = i[ 'Name' ]
    print( f'AMI = {AMI}; name = {name}' )

#            'Values' : [ 'al2023-ami-2023.7.20250527.1-kernel-6.1-x86_64' ]
