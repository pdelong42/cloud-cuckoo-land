#!/usr/bin/python

import sys
import boto3
import functools

from json import dumps

errout = functools.partial( print, file = sys.stderr )

trust_policy = {
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

class InstanceProfileRole:

    def __init__( self ):

        self.client = boto3.session.Session().client( service_name = 'iam' )

    def create( self, name, desc, *policies ):

        responses = []

        response = self.client.create_role(
            AssumeRolePolicyDocument = dumps( trust_policy ),
            Description = desc,
            RoleName = name )

        errout( f"Created role {name}" )

        responses.append( response )

        response = self.client.create_instance_profile(
            InstanceProfileName = name )

        errout( f"Created instance profile {name}" )

        responses.append( response )

        response = self.client.add_role_to_instance_profile(
            InstanceProfileName = name,
            RoleName = name )

        responses.append( response )

        errout( f"Added role {name} to instance profile {name}" )

        ARNs = list( policies )
        ARNs.append( 'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore' )
        ARNs.append( 'arn:aws:iam::aws:policy/AmazonSSMPatchAssociation' )
        ARNs.append( 'arn:aws:iam::aws:policy/AWSImageBuilderReadOnlyAccess' )
        ARNs.append( 'arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy' )

        for ARN in ARNs:

            response = self.client.attach_role_policy(
                PolicyArn = ARN,
                RoleName = name )

            responses.append( response )

            errout( f"Attached {ARN} to role {name}" )

        return( responses )

    def destroy( self, name ):

        responses = []

        response = self.client.list_attached_role_policies( RoleName = name )

        responses.append( response )

        if response[ 'IsTruncated' ]:
            errout( f"WARNING: IsTruncated set to {response[ 'IsTruncated' ]}" )

        for x in response[ 'AttachedPolicies' ]:

            ARN = x[ 'PolicyArn' ]

            response = self.client.detach_role_policy(
                PolicyArn = ARN,
                RoleName = name,
            )

            responses.append( response )

            errout( f"Detached {ARN} from role {name}" )

        response = self.client.remove_role_from_instance_profile(
            InstanceProfileName = name,
            RoleName = name )

        responses.append( response )

        errout( f"Removed role {name} from instance profile {name}" )

        response = self.client.delete_instance_profile(
            InstanceProfileName = name )

        responses.append( response )

        errout( f"Deleted instance profile {name}" )

        response = self.client.delete_role( RoleName = name )

        responses.append( response )

        errout( f"Deleted role {name}" )

        return( responses )
