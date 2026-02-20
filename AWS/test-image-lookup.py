#!/usr/bin/python

import sys
import boto3

#from pprint import pp
from json import dumps

session = boto3.session.Session()
client = session.client( service_name = 'ec2' )

date_prefix = '2026-02'
name_prefix = 'al2023-ami'
owner_alias = 'amazon'

response = client.describe_images(
    Filters = [
        {
            'Name' : 'creation-date',
            'Values' : [ f'{date_prefix}*' ]
        },
        {
            'Name' : 'name',
            'Values' : [ f'{name_prefix}*' ]
        },
        {
            'Name' : 'owner-alias',
            'Values' : [ owner_alias ]
        }
    ],
    IncludeDeprecated = True,
    IncludeDisabled = True
)

for i in response[ 'Images' ]:
    AMI = i[ 'ImageId' ]
    description = i[ 'Description' ]
    name = i[ 'Name' ]
    region = i[ 'SourceImageRegion' ]
    #print( f'region = {region}' )
    print( f'description = {description}' )
    #print( f'name = {name}' )
    #print( f'AMI = {AMI}; name = {name}' )

print( dumps( response[ 'Images' ], default = str ), file = sys.stderr )

#            'Values' : [ 'al2023-ami-2023.7.20250527.1-kernel-6.1-x86_64' ]

# This test looks for Amazon Linux AMIs, but I should write one for
# other distros too (like RHEL and Fedora).

