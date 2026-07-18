#!/usr/bin/python

import sys

from boto3 import Session

def assert_singular( parentList, resourceType ):

    resourceList = parentList[ resourceType ]

    if 1 != len( resourceList ):
        print( f'ERROR: {resourceType} non-singular' )
        sys.exit( 1 )

    [ resource ] = resourceList

    return( resource )

NameTag     = sys.argv[1]
description = sys.argv[2]
housekeeper = sys.argv[3]

cetacean = Session().client( service_name = 'ec2' )

response = cetacean.describe_tags( Filters = [ { 'Name': 'tag:Name', 'Values': [ NameTag ] } ] )
tag = assert_singular( response, 'Tags' )
rid = tag[ 'ResourceId' ]

tagspec = [
    { 'ResourceType': 'snapshot', 'Tags': [
        { 'Key': 'housekeeping', 'Value': housekeeper } ] } ]

match tag[ 'ResourceType' ]:

    case 'instance':

        response = cetacean.create_snapshots(
            Description = description,
            InstanceSpecification = { 'InstanceId': rid },
            TagSpecifications = tagspec )

        for s in response[ 'Snapshots' ]:
            sid = s[ 'SnapshotId' ]
            print( f'SnapshotId = {sid}' )

    case 'volume':

        response = cetacean.create_snapshot(
            Description = description,
            VolumeId = rid,
            TagSpecifications = tagspec )

        sid = response[ 'SnapshotId' ]

        print( f'SnapshotId = {sid}' )

    case _:

        print( f'handler for resource type {resourceType} not implemented' )
        sys.exit( 1 )
