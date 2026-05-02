#!/usr/bin/python

import sys
import boto3

from json import dumps

def printARNs( x, r ):
    for i in r[ x ]:
        arn = i[ 'arn' ]
        print( f'FOUND: {arn}' )

session = boto3.session.Session()

client = session.client( service_name = 'imagebuilder' )

printARNs( 'infrastructureConfigurationSummaryList', client.list_infrastructure_configurations() )
printARNs(                 'imageRecipeSummaryList', client.list_image_recipes() )
printARNs(                       'imageSummaryList', client.list_image_build_versions() )
printARNs(                       'imageVersionList', client.list_images() )

client = session.client( service_name = 'ec2' )

response = client.describe_images( Owners = [ 'self' ] )

for i in response[ 'Images' ]:
    arn = i[ 'ImageId' ]
    print( f'FOUND: {arn}' )
