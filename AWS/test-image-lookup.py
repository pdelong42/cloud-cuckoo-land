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

# Note about Amazon Linux: the year of release (2023, in this case),
# is part of the name.  Don't let that confuse you; they've updated it
# since then.
#
#umi = UniqueMachineImage( '137112412989',
#    architecture = 'arm64',
#    creation_date = '2026-05-01T*',
#    name = 'al2023-ami-minimal-2023.10.*-kernel-6.12-*' )

#umi = UniqueMachineImage( '125523088429',
#    architecture = 'x86_64',
#    creation_date = '2026-04-*',
#    name = 'Fedora-Cloud-Base-AmazonEC2.x86_64-43-*' )

#umi = UniqueMachineImage( '309956199498',
#    architecture = 'x86_64',
#    creation_date = '2026-04-*',
#    name = 'RHEL-*' )

umi = UniqueMachineImage( 'self' )

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
