#!/usr/bin/python

import boto3

from tagtable import Instances

def TransitionNotice( x ):

    iid = x[ 'InstanceId' ]
    prev = x[ 'PreviousState' ][ 'Name' ]
    curr = x[  'CurrentState' ][ 'Name' ]

    print( f'\nTransitioning instance {iid} from {prev} to {curr}' )

class Singleton:

    def __init__( self, NameTag ):

        instanceTable = Instances()

        self.ID = ''
        self.size = 0
        self.nametag = NameTag
        self.instance = {}
        self.instances = []
        self.client = boto3.session.Session().client( service_name = 'ec2' )

        if NameTag in instanceTable.IDs:
            self.ID = instanceTable.IDs[ NameTag ]

    def create( self, **parameters ):

        if self.ID:
            print( f'ERROR: instance with Name tag {self.nametag} already exists, aborting' )
            return

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
                            'Value': self.nametag } ] } ] } )

        response = self.client.run_instances( **parameters )

        self.instances = response[ 'Instances' ]
        self.size      = len( self.instances )

        if self.size < 1:
            print( 'ERROR: no instances were successfully created' )
            return

        if self.size > 1:
            print( f'WARNING: too many instances ({self.size}) were created - only returning first one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

        print( f'Created instance {self.ID}' )

    def destroy( self ):

        response = self.client.terminate_instances( InstanceIds = [ self.ID ] )

        self.instances = response[ 'TerminatingInstances' ]
        self.size      = len( self.instances )

        if self.size < 1:
            print( 'ERROR: no instances were successfully destroyed' )
            return

        if self.size > 1:
            print( f'WARNING: too many instances ({self.size}) were destroyed - only returning first one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

        TransitionNotice( self.instance )

        response = self.client.delete_tags( Resources = [ self.ID ] )

    def start( self ):

        response = self.client.start_instances( InstanceIds = [ self.ID ] )

        self.instances = response[ 'StartingInstances' ]
        self.size      = len( self.instances )

        if self.size < 1:
            print( 'ERROR: no instances were successfully started' )
            return

        if self.size > 1:
            print( f'WARNING: too many instances ({self.size}) were started - only returning first one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

        TransitionNotice( self.instance )

    def stop( self ):

        response = self.client.stop_instances( InstanceIds = [ self.ID ] )

        self.instances = response[ 'StoppingInstances' ]
        self.size      = len( self.instances )

        if self.size < 1:
            print( 'ERROR: no instances were successfully stopped' )
            return

        if self.size > 1:
            print( f'WARNING: too many instances ({self.size}) were stopped - only returning first one' )

        self.instance = self.instances.pop()
        self.ID       = self.instance[ 'InstanceId' ]

        TransitionNotice( self.instance )
