#!/usr/bin/python

import boto3

#from json import dumps
from crypt import crypt
from getpass import getpass
from threading import Thread
from console import ConsoleToInstance
from amiuniq import UniqueMachineImage
from instantiate import CreateSingleton

username = 'somebody'
passhash = crypt( getpass( f'Choose a password to use for the user named \'{username}\': ' ) )

UMI = UniqueMachineImage( {
    'architecture': 'x86_64',
    'creation-date': '2026-01-22T*',
    'name': 'al2023-ami-minimal-2023.10.*-kernel-6.12-*',
    'owner-id': '137112412989' } )

# ImageID is required
#
uno = CreateSingleton(
    'soup2nuts',
    IamInstanceProfile = {'Name':'Baseline'},
    ImageId = UMI.ID,
    UserData = f'#!/bin/bash\n\nuseradd -g wheel -p \'{passhash}\' {username}'
)

print( f'Created instance {uno.ID}' )

console_thread = Thread( target = ConsoleToInstance, args = [ uno.ID ] )

console_thread.start()
