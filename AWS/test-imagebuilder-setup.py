#!/usr/bin/python

import sys
import boto3

from json import dumps
from amiuniq import UniqueMachineImage

#umi = UniqueMachineImage( '125523088429',
#    architecture = 'x86_64',
#    creation_date = '2026-04-*',
#    name = 'Fedora-Cloud-Base-AmazonEC2.x86_64-43-*' )

umi = UniqueMachineImage( '309956199498',
    architecture = 'x86_64',
    creation_date = '2026-04-*',
    name = 'RHEL-10.*' )

if 1 > umi.size:
    print( "ABORT: no match found" )
    sys.exit( 1 )

if 0 < umi.size:
    print( f'FOUND: {umi.ID}' )

client = boto3.session.Session().client( service_name = 'imagebuilder' )

yaml = '''
name: kernel-tweaking
description: This is where I make tweaks to the boot parameters
schemaVersion: 1.0
phases:
  - name: build
    steps:
      - name: AlterGrubConfig
        action: ExecuteBash
        inputs:
          commands:
            - |
              sed -i '1iserial --speed=115200' /boot/grub2/grub.cfg
              sed -i '1iterminal_input --append serial; terminal_output --append serial' /boot/grub2/grub.cfg
              sed -i '/^set timeout=/s/0/10/' /boot/grub2/grub.cfg
              cat /boot/grub2/grub.cfg
'''

response = client.create_component(
    data = yaml,
    name = 'kernel-tweaking',
    platform = 'Linux',
    semanticVersion = '1.0.0' )

cbva = response[ 'componentBuildVersionArn' ]

print( f'CREATED: {cbva}' )

response = client.create_image_recipe(
    additionalInstanceConfiguration = { 'systemsManagerAgent': { 'uninstallAfterBuild': False } },
    components = [
        { 'componentArn': cbva },
        { 'componentArn': 'arn:aws:imagebuilder:us-east-1:aws:component/amazon-cloudwatch-agent-linux/1.0.1' } ],
    name = 'test',
    parentImage = umi.ID,
    semanticVersion = '2026.05.06' )

ira = response[ 'imageRecipeArn' ]

print( f'CREATED: {ira}' )

response = client.create_infrastructure_configuration(
    instanceProfileName = 'Baseline',
    name = 'test' )

ica = response[ 'infrastructureConfigurationArn' ]

print( f'CREATED: {ica}' )

#response = client.create_image_pipeline(
#    imageRecipeArn = ira,
#    infrastructureConfigurationArn = ica,
#    name = 'test' )
#
#ipa = response[ 'imagePipelineArn' ]
#
#print( ipa )
#
#response = client.start_image_pipeline_execution( imagePipelineArn = ipa )

response = client.create_image(
    imageRecipeArn = ira,
    infrastructureConfigurationArn = ica )

ibva = response[ 'imageBuildVersionArn' ]

print( f'CREATED: {ibva}' )

# Instead of creating a pipeline, we can use create_image(), but then
# it creates an ad-hoc pipeline.

# I think this behavior was caused by a typo:
#
# "At face value, this seems fine, but I suspect it is what is making
# me have to jump through an extra hoop in order to delete a recipe.
# That theory will be borne-out if I encounter no such obstacle when I
# can delete a recipe from the CLI after I delete the pipeline."
