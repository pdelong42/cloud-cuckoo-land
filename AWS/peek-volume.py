#!/usr/bin/python

import sys

from json import dumps
from boto3 import Session

cetacean = Session().client( service_name = 'ec2' )

def assert_singular( parentList, resourceType ):

    resourceList = parentList[ resourceType ]

    if 1 != len( resourceList ):
        print( f'ERROR: {resourceType} non-singular' )
        sys.exit( 1 )

    [ resource ] = resourceList

    return( resource )

def print_volume_info( resourceId ):

    ids = [ resourceId ]
    response = cetacean.describe_volumes( VolumeIds = ids )
    volume = assert_singular( response, 'Volumes' )
    vid = volume[ 'VolumeId' ]
    size = volume[ 'Size' ]
    vtype = volume[ 'VolumeType' ]

    print( f'VolumeId = {vid}' )
    print( f'VolumeType = {vtype}' )
    print( f'Size = {size}' )

def root_volume_of_instance( resourceId ):

    ids = [ resourceId ]
    response = cetacean.describe_instances( InstanceIds = ids )
    reservation = assert_singular( response, 'Reservations' )
    instance = assert_singular( reservation, 'Instances' )
    blockdevs = instance[ 'BlockDeviceMappings' ]
    rootdev = instance[ 'RootDeviceName' ]

    # footnote 1 #
    [ ebs ] = [ bd[ 'Ebs' ] for bd in blockdevs if rootdev == bd[ 'DeviceName' ] ]

    vid = ebs[ 'VolumeId' ]

    return( vid )

def get_volume_id( ResourceName ):

    response = cetacean.describe_tags( Filters = [ { 'Name': 'tag:Name', 'Values': [ ResourceName ] } ] )
    tag = assert_singular( response, 'Tags' )
    rid = tag[ 'ResourceId' ]

    match tag[ 'ResourceType' ]:
        case 'instance':
            return( root_volume_of_instance( rid ) )
        case 'volume':
            return( rid )
        case _:
            print( f'handler for resource type {resourceType} not implemented' )
            sys.exit( 1 )

NameTag = sys.argv.pop()

print_volume_info( get_volume_id( NameTag ) )

# Footnote 1:
#
# Yeah, I'm taking a little bit of a chance here by assuming there is
# only one match to my filter.  But under normal circumstances that
# should be the case.  I'm also making the assumption that EBS is the
# only block device type, which I might be wrong about (which begs the
# question: what other types are there?).
