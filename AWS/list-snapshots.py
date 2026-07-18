#!/usr/bin/python

import sys

from boto3 import Session

housekeeper = sys.argv[1]

cetacean = Session().client( service_name = 'ec2' )

filters = []

if '' != housekeeper:
    filters = [ { 'Name': 'tag:housekeeping', 'Values': [ housekeeper ] } ]

# you have to restrict it by owner, or it'll go global...
response = cetacean.describe_snapshots( Filters = filters, OwnerIds = [ 'self' ] )

for s in response[ 'Snapshots' ]:

    vid = s[ 'VolumeId' ]
    sid = s[ 'SnapshotId' ]
    prog = s[ 'Progress' ]
    state = s[ 'State' ]
    vsize = s[ 'VolumeSize' ]

    print( f'snapshotId = {sid}; volumeId = {vid}; progress = {prog}; state = {state}; size = {vsize} GiB;' )
