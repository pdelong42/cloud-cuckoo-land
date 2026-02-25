#!/usr/bin/python

import boto3

class CreateSingleton:

    def __init__( self, nametag, **parameters ):

        # MaxCount and MinCount are both required, and I need to
        # specify them anyway, since this object is meant to only
        # create a single instance.
        #
        # Also adding the Name tag.
        #
        parameters.update( {
            'MaxCount': 1,
            'MinCount': 1,
            'TagSpecifications': [
                {   'ResourceType': 'instance',
                    'Tags': [
                        {   'Key': 'Name',
                            'Value': nametag } ] } ] } )

        client = boto3.session.Session().client( service_name = 'ec2' )

        response = client.run_instances( **parameters )

        self.instances = response[ 'Instances' ]
        self.size      = len( self.instances )

        if self.size < 1:
            print( 'ERROR: no instances were successfully created' )
            return

        if self.size > 1:
            print( f'WARNING: too many instances ({self.size}) were created - only returning top one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

# other parameters to consider passing...
#    SubnetId='',
#    InstanceType='t3.large',
#    MetadataOptions='HttpTokens=required,InstanceMetadataTags=enabled'
