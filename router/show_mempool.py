#!/usr/bin/env python

import os, sys, re, time
import thread
import subprocess
import telnetlib

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
read_string = mark + " "
regexp = re.compile(r'[^\x20-\x7E\n]')

view_mode = 0

def get_stats(log):
    stats = []
    for mps in log.replace(' ', '').split('mempool')[1:]:
        vals = mps.split('\n')
        mp = {}
        mp['name']              = vals[0]
        mp['flags']             = vals[1][6:]
        mp['pool']              = vals[2][5:]
        mp['iova']              = vals[3][5:]
        mp['nb_mem_chunks']     = vals[4][14:]
        mp['size']              = vals[5][5:]
        mp['populated_size']    = vals[6][15:]
        mp['header_size']       = vals[7][12:]
        mp['elt_size']          = vals[8][9:]
        mp['trailer_size']      = vals[9][13:]
        mp['total_obj_size']    = vals[10][15:]
        mp['private_data_size'] = vals[11][18:]
        mp['avgbytes/object']   = vals[12][16:]
        mp['cache_size']        = vals[14][11:]
        mp['cache_count']       = [vals[15+i].split('=')[1].split('c')[0] for i in range(128)]
        mp['total_cache_count'] = vals[14+128+1][18:]
        mp['common_pool_count'] = vals[14+128+2][18:]
        stats.append(mp)
        stats = sorted(stats, key=lambda x:x['name'])
    return stats


def get_log(tn):
    tn.write("show mempool\n")
    result = tn.read_until(read_string)
    tn_data = regexp.sub("", result)
    return tn_data



def view_stats(stats, prv_stats):
    r_stats = 16
    r_cell = 3
    c_cell = len(stats) // r_cell if len(stats) % r_cell == 0 else len(stats) // r_cell + 1
    bg = []
    for i in range(r_stats*r_cell):
        b = list("| ")
        bg.append(b)
    for i,s in enumerate(stats):
        r_off = r_cell * (i // r_cell)
        c_off = 40 * (i // r_cell)
        id_update = "      "
        str_plus = "+"
        str_minus = "-"
        str_bar = "|"
        str_equal = "="
        if prv_stats == []:
            pass
        else:
            if s != prv_stats[i]:
                id_update = "UPDATE"
                str_equal = "E"
                str_minus = "X"
                str_bar   = "B"
                str_plus  = "Z"
        num_bar = int(30 * float(s['total_cache_count']) / float(s['populated_size']))
        bar = ['*']*30
        if 1 <= num_bar and num_bar < 15:
            bar[0:num_bar] = ['G']*num_bar
        elif 15 <= num_bar and num_bar < 30:
            bar[0:num_bar] = ['Y']*num_bar
        elif 30 <= num_bar:
            bar[0:num_bar] = ['R']*num_bar
        else:
            bar[0:num_bar] = ['D']*num_bar
        bg[r_stats*(i-r_off)+0][0+c_off:40+c_off] =  list(str_plus + str_equal*38 + str_plus)
        bg[r_stats*(i-r_off)+1][0+c_off:40+c_off] =  list(str_bar + " " + s['name'].ljust(36) + " " + str_bar)
        bg[r_stats*(i-r_off)+2][0+c_off:40+c_off] =  list(str_plus + str_minus*38 + str_plus)
        bg[r_stats*(i-r_off)+3][0+c_off:40+c_off] =  list(str_bar + " " + ("size              : " + s['size']).ljust(36)              + " " + str_bar)
        bg[r_stats*(i-r_off)+4][0+c_off:40+c_off] =  list(str_bar + " " + ("populated_size    : " + s['populated_size']).ljust(36)    + " " + str_bar)
        bg[r_stats*(i-r_off)+5][0+c_off:40+c_off] =  list(str_bar + " " + ("header_size       : " + s['header_size']).ljust(36)       + " " + str_bar)
        bg[r_stats*(i-r_off)+6][0+c_off:40+c_off] =  list(str_bar + " " + ("elt_size          : " + s['elt_size']).ljust(36)          + " " + str_bar)
        bg[r_stats*(i-r_off)+7][0+c_off:40+c_off] =  list(str_bar + " " + ("trailer_size      : " + s['trailer_size']).ljust(36)      + " " + str_bar)
        bg[r_stats*(i-r_off)+8][0+c_off:40+c_off] =  list(str_bar + " " + ("total_obj_size    : " + s['total_obj_size']).ljust(36)    + " " + str_bar)
        bg[r_stats*(i-r_off)+9][0+c_off:40+c_off] =  list(str_bar + " " + ("private_data_size : " + s['private_data_size']).ljust(36) + " " + str_bar)
        bg[r_stats*(i-r_off)+10][0+c_off:40+c_off] = list(str_bar + " " + ("avgbytes/object   : " + s['avgbytes/object']).ljust(36)   + " " + str_bar)
        bg[r_stats*(i-r_off)+11][0+c_off:40+c_off] = list(str_bar + " " + ("cache_size        : " + s['cache_size']).ljust(36)        + " " + str_bar)
        bg[r_stats*(i-r_off)+12][0+c_off:40+c_off] = list(str_bar + " " + ("total_cache_count : " + s['total_cache_count']).ljust(36) + " " + str_bar)
        bg[r_stats*(i-r_off)+13][0+c_off:40+c_off] = list(str_bar + " " + ("common_pool_count : " + s['common_pool_count']).ljust(36) + " " + str_bar)
        bg[r_stats*(i-r_off)+14][0+c_off:40+c_off] = list(str_bar + " ring: " + ''.join(bar) + " " + str_bar)
        
        bg[r_stats*(i-r_off)+15][0+c_off:40+c_off] = list(str_plus + str_equal*38 + str_plus)
    os.system('clear')
    print "[0]: NORMAL STATS VIEW | [1]: INTERNAL CHACHE INFO | now: " + str(view_mode)
    print
    for i in range(r_stats*r_cell):
        #print ''.join(bg[i])
        line = ''.join(bg[i])
        line = re.sub(r'(UPDATE)', r"\033[36m\1\033[0m", line)
        line = re.sub(r'(G+)', r"\033[32m\1\033[0m", line)
        line = re.sub(r'G', r"D", line)
        line = re.sub(r'(Y+)', r"\033[33m\1\033[0m", line)
        line = re.sub(r'Y', r"D", line)
        line = re.sub(r'(R+)', r"\033[31m\1\033[0m", line)
        line = re.sub(r'R', r"D", line)
        line = re.sub(r'(E+)', r"\033[35m\1\033[0m", line)
        line = re.sub(r'E', r"=", line)
        line = re.sub(r'(X+)', r"\033[35m\1\033[0m", line)
        line = re.sub(r'X', r"-", line)
        line = re.sub(r'(B+)', r"\033[35m\1\033[0m", line)
        line = re.sub(r'B', r"|", line)
        line = re.sub(r'(Z+)', r"\033[35m\1\033[0m", line)
        line = re.sub(r'Z', r"+", line)
        print line


def view_cache(stats, prv_stats):
    cache_size = float(stats[0]['cache_size'])
    nb_core = 40
    core_info = [""]*nb_core
    core_info[22] = "ethdev.rx_core"
    core_info[23] = "ethdev.tx_core"
    core_info[24] = "bridge.core"
    core_info[25] = "rif.core"
    core_info[26] = "router.core"
    core_info[27] = "tunnel.inbound_core"
    core_info[28] = "tunnel.outbound.core"
    core_load = []
    mpstats = subprocess.check_output(['mpstat', '-P', 'ALL'])
    for line in mpstats.split('\n')[4:-1]:
        load = float(line.split()[3])
        core_load.append(load)
    num_load = int(20 * load / 100) if load <= 100 else 20
    cpu_bar = ['*']*20
    if 1 <= num_load and num_load < 10:
        cpu_bar[0:num_laad] = ['G']*num_load
    elif 10 <= num_load and num_load < 20:
        cpu_bar[0:num_load] = ['Y']*num_load
    elif 20 <= num_load:
        cpu_bar[0:num_load] = ['R']*num_load
    else:
        cpu_bar[0:num_load] = ['D']*num_load
    bg = []
    for i in range(nb_core):
        b = list("| ")
        bg.append(b)
    for i,s in enumerate(stats[0]['cache_count']):
        if nb_core <= i:
            break
        str_start = " "
        str_end = " "
        if prv_stats == []:
            pass
        else:
            if s != prv_stats[0]['cache_count'][i]:
                str_start = "S"
                str_end   = "E"
        num_bar = int(30 * float(s) / cache_size) if int(s) <= cache_size else 30
        bar = ['*']*30
        if 1 <= num_bar and num_bar < 15:
            bar[0:num_bar] = ['G']*num_bar
        elif 15 <= num_bar and num_bar < 30:
            bar[0:num_bar] = ['Y']*num_bar
        elif 30 <= num_bar:
            bar[0:num_bar] = ['R']*num_bar
        else:
            bar[0:num_bar] = ['D']*num_bar
        bg[i][0:40] =  list("|" + str_start + "cpu[" + (str(i)).ljust(3) + "]: " + (core_info[i]).ljust(25) + str_end + " |")
        bg[i][40:70] =  list(str_start + "load: " + str_end + ''.join(cpu_bar) + " |")
        bg[i][70:120] =  list(" cache[" + (str(i)).ljust(3) + "]: " + (s).ljust(4) + str_end + ''.join(bar) + "  |")
       
    os.system('clear')
    print "[0]: NORMAL STATS VIEW | [1]: INTERNAL CHACHE INFO | now: " + str(view_mode)
    print
    for i in range(nb_core):
        line = ''.join(bg[i])
        line = re.sub(r'S', r"\033[35m ", line)
        line = re.sub(r'E', r" \033[0m", line)
        line = re.sub(r'(G+)', r"\033[32m\1\033[0m", line)
        line = re.sub(r'G', r"D", line)
        line = re.sub(r'(Y+)', r"\033[33m\1\033[0m", line)
        line = re.sub(r'Y', r"D", line)
        line = re.sub(r'(R+)', r"\033[31m\1\033[0m", line)
        line = re.sub(r'R', r"D", line)
        print line


def show_mempool():
    global view_mode

    tn = telnetlib.Telnet('localhost', 5555)
    tn.read_until(read_string)

    prv_stats = []

    while True:
        log = get_log(tn)
        stats = get_stats(log)

        #print len(stats)

        if view_mode == '1':
            view_cache(stats, prv_stats)
        else:
            view_stats(stats, prv_stats)
    
        #exit(0)
        time.sleep(1)

        prv_stats = stats


if __name__ == "__main__":

    thread.start_new_thread(show_mempool, ())

    while True:
        view_mode = raw_input()
        
    
    tn.write("exit\n")

