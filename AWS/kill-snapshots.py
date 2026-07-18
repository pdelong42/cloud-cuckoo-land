#!/usr/bin/python

import sys

from boto3 import Session

housekeeper = sys.argv[1]

cetacean = Session().client( service_name = 'ec2' )

filters = [ { 'Name': 'tag:housekeeping', 'Values': [ housekeeper ] } ]

# you have to restrict it by owner, or it'll go global...
response = cetacean.describe_snapshots( Filters = filters, OwnerIds = [ 'self' ] )
snapshots = response[ 'Snapshots' ]

print( 'Preparing to delete the following snapshots:' )
print()

for s in snapshots:

    vid = s[ 'VolumeId' ]
    sid = s[ 'SnapshotId' ]
    prog = s[ 'Progress' ]
    state = s[ 'State' ]
    vsize = s[ 'VolumeSize' ]

    print( f'snapshotId = {sid}; volumeId = {vid}; size = {vsize} GiB;' )

response = input( 'Continue? (y/n):' )

if 'y' != response:
    sys.exit()

for s in snapshots:
    sid = s[ 'SnapshotId' ]
    response = cetacean.delete_snapshot( SnapshotId = sid )
    print( f'Deleted {sid}' )
