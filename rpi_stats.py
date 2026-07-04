#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import socket
import time

import psutil

from lib.eboard import i2c_control, oled_control


LOOP_INTERVAL = 5
HARDWARE_DELAY = 1.0
TEMP_CLOSE = 45.0
TEMP_HALF = 58.0
ETH_IFACE = os.environ.get("ETH_IFACE", "eth0")
WLAN_IFACE = os.environ.get("WLAN_IFACE", "wlan0")


def get_cpu_usage():
    return psutil.cpu_percent(interval=0.5)


def get_cpu_temperature():
    temps = psutil.sensors_temperatures(fahrenheit=False)
    for sensor_name in ("cpu_thermal", "coretemp", "soc_thermal"):
        entries = temps.get(sensor_name)
        if entries:
            for entry in entries:
                if entry.current is not None:
                    return float(entry.current)

    temp_path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(temp_path, "r", encoding="utf-8") as handle:
            return int(handle.read().strip()) / 1000.0
    except (OSError, ValueError):
        return None


def get_ram_info():
    mem = psutil.virtual_memory()
    return mem.percent


def get_interface_ip(ifname):
    addrs = psutil.net_if_addrs().get(ifname, [])
    for addr in addrs:
        if addr.family == socket.AF_INET:
            return addr.address
    return "-"


def select_fan_speed(cpu_temp):
    if cpu_temp is None:
        return "fullspeed"
    if cpu_temp < TEMP_CLOSE:
        return "close"
    if cpu_temp < TEMP_HALF:
        return "halfspeed"
    return "fullspeed"


def fan_state_label(fan_state):
    return {
        "close": "off",
        "halfspeed": "half",
        "fullspeed": "full",
    }.get(fan_state, "unk")


def format_line(label, value, width=20):
    text = f"{label}{value}"
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def build_display_lines(cpu_usage, cpu_temp, fan_state):
    ram_percent = get_ram_info()
    eth0_ip = get_interface_ip(ETH_IFACE)
    wlan0_ip = get_interface_ip(WLAN_IFACE)

    if cpu_temp is None:
        temp_text = "T:--.-C"
    else:
        temp_text = f"T:{cpu_temp:.1f}C"

    line1 = f"CPU:{cpu_usage:4.1f}% {temp_text}"
    line2 = format_line(f"{ETH_IFACE}:", eth0_ip)
    line3 = format_line(f"{WLAN_IFACE}:", wlan0_ip)
    line4 = f"fan:{fan_state_label(fan_state)} mem:{ram_percent:.0f}%"

    return (
        line1,
        line2,
        line3,
        line4,
    )


def update_fan(board, current_state, desired_state):
    if desired_state != current_state:
        board.fan_speed_switch(desired_state)
        time.sleep(HARDWARE_DELAY)
        return desired_state
    return current_state


def main():
    oled = None
    board = None
    fan_state = None

    try:
        oled = oled_control()
        board = i2c_control()
        time.sleep(HARDWARE_DELAY)
        while True:
            cpu_usage = get_cpu_usage()
            cpu_temp = get_cpu_temperature()
            desired_fan_state = select_fan_speed(cpu_temp)
            fan_state = update_fan(board, fan_state, desired_fan_state)
            print(cpu_usage, cpu_temp, desired_fan_state, fan_state)

            str_list = build_display_lines(cpu_usage, cpu_temp, fan_state)
            oled.draw_4line_string(str_list)
            oled.output_disp()
            time.sleep(HARDWARE_DELAY)

            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        if board is not None:
            try:
                board.fan_speed_switch("close")
            except Exception:
                pass
            try:
                board.i2c_close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
