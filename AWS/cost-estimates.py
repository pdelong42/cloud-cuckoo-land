#!/usr/bin/python

import sys
import copy

from json import dumps
from boto3 import Session
from time import localtime, mktime, strftime

# for future consideration...
#import datetime

now = localtime()
begin = strftime( '%Y-%m-01', now )
today = strftime( '%Y-%m-%d', now )
tomorrow = strftime( '%Y-%m-%d', localtime( mktime( copy.replace( now, tm_mday = now.tm_mday + 1 ) ) ) )
end = strftime( '%Y-%m-01', localtime( mktime( copy.replace( now, tm_mon = now.tm_mon + 1 ) ) ) )

cetacean = Session().client( service_name = 'ce' )

# I don't really understand why metrics are handled so differently by
# the two API calls below, but I worked around it as best as I could.
#
metric = 'UNBLENDED_COST'
metrics = [ 'UnblendedCost' ]

response = cetacean.get_cost_and_usage(
    Granularity = 'MONTHLY',
    Metrics = metrics,
    TimePeriod = { 'Start': begin, 'End': tomorrow } )

#print( dumps( response, default = str ), file = sys.stderr )

print( f'Costs so-far for this month:' )

for r in response[ 'ResultsByTime' ]:

    for m in metrics:

        total = r[ 'Total' ][ m ]
        amount = float( total[ 'Amount' ] )
        unit = total[ 'Unit' ]

        print( f'\t...for metric "{m}": {amount:#.2f} {unit}' )

if( tomorrow == end ):
    print( f'Cannot forecast remainder of the month because this is the last day.' )
    sys.exit()

response = cetacean.get_cost_forecast(
    Granularity = 'MONTHLY',
    Metric = metric,
    TimePeriod = { 'Start': tomorrow, 'End': end } )

#print( dumps( response, default = str ), file = sys.stderr )

total = response[ 'Total' ]
amount = float( total[ 'Amount' ] )
unit = total[ 'Unit' ]

print( f'Costs forecast for this month:' )
print( f'\t...for metric "{metric}": {amount:#.2f} {unit}' )
