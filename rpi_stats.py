#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time
import psutil
import socket
import fcntl
#import netifaces as ni
import struct
import subprocess
from lib.eboard import i2c_control, oled_control
from datetime import datetime

# Return % of CPU used by user as a character string
def getCPUuse():
    return psutil.cpu_percent(interval=0.5)
    #return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())[:3])

# Return CPU temperature as a character string
def getCPUtemperature():
    temp_path = "/sys/class/thermal/thermal_zone0/temp"
    cmd = 'cat {}'.format(temp_path)
    res = os.popen(cmd).readline()
    temp = int(res) / 1000.0
    return temp
    # cmd: vcgencmd measure_temp

# Return RAM information (unit=kb) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def getRAMinfo():
    cmd = 'free'
    p = os.popen(cmd)
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i == 2:
            ram_stats = line.split()[1:4]
            ram_total = round(float(ram_stats[0]) / 1024, 3)
            ram_used = round(float(ram_stats[1]) / 1024, 3)
            ram_free = round(float(ram_stats[2]) / 1024, 3)
            return (ram_free, ram_total, ram_free * 100 / ram_total)

# Return information about disk space as a list (unit included)
# Output is in kb, here I convert it in Mb for readability
# Index 0: total disk space
# Index 1: used disk space
# Index 2: remaining disk space
# Index 3: percentage of disk used
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i == 2:
            disk_stats = line.split()[1:5]
            disk_total = disk_stats[0]
            disk_used = disk_stats[1]
            disk_perc = disk_stats[3]
            return (disk_used, disk_total, disk_perc)

# Return information about ip address
# get_ip_address('eth0')
def get_ip_address(ifname):
    #ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    #print(ip)
    #return ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15]))[20:24])

def adjust_rgb(cpu_temp):
    # temp control rgb
    level_temp = 0
    if abs(int(cpu_temp) - level_temp) > 0:
        if cpu_temp <= 40:
            level_temp = 40
            i2c_control.rgb_animate(0x01, 0x01, 0x06)
        elif cpu_temp <= 45:
            level_temp = 45
            i2c_control.rgb_animate(0x01, 0x02, 0x03)
        elif cpu_temp <= 50:
            level_temp = 50
            i2c_control.rgb_animate(0x01, 0x03, 0x00)

def stdout_flush(string_list, delay=1):
    for i in string_list:
        sys.stdout.write("\r{:40}".format(i))
        sys.stdout.flush()  # '\t' can't flush()
        time.sleep(delay)

def loop_check():
    global fan_flag
    # CPU informatiom
    cpu_usage = getCPUuse()
    cpu_temp = getCPUtemperature()

    # RAM information
    ram_stats = getRAMinfo()

    # Disk information
    disk_stats = getDiskSpace()

    cpu_info_string = "CPU:{:<4.1f}%  T:{:.2f}{}C".format(cpu_usage, cpu_temp, chr(0xB0))
    ram_info_string = "Mem:{:.0f}/{:.0f}M {:.1f}%".format(*ram_stats)
    disk_info_string = "Disk:{}/{} {}".format(*disk_stats)
    ip_addr_string = "eth0:{}".format(get_ip_address('eth0'))
    str_list = (cpu_info_string, ram_info_string, disk_info_string, ip_addr_string)
    #stdout_flush(str_list)

    oled.draw_4line_string(str_list)
    oled.output_disp()
    #adjust_rgb(cpu_temp)
    time.sleep(5)

    if datetime.now().time().hour > 9 and datetime.now().time().hour < 20 and not fan_flag:
        i2c_control.fan_speed_switch('fullspeed')
        fan_flag = True
    if (datetime.now().time().hour <= 9 and fan_flag) or (datetime.now().time().hour >= 20 and fan_flag):
        i2c_control.fan_speed_switch('close')
        fan_flag = False

def process_check():
    count=0
    process = subprocess.Popen("ps aux | grep rpi_stats", shell=True, stdout=subprocess.PIPE)
    stdout_list = process.communicate()[0].split('\n')
    for s in stdout_list:
        if "/home/luke/rpi_stats.py" in s:
            count+=1
    print(count)
    if count > 2:
        return True
    return False

if __name__ == '__main__':
    if process_check():
        print('process exist')
        exit()

    global oled, i2c_control
    oled = oled_control()
    i2c_control = i2c_control()
    fan_flag = True

    while True:
       loop_check()
