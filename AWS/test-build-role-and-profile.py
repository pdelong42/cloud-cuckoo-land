#!/usr/bin/python

import sys
import boto3
import functools

from json import dumps

errout = functools.partial( print, file = sys.stderr )

assume = {
    'Statement': [
        {
            'Action': 'sts:AssumeRole',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'ec2.amazonaws.com'
            }
        }
    ],
    'Version': '2012-10-17'
}

responses = []
client = boto3.session.Session().client( service_name = 'iam' )

def create_role( name, desc ):
    responses.append( client.create_role( RoleName = name, AssumeRolePolicyDocument = dumps( assume ), Description = desc ) )
    errout( f"Created role {name}" )

def create_instance_profile( name ):
    responses.append( client.create_instance_profile( InstanceProfileName = name ) )
    errout( f"Created instance profile {name}" )

def add_role_to_instance_profile( name ):
    responses.append( client.add_role_to_instance_profile( InstanceProfileName = name, RoleName = name ) )
    errout( f"Added role {name} to instance profile {name}" )

def attach_role_policy( name, ARN ):
    responses.append( client.attach_role_policy( RoleName = name, PolicyArn = ARN ) )
    errout( f"Attached {ARN} to role {name}" )

def build_baseline_role_and_profile( name ):
    create_role( name, 'minmal set of permissions that should be associated with any instance in our environment' )
    create_instance_profile( name )
    add_role_to_instance_profile( name )
    attach_role_policy( name, 'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore' )
    attach_role_policy( name, 'arn:aws:iam::aws:policy/AmazonSSMPatchAssociation' )
    attach_role_policy( name, 'arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy' )

build_baseline_role_and_profile( 'Baseline' )

print( dumps( responses, default = str ) )
