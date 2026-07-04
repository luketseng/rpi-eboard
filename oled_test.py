#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

from PIL import Image, ImageDraw, ImageFont

from lib.eboard import oled_control


WIDTH = 128
HEIGHT = 32


def make_display():
    oled = oled_control()
    return oled


def new_canvas(fill=0):
    image = Image.new("1", (WIDTH, HEIGHT), fill)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    return image, draw, font


def push(oled, image):
    oled.image = image
    oled.output_disp()


def hold_frame(oled, image, seconds):
    push(oled, image)
    time.sleep(seconds)


def clear(oled, seconds=1.0):
    image, _, _ = new_canvas(0)
    hold_frame(oled, image, seconds)


def full_on(oled, seconds=1.0):
    image, _, _ = new_canvas(1)
    hold_frame(oled, image, seconds)


def row_scan(oled, seconds=0.4):
    for y in range(HEIGHT):
        image, draw, _ = new_canvas(0)
        draw.line((0, y, WIDTH - 1, y), fill=1)
        hold_frame(oled, image, seconds)


def column_scan(oled, seconds=0.4):
    for x in range(WIDTH):
        image, draw, _ = new_canvas(0)
        draw.line((x, 0, x, HEIGHT - 1), fill=1)
        hold_frame(oled, image, seconds)


def block_scan(oled, seconds=0.5):
    block_w = 16
    block_h = 8
    for y in range(0, HEIGHT, block_h):
        for x in range(0, WIDTH, block_w):
            image, draw, _ = new_canvas(0)
            draw.rectangle((x, y, x + block_w - 1, y + block_h - 1), fill=1, outline=1)
            hold_frame(oled, image, seconds)


def checkerboard(oled, seconds=2.0):
    image, draw, _ = new_canvas(0)
    for y in range(0, HEIGHT, 4):
        for x in range(0, WIDTH, 4):
            if ((x // 4) + (y // 4)) % 2 == 0:
                draw.rectangle((x, y, x + 3, y + 3), fill=1, outline=1)
    hold_frame(oled, image, seconds)


def grid(oled, seconds=2.0):
    image, draw, _ = new_canvas(0)
    for x in range(0, WIDTH, 8):
        draw.line((x, 0, x, HEIGHT - 1), fill=1)
    for y in range(0, HEIGHT, 8):
        draw.line((0, y, WIDTH - 1, y), fill=1)
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=1)
    hold_frame(oled, image, seconds)


def text_pages(oled, seconds=2.0):
    image, draw, font = new_canvas(0)
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=1, fill=0)
    draw.text((2, 0), "OLED TEST", font=font, fill=1)
    draw.text((2, 10), "Line 2: text", font=font, fill=1)
    draw.text((2, 20), "1234567890", font=font, fill=1)
    hold_frame(oled, image, seconds)


def diagonal(oled, seconds=2.0):
    image, draw, _ = new_canvas(0)
    for x in range(min(WIDTH, HEIGHT)):
        draw.point((x * 2, x), fill=1)
    draw.line((0, HEIGHT - 1, WIDTH - 1, 0), fill=1)
    hold_frame(oled, image, seconds)


def border_test(oled, seconds=2.0):
    image, draw, _ = new_canvas(0)
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=1, fill=0)
    draw.rectangle((2, 2, WIDTH - 3, HEIGHT - 3), outline=1, fill=0)
    draw.text((10, 8), "BORDER", fill=1)
    hold_frame(oled, image, seconds)


def run_targeted_sequence(oled, hold):
    clear(oled, hold)
    full_on(oled, hold)
    row_scan(oled, hold)
    column_scan(oled, 0.2)
    block_scan(oled, 0.25)
    clear(oled, hold)


def run_visual_sequence(oled, hold):
    checkerboard(oled, hold)
    grid(oled, hold)
    text_pages(oled, hold)
    diagonal(oled, hold)
    border_test(oled, hold)
    clear(oled, hold)


def main():
    parser = argparse.ArgumentParser(description="OLED display test for the rpi-eboard panel")
    parser.add_argument("--hold", type=float, default=2.0, help="Seconds to hold each pattern")
    parser.add_argument("--loop", action="store_true", help="Repeat the test sequence until interrupted")
    args = parser.parse_args()

    oled = make_display()

    try:
        while True:
            run_targeted_sequence(oled, args.hold)
            run_visual_sequence(oled, args.hold)
            if not args.loop:
                break
    except KeyboardInterrupt:
        pass
    finally:
        clear(oled, 0.2)


if __name__ == "__main__":
    main()
