#!/usr/bin/python

import sys
import boto3

from json import dumps

session = boto3.session.Session()

client = session.client( service_name = 'ec2' )

response = client.describe_images( Owners = [ 'self' ] )

for i in response[ 'Images' ]:

    arn = i[ 'ImageId' ]
    response = client.deregister_image( ImageId = arn )

    if response[ 'Return' ]:
        print( f'DELETED: {arn}' )
    else:
        print( f'ABORTED: failed to delete {arn}' )
        sys.exit()

client = session.client( service_name = 'imagebuilder' )

response = client.list_images()

for i in response[ 'imageVersionList' ]:

    arn = i[ 'arn' ]

    print( f'FOUND: {arn}' )

response = client.list_image_build_versions()

for i in response[ 'imageSummaryList' ]:

    arn = i[ 'arn' ]
    response = client.delete_image( imageBuildVersionArn = arn )

    print( f'DELETED: {arn}' )

response = client.list_infrastructure_configurations()

for i in response[ 'infrastructureConfigurationSummaryList' ]:

    arn = i[ 'arn' ]
    response = client.delete_infrastructure_configuration( infrastructureConfigurationArn = arn )

    print( f'DELETED: {arn}' )

response = client.list_image_recipes()

for i in response[ 'imageRecipeSummaryList' ]:

    arn = i[ 'arn' ]
    response = client.delete_image_recipe( imageRecipeArn = arn )

    print( f'DELETED: {arn}' )
