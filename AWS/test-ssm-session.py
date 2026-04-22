#!/usr/bin/python

# This assumes that the session-manager-plugin has been installed and
# can be found in a search through PATH.

import os
import sys
import boto3

from json import dumps
from console import ConsoleToInstance
from tagtable import Instances

if 2 != len( sys.argv ):
    print( "ERROR: please provide an instance Name tag as the first (and only) arg" )
    sys.exit()

instanceNameTag = sys.argv.pop()
instanceTable = Instances()
instanceId = instanceTable.IDs[ instanceNameTag ]

session = boto3.session.Session()
region = session.region_name
client = session.client( service_name = 'ssm' )

response = client.start_session( Target = instanceId )

nospaces = (',', ':')
program = 'session-manager-plugin'
payload = dumps( response, separators = nospaces )
target = dumps( { 'Target': instanceId }, separators = nospaces )
URL = f'https://ssm.{region}.amazonaws.com'

os.execlp( program, program, payload, region, 'StartSession', '', target, URL )

# Note:
#
# The profile field is required, but specifying an empty value seems
# to cause it to default to the value of $AWS_PROFILE.  The region
# field is *also* requried, but the session-manager-plugin seems to
# not care what its value is.  And even though it is also used to
# construct the SSM URL, it seems to work no matter what region's URL
# I connect to, so I guess it gets routed properly regardless.
