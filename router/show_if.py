#!/usr/bin/env python

import os, sys, re, time
import subprocess
import json

class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'


mark = chr(167)
regexp = re.compile(r'[^\x20-\x7E\n]')



def roundstr(size):
    return str(round(size, 1))

def fix_size(originsize):
    if originsize < 1024:
        return str(originsize)
    elif originsize < 1024 ** 2:
        return roundstr(originsize / 1024.0) + ' K'
    elif originsize < 1024 ** 3:
        return roundstr(originsize / (1024.0 ** 2)) + ' M'
    elif originsize < 1024 ** 4:
        return roundstr(originsize / (1024.0 ** 3)) + ' G'
    elif originsize < 1024 ** 5:
        return roundstr(originsize / (1024.0 ** 4)) + ' T'
    else:
        return str(originsize)


def view_stats(stats, prv_stats):

    os.system('clear')
    ifs = stats['data'].keys()
    print '================================================================================================================================================'
    print '                         bps  |    unicast(p/s)  |  broadcast(p/s)  |  multicast(p/s)  |   discards(p/s)  |     errors(p/s)  |    unknown(p/s)'
    print '------------------------------+------------------+------------------+------------------+------------------+------------------+------------------'
    for idx in ifs:
        in_stat   = '{:6s}'.format(idx)
        out_stat  = '      '
        counters = stats['data'][idx]['state']['counters']
        prv_counters = prv_stats['data'][idx]['state']['counters']
        in_stat  += ' [IN]  ' 
        in_stat  += '{:>16s}'.format( fix_size( 8 * ( counters['in-octets'] - prv_counters['in-octets'] ) ) )
        in_stat  += ' | ' + '{:>16s}'.format( fix_size( counters['in-unicast-pkts'] - prv_counters['in-unicast-pkts']) )
        in_stat  += ' | ' + '{:>16s}'.format( fix_size( counters['in-broadcast-pkts'] - prv_counters['in-broadcast-pkts']) )
        in_stat  += ' | ' + '{:>16s}'.format( fix_size( counters['in-multicast-pkts'] - prv_counters['in-multicast-pkts']) )
        in_stat  += ' | ' + '{:>16s}'.format( fix_size( counters['in-discards'] - prv_counters['in-discards']) )
        in_stat  += ' | ' + '{:>16s}'.format( fix_size( counters['in-errors'] - prv_counters['in-errors']) )
        in_stat  += ' | ' + '{:>16s}'.format( fix_size( counters['in-unknown-protos'] - prv_counters['in-unknown-protos']) )
        out_stat += ' [OUT] '
        out_stat += '{:>16s}'.format( fix_size( 8 * ( counters['out-octets'] - prv_counters['out-octets'] ) ) )
        out_stat += ' | ' + '{:>16s}'.format( fix_size( counters['out-unicast-pkts'] - prv_counters['out-unicast-pkts']) )
        out_stat += ' | ' + '{:>16s}'.format( fix_size( counters['out-broadcast-pkts'] - prv_counters['out-broadcast-pkts']) )
        out_stat += ' | ' + '{:>16s}'.format( fix_size( counters['out-multicast-pkts'] - prv_counters['out-multicast-pkts']) )
        out_stat += ' | ' + '{:>16s}'.format( fix_size( counters['out-discards'] - prv_counters['out-discards']) )
        out_stat += ' | ' + '{:>16s}'.format( fix_size( counters['out-errors'] - prv_counters['out-errors']) )
        print in_stat
        print out_stat
        print '------------------------------+------------------+------------------+------------------+------------------+------------------+------------------'
        '''
        if 'subinterfaces' in stats['data'][idx]:
            subifs = stats['data'][idx]['subinterfaces'].keys()
            for sidx in subifs:
                print sidx
                print stats['data'][idx]['subinterfaces'][sidx]['state']['counters']
        print '-----------------------------------------'
        '''




if __name__ == "__main__":
    
    prv_stats = json.loads(subprocess.check_output(['./get_if_stats.sh', 'interfaces']))
    time.sleep(1)

    ifs = prv_stats['data'].keys()

    while True:
        
        stats = json.loads(subprocess.check_output(['./get_if_stats.sh', 'interfaces']))

        view_stats(stats, prv_stats)
    
        time.sleep(1)

        prv_stats = stats
    

