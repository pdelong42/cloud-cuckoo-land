#!/usr/bin/python

import sys

from boto3 import Session
from tagtable import Instances, Volumes

instanceTable = Instances()
allInstanceIDs = instanceTable.IDs
allInstanceNames = instanceTable.names

volumeTable = Volumes()
allVolumeIDs = volumeTable.IDs
allVolumeNames = volumeTable.names

cetacean = Session().client( service_name = 'ec2' )

response = cetacean.describe_volumes()

for volume in response[ 'Volumes' ]:

    volId = volume[ 'VolumeId' ]
    size = volume[ 'Size' ]
    volType = volume[ 'VolumeType' ]

    if volId in allVolumeNames:
        NameTag = allVolumeNames[ volId ]
        volId += f' (NameTag = {NameTag})'

    print( f'volumeId = {volId}; size = {size} GiB; type = {volType};' )

    for attachment in volume[ 'Attachments' ]:

        device = attachment[ 'Device' ] # footnote 1 #
        instanceId = attachment[ 'InstanceId' ]
        delOnTerm = attachment[ 'DeleteOnTermination' ]

        if instanceId in allInstanceNames:
            NameTag = allInstanceNames[ instanceId ]
            instanceId += f' (NameTag = {NameTag})'

        print( f'\tinstanceId = {instanceId}; device = {device}; delete on termination = {delOnTerm};' )

# Footnote 1:
#
# I'm honestly not sure why I bother printing this field, as it hardly
# serves any useful purpose.  It corresponds to what AWS thinks the
# guest OS calls the block device, but the actual naming scheme used
# in the OS is not the same (for either Amazon Linux or for RHEL).  I
# suppose it has marginal value as some sort of relative positional
# indicator, so I'm hesitant to compleletly drop it.  But I will drop
# it if I decide that value isn't outweighed by how misleading this
# is.
