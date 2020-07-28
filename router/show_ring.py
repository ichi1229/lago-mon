#!/usr/bin/env python

import os, sys, re, time
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
regexp = re.compile(r'[^\x20-\x7E\n]')


def get_stats(log):
    stats = []
    for rings in log.replace(' ', '').split('ring')[1:]:
        vals = rings.split('\n')
        rs = {}
        rs['name'] = vals[0]
        rs['flags'] = vals[1][6:]
        rs['size'] = vals[2][5:]
        rs['capacity'] = vals[3][9:]
        rs['ct'] = vals[4][3:]
        rs['ch'] = vals[5][3:]
        rs['pt'] = vals[6][3:]
        rs['ph'] = vals[7][3:]
        rs['used'] = vals[8][5:]
        rs['avail'] = vals[9][6:]
        stats.append(rs)
    stats = sorted(stats, key=lambda x:x['name'])
    return stats


def get_log(tn):
    tn.write("show ring\n")
    result = tn.read_until(read_string)
    tn_data = regexp.sub("", result)
    return tn_data



def view_stats(stats, prv_stats):
    r_stats = 9
    r_cell = 8
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
        num_bar = int(30 * float(s['used']) / float(s['capacity']))
        bar = ['*']*30
        if 1 <= num_bar and num_bar < 15:
            bar[0:num_bar] = ['G']*num_bar
        elif 15 <= num_bar and num_bar < 30:
            bar[0:num_bar] = ['Y']*num_bar
        elif 30 <= num_bar:
            bar[0:num_bar] = ['R']*num_bar
        else:
            bar[0:num_bar] = ['D']*num_bar
        bg[r_stats*(i-r_off)+0][0+c_off:40+c_off] = list(str_plus + str_equal*38 + str_plus)
        bg[r_stats*(i-r_off)+1][0+c_off:40+c_off] = list(str_bar + " " + s['name'].ljust(36) + " " + str_bar)
        bg[r_stats*(i-r_off)+2][0+c_off:40+c_off] = list(str_plus + str_minus*38 + str_plus)
        #bg[r_stats*(i-r_off)+3][0+c_off:40+c_off] = list(str_bar + " " + id_update + "             "                  + ("flags: " + s['flags'] + "      ").ljust(17) + " " + str_bar)
        bg[r_stats*(i-r_off)+3][0+c_off:40+c_off] = list(str_bar + " " + ("ct   : " + s['ct']).ljust(17) +       "  " + ("pt   : " + s['pt']).ljust(17) + " " + str_bar)
        bg[r_stats*(i-r_off)+4][0+c_off:40+c_off] = list(str_bar + " " + ("ch   : " + s['ch']).ljust(17) +       "  " + ("ph   : " + s['ph']).ljust(17) + " " + str_bar)
        bg[r_stats*(i-r_off)+5][0+c_off:40+c_off] = list(str_bar + " " + ("capa : " + s['capacity']).ljust(17) + "  " + ("avail: " + s['avail']).ljust(17) + " " + str_bar)
        bg[r_stats*(i-r_off)+6][0+c_off:40+c_off] = list(str_bar + " " + ("size : " + s['size']).ljust(17) +     "  " + ("used : " + s['used']).ljust(17) + " " + str_bar)
        bg[r_stats*(i-r_off)+7][0+c_off:40+c_off] = list(str_bar + " ring: " + ''.join(bar) + " " + str_bar)
        bg[r_stats*(i-r_off)+8][0+c_off:40+c_off] = list(str_plus + str_equal*38 + str_plus)
    os.system('clear')
    for i in range(r_stats*r_cell):
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
        sys.stdout.flush()

if __name__ == "__main__":
    tn = telnetlib.Telnet('localhost', 5555)
    read_string = mark + " "
    tn.read_until(read_string)

    prv_stats = []
    
    while True:
        
        log = get_log(tn)
        stats = get_stats(log)

        view_stats(stats, prv_stats)
    
        #exit(0)
        time.sleep(1)

        prv_stats = stats
    
    tn.write("exit\n")

