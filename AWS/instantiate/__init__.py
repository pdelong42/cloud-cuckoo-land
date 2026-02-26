#!/usr/bin/python

import boto3

from tagtable import Instances

class CreateSingleton:

    def __init__( self, nametag, **parameters ):

        self.ID = ''
        self.size = 0
        self.instance = {}
        self.instances = []

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
            print( f'WARNING: too many instances ({self.size}) were created - only returning first one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

class DestroySingleton:

    def __init__( self, NameTag ):

        self.ID = ''
        self.size = 0
        self.instance = {}
        self.instances = []

        instanceTable = Instances()
        instanceId = instanceTable.IDs[ NameTag ]

        client = boto3.session.Session().client( service_name = 'ec2' )

        response = client.terminate_instances( InstanceIds = [ instanceId ] )

        #print( dumps( response, default = str ) )

        self.instances = response[ 'TerminatingInstances' ]
        self.size      = len( self.instances )

        if self.size < 1:
            print( 'ERROR: no instances were successfully destroyed' )
            return

        if self.size > 1:
            print( f'WARNING: too many instances ({self.size}) were destroyed - only returning first one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

        response = client.delete_tags( Resources = [ instanceId ] )

# other parameters to consider passing...
#    SubnetId='',
#    InstanceType='t3.large',
#    MetadataOptions='HttpTokens=required,InstanceMetadataTags=enabled'
