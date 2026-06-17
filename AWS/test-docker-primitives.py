#!/usr/bin/python

import io
import os
import sys
import boto3
import base64
import docker

from json import dumps
from urllib.parse import urlparse
from tarfile import open as opentar, TarInfo

reponame = 'hello-repository'
dockername = 'hello-world'

dockerfile = ''

dockercfg = '''
FROM public.ecr.aws/amazonlinux/amazonlinux:latest
RUN dnf -y update && dnf -y install httpd
RUN echo '<html><head><title>*TAP-TAP*</title></head><body><h1>Testing 1...2...3</h1></body></html>' > /var/www/html/index.html
RUN echo 'mkdir -pv /var/{lock,run}/httpd && /usr/sbin/httpd -D FOREGROUND' >> /root/run_httpd.sh
EXPOSE 80
CMD sh /root/run_httpd.sh
'''

cetacean = boto3.session.Session().client( service_name = 'ecr' )
pier = docker.from_env()
bytestream = io.BytesIO()
encoded_cfg = dockercfg.encode( 'utf-8' )
info = TarInfo( name = 'Dockerfile' )
info.size = len( encoded_cfg )

with opentar( fileobj = bytestream, mode = 'w' ) as tar:
    tar.addfile( info, io.BytesIO( encoded_cfg ) )

bytestream.seek( 0 )

image, logs = pier.images.build( custom_context = True, fileobj = bytestream, tag = dockername )

for log in logs:
    if 'stream' in log:
        print( log[ 'stream' ], end = '' )
    else:
        print( log, file = sys.stderr )

#images = pier.images.list( filters = { 'reference': dockername } )
#
#for image in images:
#    print( image.tags, image.id )

#foo = pier.containers.run( dockername, ports = { '80/tcp': 80 } )

response = cetacean.create_repository( repositoryName = reponame )
url_sans_scheme = response[ 'repository' ][ 'repositoryUri' ]

if not image.tag( repository = url_sans_scheme ):
    print( "ERROR: unsuccessful attempt to tag" )
    sys.exit( 1 )

token = ''
url = urlparse( f'https://{url_sans_scheme}' )
response = cetacean.get_authorization_token()

# it's crude but it gets the job done...
for data in response[ 'authorizationData' ]:
    if f'{url.scheme}://{url.netloc}' == data[ 'proxyEndpoint' ]:
        token = data[ 'authorizationToken' ]

# I also don't like chaining this, without validating intermediate values, but it's fine... :-D
username, password = base64.b64decode( token ).decode( 'utf-8' ).split( sep = ':', maxsplit = 1 )

response = pier.login( username = username, password = password, registry = url.netloc )

print( dumps( response ), file = sys.stderr )

logs = pier.images.push( url_sans_scheme )

print( logs, file = sys.stderr )

#for log in logs:
#    if 'stream' in log:
#        print( log[ 'stream' ], end = '' )
#    else:
#        print( log, file = sys.stderr )

# some cleanup commands to run before running this Python script again:
#aws ecr describe-repositories
#aws ecr delete-repository --repository-name hello-repository
#aws ecr delete-repository --repository-name hello-repository --force
