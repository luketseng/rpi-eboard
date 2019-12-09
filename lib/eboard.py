#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time
# import smbus2 to crotrol i2c
from smbus2 import SMBus
# import SSD1306 library for oled control
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

class i2c_control():
    '''init logging'''

    i2c_addr=None
    i2c=None

    def __init__(self):
        #see i2c device: $ sudo i2cdetect -y -a 1
        self.i2c=SMBus(1) # device in 1st I2C module
        self.i2c_addr=0x0d
        self.i2c_table={'rgb_bright':{
                            'reg_rgb_control': 0x00, # (1st, 2nd, 3th, all): (0x00, 0x01, 0x02, 0xFF)
                            'reg_rgb_R': 0x01, # R value(0x00-0xFF)
                            'reg_rgb_G': 0x02, # G value(0x00-0xFF)
                            'reg_rgb_B': 0x03}, # B value(0x00-0xFF)
                        'rgb_animate':{
                            'reg_rgb_mode': 0x04,
                            'reg_rgb_speed': 0x05,
                            'reg_rgb_color': 0x06,
                            'reg_rgb_close': 0x07},
                        'fan_control':{
                            'reg_fan_speed': 0x08}
                       }

        self.rgb_close()
        self.fan_speed_switch(0)
        for i in range(3):
            self.rgb_simple_control(0xFF, [0xFF, 0xFF, 0xFF])
            self.rgb_close()
        time.sleep(2)
        self.fan_speed_switch(1)
        #self.rgb_animate(0x01, 0x01, 0x06)
        #for i in range(7):
        #    self.rgb_animate(0x01, 0x02, i)
        #    time.sleep(3)

    def rgb_simple_control(self, rgb_index, rgb_list):
        i2c=self.i2c
        i2c_addr=self.i2c_addr
        req_table=self.i2c_table['rgb_bright']
        val_table=[('reg_rgb_control', rgb_index),
                   ('reg_rgb_R', rgb_list[0]), ('reg_rgb_G', rgb_list[1]), ('reg_rgb_B', rgb_list[2])]
        for key, value in val_table:
            i2c.write_byte_data(i2c_addr, req_table[key], value)
            time.sleep(.2)
        time.sleep(.3)

    def rgb_animate(self, rgb_mode, rgb_speed, rgb_color):
        i2c=self.i2c
        i2c_addr=self.i2c_addr
        req_table=self.i2c_table['rgb_animate']
        i2c.write_byte_data(i2c_addr, int('{reg_rgb_mode}'.format(**req_table)), rgb_mode)
        i2c.write_byte_data(i2c_addr, int('{reg_rgb_speed}'.format(**req_table)), rgb_speed)
        if rgb_mode==0x00 or rgb_mode==0x01:
            i2c.write_byte_data(i2c_addr, int('{reg_rgb_color}'.format(**req_table)), rgb_color)
        time.sleep(.3)

    def rgb_close(self):
        i2c=self.i2c
        i2c_addr=self.i2c_addr
        req_table=self.i2c_table['rgb_animate']
        i2c.write_byte_data(i2c_addr, int('{reg_rgb_close}'.format(**req_table)), 0x00)
        time.sleep(.3)

    def fan_speed_switch(self, sw):
        i2c=self.i2c
        i2c_addr=self.i2c_addr
        req_table=self.i2c_table['fan_control']
        # sw: [0x00~0x09], ex: 0x00=close, 0x01=full speed, 0x02=20% speed
        i2c.write_byte_data(i2c_addr, int('{reg_fan_speed}'.format(**req_table)), sw)
        time.sleep(1)

class oled_control():
    '''init logging'''

    i2c_addr=None
    disp=None
    width=None
    height=None
    image=None
    draw=None

    def __init__(self):
        self.i2c_addr=0x3c
        RST = None     # on the PiOLED this pin isnt used
        # 128x32 display with hardware I2C:
        self.disp=Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_address=self.i2c_addr)
        # Initialize library.
        self.disp.begin()
        self.clear_disp()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width=self.disp.width
        self.height=self.disp.height
        self.draw_init()

    def draw_init(self):
        self.image=Image.new('1', (self.width, self.height))
        # Get drawing object to draw on image.
        self.draw=ImageDraw.Draw(self.image)
        # Draw a black filled box to clear the image.
        for i in range(3):
            self.draw.rectangle((0, 0, self.width, self.height), outline=1, fill=1)
            self.output_disp()
            time.sleep(1)
            self.clear_disp()
            time.sleep(1)

    def clear_disp(self):
        # Clear display.
        self.disp.clear()
        self.disp.display()

    def output_disp(self):
        '''Display image.'''
        self.disp.image(self.image)
        self.disp.display()

    def draw_4line_string(self, str_list):
        # First define some constants to allow easy resizing of shapes.
        padding=-2
        top=padding
        # Move left to right keeping track of the current x position for drawing shapes.
        x=0
        # Load default font.
        font=ImageFont.load_default()
        # ex. you can change font stype as below
        #font=ImageFont.truetype('Downloads/EBRIMA.TTF', 10)#, encoding='utf-8')

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # Write two lines of text.
        for i, diff in enumerate(range(0, 32, 8)):
            self.draw.text((x, top+diff), str_list[i], font=font, fill=255)

if __name__ == '__main__':
    '''sample for oled control and use 'draw_4line_string' function'''
    #oled=oled_control()
    #strlist=['abcde', '12345', 'hello word', 'by luke']
    #oled.draw_4line_string(strlist)
    #oled.output_disp()

    '''sample for rgb control'''
    man=i2c_control()
