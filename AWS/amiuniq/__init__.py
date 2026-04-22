#!/usr/bin/python

import boto3

class UniqueMachineImage:

    def __init__( self, parameters ):

        filters = []

        for k in parameters.keys():
            v = parameters[ k ]
            f = { 'Name': k, 'Values': [ v ] }
            filters.append( f )

        self.ID = ''
        self.name = ''
        self.image = {}
        self.images = []
        self.size = 0

        client = boto3.session.Session().client( service_name = 'ec2' )

        response = client.describe_images( Filters = filters )

        self.images = response[ 'Images' ]
        self.size = len( self.images )

        if self.size < 1:
            print( 'ERROR: no results from unique AMI search (filter too narrow?)' )
            return

        if self.size > 1:
            print( f'WARNING: too many results ({self.size}) from unique AMI search (filter too broad?) - only returning top one' )

        self.image = self.images.pop()
        self.ID    = self.image[ 'ImageId' ]
        self.name  = self.image[ 'Name' ]
