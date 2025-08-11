#!/usr/bin/python

# First major bug after modularizing this: usage of sys.exit() is
# wildly inappropriate.  ToDo: fix this.

import sys
import tty
import time
import boto3
import atexit
import select
import socket
import termios
import paramiko
import functools

old_attr = termios.tcgetattr( sys.stdin )

def cleanup():
    termios.tcsetattr( sys.stdin, termios.TCSADRAIN, old_attr )

def modeset( fileId ):
    tty.setraw( fileId )
    tty.setcbreak( fileId )

def from_remote_to_local( remote ):

    chars = remote.recv( 1024 ).decode()

    if len( chars ) > 0:
        sys.stdout.write( chars )
        sys.stdout.flush()
    else:
        sys.stdout.write( "\r\n...connection closed.\r\n" )
        sys.exit()

# fix the SSH-style break feature to only happen when prefixed with a newline...
def from_local_to_remote( remote ):

    char = sys.stdin.read( 1 )

    if "~" == char:

        char = sys.stdin.read( 1 )

        if "." == char:
            sys.exit()
        else:
            remote.send( "~" )
            remote.send( char )

    if len( char ) == 0:
        sys.exit()

    remote.send( char )

# This was a quick-and-dirty job of just taking a bunch of
# imperative-style code I wrote earlier, and wrapping it in the
# constructor of an object definition, so that I could pull this in as
# a library from other scripts.  It's probably not the most elegant OO
# code you'll ever see, and I really don't give a rat's ass, because I
# think OO is gross.  If there is a way to do libraries in Python
# without using OO, then I will figure it out or die trying...
#
class ConsoleToInstance:

    def __init__( self, instanceId ):

        # preprint() is for when you don't want to end the line yet...
        # postprint() is for when you're done and want a newline...
        # ...and both have line-buffering disabled, because we're doing
        # terminal emulation.
        #
        preprint  = functools.partial( print, flush = True, end = '' )
        postprint = functools.partial( print, flush = True )

        session = boto3.session.Session()

        client = session.client( service_name='ec2-instance-connect' )
        region = session.region_name

        private_key = paramiko.RSAKey.generate( 3072 )
        public_key = private_key.get_base64()

        preprint( f"Uploading ephemeral public key to instance {instanceId} (ctrl-c to abort)... " )

        while True:
            try:
                # abstract this into a function?
                response = client.send_serial_console_ssh_public_key(
                    InstanceId = instanceId,
                    SSHPublicKey = f"ssh-rsa {public_key} paramiko-generated-key" )
                if True == response['Success']:
                    postprint( " success: continuing..." )
                else:
                    postprint( " ABORT - this should never happen, because an exception should be thrown first" )
                    sys.exit()
                break
            except client.exceptions.SerialConsoleSessionLimitExceededException:
                preprint( "." )
                # footnote 1 #
            except client.exceptions.EC2InstanceTypeInvalidException:
                preprint( "o" )
                # footnote 1 #
            except client.exceptions.EC2InstanceStateInvalidException:
                preprint( "O" )
                # footnote 1 #
            except client.exceptions.EC2InstanceNotFoundException:
                postprint( " ...aborting - instance does not exist in this profile." )

        # yes, I'm recycling a variable here; sloppy? yes - but I'm not using
        # them both at the same time anyway, and I trust Python to GC the old
        # client...
        #
        client = paramiko.SSHClient()

        # Automatically add the server's host key (less secure, for testing purposes only)
        client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        #client.load_system_host_keys()
        # ...not really sure which of those two things is better (but only one is needed)

        port = 0
        userId = f"{instanceId}.port{port}"
        endpoint = f"serial-console.ec2-instance-connect.{region}.aws"

        preprint( f"Connecting to instance {instanceId} (ctrl-c to abort)" )

        # we'll catch specific exceptions as we stumble across them...
        while True:
            try:
                client.connect( hostname = endpoint, username = userId, pkey = private_key )
                break
            # this will often be raised erroneously, masking a more fundamental issue:
            #except paramiko.ssh_exception.PasswordRequiredException:
            finally:
                postprint( " success: press <tilde><dot> to break out of session" )

        channel = client.invoke_shell()

        atexit.register( cleanup );
        modeset( sys.stdin.fileno() )
        channel.settimeout( 0.0 ) # do we *want* this to block indefinitely?

        while True:

            read, write, error = select.select( [channel, sys.stdin], [], [] )

            if channel in read:
                try:
                    from_remote_to_local( channel )
                except socket.timeout:
                    pass
                # I'm not sure we *want* to ignore socket timeouts...

            if sys.stdin in read:
                from_local_to_remote( channel )

# Footnote 1
#
# Yes, it would be more proper of me to insert a sleep() here, so that
# I'm not relentlessly hammering on the endpoint.  But without the
# sleep, it seems to still retry the same number of times, which leads
# me to believe that the artificial delay I had inserted (of a tenth
# of a second) wasn't really doing me any benefit, and that the delays
# that are already baked-in to the function calls I was making were
# getting the job done sufficiently.

# Notes (just the regular kind, no feet involved):

# It really bugs the crap out of me that I've been able to narrow the
# timings on things as much as AWS will let me, but I still can't
# catch those first kernel messages from the bootup process.  And I've
# looked for whether there is a way to inject an artificial delay into
# the bootloader, before it actually loads the kernel (so that the
# machine can be seen as "up" for a short window, while this script
# still has time to set up a serial connection), but I've had no luck
# in that.  So, what you see above was the best I could do.

# I'm still making up my mind whether I want this to become some kind
# of Swiss-Army-Knife-style of program, or if that's just going to
# open a can of worms and make it snowball into bloat territory.  But
# on the other hand, it could be nice to integrate a few common
# functions, like stop, start, create ("run"), destroy ("terminate").
# But anything beyond that, like kicking-off an Automation document
# (assuming that any of the just mentioned operations are part of it),
# might be overkill.
