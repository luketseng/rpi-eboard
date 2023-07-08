#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time
import json, yaml

class i2c_control():
    '''init logging'''

table = {
    'rgb_bright': {
        'rgb_control': {
            'reg': 0x00,
            'value': {
                'All': 0xFF,
                'rgb1': 0x00,
                'rgb2': 0x01,
                'rgb3': 0x02}},
        'rgb_R': {
            'reg': 0x01,
            'value': 0x00},
        'rgb_G': {
            'reg': 0x02,
            'value': 0x00},
        'rgb_B': {
            'reg': 0x03,
            'value': 0x00}},
    'rgb_animate': {
        'reg_rgb_mode': {
            'reg': 0x04,
            'value': {
                'running': 0x00,
                'breathing': 0x01,
                'scroll': 0x02,
                'rainbow': 0x03,
                'colorful': 0x04}},
        'rgb_speed': {
            'reg': 0x05,
            'value': {
                'slow': 0x01,
                'medium': 0x02,
                'high': 0x03}},
        'rgb_color': {
            'reg': 0x06,
            'value': {
                'red': 0x00,
                'green': 0x01,
                'blue': 0x02,
                'yellow': 0x03,
                'purple': 0x04,
                'cyan': 0x05,
                'white': 0x06}},
        'rgb_close': {
            'reg': 0x07,
            'value': {
                'close': 0x00}}},
    'fan_control': {
        'fan_speed': {
            'reg': 0x08,
            'value': {
                'close': 0x00,
                'fullspeed': 0x01,
                'halfspeed': 0x05}}}}

if __name__ == '__main__':
    # use json
    #with open('config.json', 'w') as f:
    #    json.dump(table, f, indent=4)
    #with open('config.json', 'r') as f:
    #    a=json.load(f, encoding='utf-8')
    #    #v=a['fan_control']['fan_speed']['value']['close']
    #print(a)

    # use yaml
    with open('config.yaml', 'w') as f:
        yaml.dump(table, f, encoding='utf-8', default_flow_style=False, sort_keys=False)
    with open('config.yaml', 'r') as f:
        a = yaml.load(f, Loader=yaml.FullLoader)
    print(a)
    RGB_value = {'rgb_R': 0xFF, 'rgb_G': 0xFF, 'rgb_B': 0xFF}
    a['rgb_bright']['rgb_R']['value'] = RGB_value['rgb_R']
    a['rgb_bright']['rgb_G']['value'] = RGB_value['rgb_G']
    a['rgb_bright']['rgb_B']['value'] = RGB_value['rgb_B']
    print(a)
    pass
