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


RGB_LEVELS = (0, 32, 64, 128, 192, 255)
RGB_TARGETS = (
    ("All", (255, 255, 255), "white"),
    ("All", (255, 0, 0), "red"),
    ("All", (0, 255, 0), "green"),
    ("All", (0, 0, 255), "blue"),
    ("All", (255, 255, 0), "yellow"),
    ("All", (255, 0, 255), "purple"),
    ("All", (0, 255, 255), "cyan"),
)


def run_sequence(board, hold, include_channels=False):
    for level in RGB_LEVELS:
        board.rgb_simple_control("All", [level, level, level])
        print(f"RGB all -> {level:3d},{level:3d},{level:3d}")
        time.sleep(hold)

    for control, values, label in RGB_TARGETS:
        board.rgb_simple_control(control, list(values))
        print(f"RGB {control} -> {label}")
        time.sleep(hold)

    if include_channels:
        # Some controller revisions do not accept per-channel mode writes.
        # Keep this opt-in so the default test stays on the safer path.
        for control in ("rgb1", "rgb2", "rgb3"):
            board.rgb_simple_control(control, [255, 255, 255])
            print(f"RGB channel -> {control}: white")
            time.sleep(hold)
            board.rgb_close()
            time.sleep(hold / 2 if hold > 0 else 0)

    board.rgb_close()


def main():
    parser = argparse.ArgumentParser(description="RGB brightness and color test for the rpi-eboard panel")
    parser.add_argument("--hold", type=float, default=1.0, help="Seconds to hold each RGB step")
    parser.add_argument("--channels", action="store_true", help="Also test rgb1/rgb2/rgb3 channel mode")
    parser.add_argument("--loop", action="store_true", help="Repeat the test sequence until interrupted")
    args = parser.parse_args()

    board = None
    try:
        board = i2c_control()
        while True:
            run_sequence(board, args.hold, include_channels=args.channels)
            if not args.loop:
                break
    except KeyboardInterrupt:
        pass
    finally:
        if board is not None:
            try:
                board.rgb_close()
            except Exception:
                pass
            try:
                board.i2c_close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
