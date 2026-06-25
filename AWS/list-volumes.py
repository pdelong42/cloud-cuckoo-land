#!/usr/bin/python

import sys
import boto3

from tagtable import Instances

filters = []
instanceTable = Instances()
allInstanceIDs = instanceTable.IDs
allInstanceNames = instanceTable.names
instanceIDs = [ allInstanceIDs[ NameTag ] for NameTag in sys.argv if NameTag in allInstanceIDs ]

# this and the logic that uses it is anticipating the
# yet-to-be-written Volume class in the tagtable module
#
allVolumeNames = {}

cetacean = boto3.session.Session().client( service_name = 'ec2' )

if instanceIDs:
    filters = [ { 'Name': 'attachment.instance-id', 'Values': instanceIDs } ]

response = cetacean.describe_volumes( Filters = filters )

for volume in response[ 'Volumes' ]:

    volId = volume[ 'VolumeId' ]
    size = volume[ 'Size' ]
    volType = volume[ 'VolumeType' ]

    if volId in allVolumeNames:
        NameTag = allVolumeNames[ volId ]
        volId += f' NameTag = {NameTag};'

    print( f'ID = {volId}; size = {size} GiB; type = {volType};' )

    for attachment in volume[ 'Attachments' ]:

        device = attachment[ 'Device' ]
        instanceId = attachment[ 'InstanceId' ]
        delOnTerm = attachment[ 'DeleteOnTermination' ]

        if instanceId in allInstanceNames:
            NameTag = allInstanceNames[ instanceId ]
            instanceId += f' NameTag = {NameTag};'

        print( f'\tinstanceId = {instanceId}; device = {device}; delete on termination = {delOnTerm};' )
