#!/usr/bin/python

from boto3 import Session
from tagtable import VPCs

class VPC:

    def __init__( self, NameTag ):

        vpcTable = VPCs()

        self.ID = ''
        self.VPC = {}
        self.nametag = NameTag
        self.client = Session().client( service_name = 'ec2' )

        if NameTag in vpcTable.IDs:
            self.ID = vpcTable.IDs[ NameTag ]

    def create( self, **parameters ):

        if self.ID:
            print( f'ERROR: instance with Name tag {self.nametag} already exists, aborting' )
            return

        parameters.update( {
            'TagSpecifications': [
                {   'ResourceType': 'vpc',
                    'Tags': [
                        {   'Key': 'Name',
                            'Value': self.nametag } ] } ] } )

        response = self.client.create_vpc( **parameters )

        self.VPC = response[ 'Vpc' ]
        self.ID  = self.VPC[ 'VpcId' ]

        print( f'Created VPC {self.ID}' )

    def destroy( self ):

        response = self.client.delete_vpc( VpcId = self.ID )
