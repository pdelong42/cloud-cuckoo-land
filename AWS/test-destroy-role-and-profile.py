#!/usr/bin/python

import sys
import boto3
import functools

from json import dumps

errout = functools.partial( print, file = sys.stderr )

responses = []
client = boto3.session.Session().client( service_name = 'iam' )

def detach_role_policy( name, ARN ):
    responses.append( client.detach_role_policy( RoleName = name, PolicyArn = ARN ) )
    errout( f"Detached {ARN} from role {name}" )

def remove_role_from_instance_profile( name ):
    responses.append( client.remove_role_from_instance_profile( InstanceProfileName = name, RoleName = name ) )
    errout( f"Removed role {name} from instance profile {name}" )

def delete_instance_profile( name ):
    responses.append( client.delete_instance_profile( InstanceProfileName = name ) )
    errout( f"Deleted instance profile {name}" )

def delete_role( name ):
    responses.append( client.delete_role( RoleName = name ) )
    errout( f"Deleted role {name}" )

def destroy_baseline_role_and_profile( name ):

    response = client.list_attached_role_policies( RoleName = name )

    responses.append( response )

    if response[ 'IsTruncated' ]:
        errout( f"WARNING: IsTruncated set to {response[ 'IsTruncated' ]}" )

    for x in response[ 'AttachedPolicies' ]:
        detach_role_policy( name, x[ 'PolicyArn' ] )

    remove_role_from_instance_profile( name )
    delete_instance_profile( name )
    delete_role( name )

destroy_baseline_role_and_profile( 'Baseline' )

print( dumps( responses, default = str ) )
