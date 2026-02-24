#!/usr/bin/python

import sys
import boto3

from json import dumps
from amiuniq import UniqueMachineImage

#umi = UniqueMachineImage( {
#    'architecture': 'x86_64',
#    'creation-date': '2026-01-*',
#    'name': 'RHEL-*',
#    'owner-id': '309956199498'
#} )

umi = UniqueMachineImage( {
    'architecture': 'arm64',
    'creation-date': '2026-01-22T*',
    'name': 'al2023-ami-minimal-2023.10.*-kernel-6.12-*',
    'owner-id': '137112412989'
} )

if 1 > umi.size:
    print( "ABORT: no match found" )
    sys.exit( 1 )

if 0 < umi.size:
    print( umi.ID )

if not 1 < umi.size:
    sys.exit( 0 )

print( dumps( umi.images, default = str ), file = sys.stderr )

print( "extra matches..." )

for i in umi.images:
    AMI = i[ 'ImageId' ]
    name = i[ 'Name' ]
    print( f'name = {name}' )
    #print( f'AMI = {AMI}; name = {name}' )

#            'Values' : [ 'al2023-ami-2023.7.20250527.1-kernel-6.1-x86_64' ]
