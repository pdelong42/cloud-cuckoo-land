#!/usr/bin/python

import sys
import boto3

class Instances:

    # ...where our hero actually decides to use some OO design
    # principles...  like, just barely (compare and contrast with the
    # console implementation, which is basically just an imperative
    # wolf in grandma-OO's clothing).

    def __init__( self ):

        self.IDs   = {}
        self.names = {}

        client = boto3.session.Session().client( service_name = 'ec2' )
        response = client.describe_instances()
        reservations = response[ 'Reservations' ]
        instances = [ reservation[ 'Instances' ][0] for reservation in reservations ]

        for i in instances:

            if not 'Tags' in i: continue

            tags = { t[ 'Key' ]: t[ 'Value' ] for t in i[ 'Tags' ] }

            self.names[ i[ 'InstanceId' ] ] = tags[ 'Name' ]
            self.IDs[ tags[ 'Name' ] ] = i[ 'InstanceId' ]

            # We can build on this by adding other tags, so that one
            # can index an "owners" array by ID, for example.
            #
            # But don't expect the converse to ever be something we
            # can do; i.e., we can't index another IDs array by owner,
            # mostly because it's not unique, but also because that
            # gets more complicated than is worthwhile (yeah, you
            # could return an array of IDs owned by that principal,
            # but why...).
            #
            # Besides, we're already skating on thin-ice by assuming
            # that the Name tag is unique enough to use for a
            # "reverse-lookup" (I guess we don't *have* to assume it's
            # unique, if we use that array-of-IDs idea here too; but
            # again, why...)

