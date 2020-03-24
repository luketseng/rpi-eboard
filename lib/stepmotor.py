#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
# see GPIO output pin: $ pinout
STEPPER_PINS = [14, 15, 18, 23]
STEPS_PER_REVOLUTION = 64 * 64

SEQUENCE = ['1000', '1100', '0100', '0110', '0010', '0011', '0001', '1001']

for pin in STEPPER_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

SEQUENCE_COUNT = len(SEQUENCE)
PINS_COUNT = len(STEPPER_PINS)

if len(sys.argv) > 1:
    wait_time = int(sys.argv[1]) / float(1000)
else:
    wait_time = 10 / float(1000)

if __name__ == '__main__':
    sequence_index = 0
    direction = -1
    steps = 0
    try:
        print('按下 Ctrl-C 可停止程式')
        while True:
            for pin in range(PINS_COUNT):
                GPIO.output(STEPPER_PINS[pin], int(SEQUENCE[sequence_index][pin]))

            steps += direction
            #if steps >= STEPS_PER_REVOLUTION:
            #    direction=-1
            #elif steps < 0:
            #    direction=1

            sequence_index += direction
            sequence_index %= SEQUENCE_COUNT

            #print('index={}, direction={}'.format(sequence_index, direction))
            time.sleep(wait_time)
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()
