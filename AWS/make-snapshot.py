#!/usr/bin/python

# This wants three args passed to it on the comand-line:
# - NameTag: the Name tag of either the instance or the volume that is
#   desired.  In the former case, all volumes attached to the instance
#   will be snapshotted, in a way that is consistent across a reboot.
#   And in the latter case, it just snapshots the specific volume
#   you've provided the Name tag of.  In either case, the script won't
#   snapshot anything without a Name tag.
# - housekeeper: This is the tag that is used later by the delete
#   script, to find the snapshots that need to be cleaned-up.
# - description: what it says on the tin.  If you're feeling lazy, you
#   can just pass the empty string in a pair of quotes.  I didn't
#   really consider it worth my while to implement the logic for
#   making this optional.

import sys

from boto3 import Session

def assert_singular( parentList, listName ):

    resourceList = [ t for t in parentList[ listName ] if 'instance' == t[ 'ResourceType' ] or 'volume' == t[ 'ResourceType' ] ]

    if 1 != len( resourceList ):
        print( f'ERROR: resource is non-singular' )
        sys.exit( 1 )

    [ resource ] = resourceList

    return( resource )

NameTag     = sys.argv[1]
housekeeper = sys.argv[2]
description = sys.argv[3]

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
            TagSpecifications = tagspec,
            VolumeId = rid )

        sid = response[ 'SnapshotId' ]

        print( f'SnapshotId = {sid}' )

    case _:

        print( f'handler for resource type {resourceType} not implemented' )
        sys.exit( 1 )
