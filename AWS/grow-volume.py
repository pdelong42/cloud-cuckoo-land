#!/usr/bin/python

# This wants one arg passed to it on the comand-line:
# - NameTag: the Name tag of either the instance or the volume that is
#   desired.  In the former case, the root volume attached to the
#   instance will be grown.  And in the latter case, it will grow the
#   specific volume you've provided the Name tag of.  In either case,
#   the script won't snapshot anything without a Name tag (though the
#   root volume doesn't have a Name tag, it is associated with an
#   instance that does).

import sys
import time

from boto3 import Session

cetacean = Session().client( service_name = 'ec2' )

def assert_singular( parentList, resourceType ):

    resourceList = parentList[ resourceType ]

    if 1 != len( resourceList ):
        print( f'ERROR: {resourceType} non-singular' )
        sys.exit( 1 )

    [ resource ] = resourceList

    return( resource )

def print_volume_modification( volmod ):

    modstate = volmod[ 'ModificationState' ]
    original = volmod[ 'OriginalSize' ]
    target   = volmod[ 'TargetSize' ]
    started  = volmod[ 'StartTime' ]
    progress = volmod[ 'Progress' ]
    volumeid = volmod[ 'VolumeId' ]

    ended = 'TBD'
    status = 'TBD'

    if 'EndTime' in volmod:
        ended = volmod[ 'EndTime' ]

    if 'StatusMessage' in volmod:
        status = volmod[ 'StatusMessage' ]

    print()
    print( f'state: {modstate}' )
    print( f'growing {volumeid} from {original} GiB to {target} GiB, progress {progress}%' )
    print( f'started: {started}' )
    print( f'ended:   {ended}' )
    print( f'status: {status}' )

    return( modstate )

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

def pick_resource( tag ):

    rtype = tag[ 'ResourceType' ]
    rid   = tag[ 'ResourceId' ]

    match rtype:

        case 'instance':
            return( root_volume_of_instance( rid ) )

        case 'volume':
            return( rid )

        case _:
            print( f'handler for resource type {rtype} not implemented' )
            sys.exit( 1 )

NameTag = sys.argv[1]
VolSize = sys.argv[2]

response = cetacean.describe_tags( Filters = [ { 'Name': 'tag:Name', 'Values': [ NameTag ] } ] )
vid = pick_resource( assert_singular( response, 'Tags' ) )

print()
print( 'NOTE: After initiating the change, this will block until the change' )
print( 'has completed, stopping once a second to poll for status.' )
print()
print( f'Ready to grow {vid} to {VolSize} GiB...' )

response = input( f'Continue? (y/n): ' )

if 'y' != response:
    sys.exit()

response = cetacean.modify_volume( Size = int( VolSize ), VolumeId = vid )

state = print_volume_modification( response[ 'VolumeModification' ] )

incomplete = ( 'modifying' == state ) or ( 'optimizing' == state )

while incomplete:

    print( '...waiting one second...' )
    time.sleep( 1 )

    response = cetacean.describe_volumes_modifications( VolumeIds = [ vid ] )
    incomplete = False

    for volmod in response[ 'VolumesModifications' ]:

        state = print_volume_modification( volmod )
        incomplete = incomplete or ( 'modifying' == state ) or ( 'optimizing' == state )
