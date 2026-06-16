#!/usr/bin/python

import io
import os
import sys
import docker
import tarfile

dockerfile = ''
dockerpath = './Dockerfile'

dockercfg = '''
FROM public.ecr.aws/amazonlinux/amazonlinux:latest
RUN dnf -y update && dnf -y install httpd
RUN echo '<html><head><title>*TAP-TAP*</title></head><body><h1>Testing 1...2...3</h1></body></html>' > /var/www/html/index.html
RUN echo 'mkdir -pv /var/{lock,run}/httpd && /usr/sbin/httpd -D FOREGROUND' >> /root/run_httpd.sh
EXPOSE 80
CMD sh /root/run_httpd.sh
'''

client = docker.from_env()
bytestream = io.BytesIO()
encoded_cfg = dockercfg.encode( 'utf-8' )
info = tarfile.TarInfo( name = 'Dockerfile' )
info.size = len( encoded_cfg )

with tarfile.open( fileobj = bytestream, mode = 'w' ) as tar:
    tar.addfile( info, io.BytesIO( encoded_cfg ) )

bytestream.seek( 0 )

image, logs = client.images.build( custom_context = True, fileobj = bytestream, tag = 'hello-world' )

for log in logs:
    if 'stream' in log:
        print( log[ 'stream' ], end = '' )
    else:
        print( log, file = sys.stderr )
