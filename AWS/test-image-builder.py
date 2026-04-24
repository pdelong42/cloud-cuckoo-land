#!/usr/bin/python

import sys
import boto3

from json import dumps
from amiuniq import UniqueMachineImage

#umi = UniqueMachineImage( {
#    'architecture': 'x86_64',
#    'creation-date': '2026-02-*',
#    'name': 'Fedora-Cloud-Base-AmazonEC2.x86_64-43-*',
#    'owner-id': '125523088429'
#} )

umi = UniqueMachineImage( {
    'architecture': 'x86_64',
    'creation-date': '2026-02-*',
    'name': 'RHEL-10.*',
    'owner-id': '309956199498'
} )

if 1 > umi.size:
    print( "ABORT: no match found" )
    sys.exit( 1 )

if 0 < umi.size:
    print( f'found {umi.ID}' )

client = boto3.session.Session().client( service_name = 'imagebuilder' )

response = client.create_image_recipe(
    name = 'test',
    parentImage = umi.ID,
    semanticVersion = '2026.03.22' )

ira = response[ 'imageRecipeArn' ]

print( ira )

response = client.create_infrastructure_configuration(
    instanceProfileName = 'Baseline',
    name = 'test' )

ica = response[ 'infrastructureConfigurationArn' ]

print( ica )

response = client.create_image_pipeline(
    imageRecipeArn = ira,
    infrastructureConfigurationArn = ica,
    name = 'test' )

ipa = response[ 'imagePipelineArn' ]

print( ipa )

response = client.start_image_pipeline_execution( imagePipelineArn = ipa )

ibva = response[ 'imageBuildVersionArn' ]

print( ibva )

# Instead of creating a pipeline, we can use create_image(), but then
# it creates an ad-hoc pipeline.  At face value, this seems fine, but
# I suspect it is what is making me have to jump through an extra hoop
# in order to delete a recipe.  That theory will be borne-out if I
# encounter no such obstacle when I can delete a recipe from the CLI
# after I delete the pipeline.
