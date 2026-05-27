#!/usr/bin/python

from boto3 import Session
from tagtable import VPCs, Subnets

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

class Subnet:

    def __init__( self, NameTag ):

        subnetTable = Subnets()

        self.ID = ''
        self.Subnet = {}
        self.nametag = NameTag
        self.client = Session().client( service_name = 'ec2' )

        if NameTag in subnetTable.IDs:
            self.ID = subnetTable.IDs[ NameTag ]

    def create( self, **parameters ):

        if self.ID:
            print( f'ERROR: instance with Name tag {self.nametag} already exists - aborting' )
            return

        vpcTable = VPCs()
        vpcName = parameters.pop( 'VpcName' )

        if vpcName not in vpcTable.IDs:
            print( f'ERROR: VPC named {vpcName} not found - aborting' )
            return

        vpcId = vpcTable.IDs[ vpcName ]

        parameters.update( {
            'TagSpecifications': [
                {   'ResourceType': 'subnet',
                    'Tags': [
                        {   'Key': 'Name',
                            'Value': self.nametag } ] } ],
            'VpcId': vpcId } )

        response = self.client.create_subnet( **parameters )

        self.Subnet = response[ 'Subnet' ]
        self.ID     = self.Subnet[ 'SubnetId' ]

        print( f'Created subnet {self.ID}' )

    def destroy( self ):

        response = self.client.delete_subnet( SubnetId = self.ID )
