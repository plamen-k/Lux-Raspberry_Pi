#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time

LCD_RS = 26
LCD_E = 24
LCD_D4 = 23
LCD_D5 = 21
LCD_D6 = 19
LCD_D7 = 22

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM adres dla 1 linii
LCD_LINE_2 = 0xC0 # LCD RAM adres dla 2 linii

E_PULSE = 0.00005
E_DELAY = 0.00005

def main():
    GPIO.setup(LCD_E, GPIO.OUT)# E
    GPIO.setup(LCD_RS, GPIO.OUT)# RS
    GPIO.setup(LCD_D4, GPIO.OUT)# DB4
    GPIO.setup(LCD_D5, GPIO.OUT)# DB5
    GPIO.setup(LCD_D6, GPIO.OUT)# DB6
    GPIO.setup(LCD_D7, GPIO.OUT)# DB7


    lcd_init()

   
    
    li = ["1", "3"]
    bi = ["2", "4"]
    for x in li:
        for y in bi:
            lcd_byte(LCD_LINE_1, LCD_CMD)
            lcd_string("________________")
    

    



def lcd_init():
    lcd_byte(0x33,LCD_CMD)
    lcd_byte(0x32,LCD_CMD)
    lcd_byte(0x28,LCD_CMD)
    lcd_byte(0x0C,LCD_CMD)
    lcd_byte(0x06,LCD_CMD)
    lcd_byte(0x01,LCD_CMD)


def lcd_string(message):
    message = message.ljust(LCD_WIDTH," ")

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
    GPIO.output(LCD_RS, mode) # RS


    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)


    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)


    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)


    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

if __name__ == '__main__':
    main()
