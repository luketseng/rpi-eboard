#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.eboard import i2c_control
from rpi_stats import fan_state_label, get_cpu_temperature, select_fan_speed


FAN_SEQUENCE = ("close", "halfspeed", "fullspeed", "close")


def run_manual_sequence(board, hold):
    for state in FAN_SEQUENCE:
        board.fan_speed_switch(state)
        print(f"fan -> {state} ({fan_state_label(state)})")
        time.sleep(hold)


def run_live_control(board, interval):
    while True:
        cpu_temp = get_cpu_temperature()
        desired = select_fan_speed(cpu_temp)
        board.fan_speed_switch(desired)
        temp_text = "--.-" if cpu_temp is None else f"{cpu_temp:.1f}"
        print(f"temp={temp_text}C fan={desired} ({fan_state_label(desired)})")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Fan control test for the rpi-eboard panel")
    parser.add_argument("--hold", type=float, default=2.0, help="Seconds to hold each manual fan step")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between live temperature checks")
    parser.add_argument("--live", action="store_true", help="Drive the fan from CPU temperature like rpi_stats.py")
    parser.add_argument("--loop", action="store_true", help="Repeat the manual fan sequence until interrupted")
    args = parser.parse_args()

    board = None
    try:
        board = i2c_control()
        if args.live:
            run_live_control(board, args.interval)
        else:
            while True:
                run_manual_sequence(board, args.hold)
                if not args.loop:
                    break
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
