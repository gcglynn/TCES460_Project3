#!/usr/bin/python
import mraa
import time

#short side = y
#long side = x

y_pin=6
y_servo=0

x_pin=5
x_servo=0

home=1000
max=500
min=1500

def init_servo(pin, home):
	servo=mraa.Pwm(pin)
        servo.period_ms(20)
        servo.write(.2)
        servo.pulsewidth_us(home)
        servo.enable(True)
        return servo

def tilt(servo, position):
	servo.pulsewidth_us(position)

def tilt_neutral():
	tilt(y_servo, home)
        tilt(x_servo, home)

def tilt_max():
        tilt(y_servo, max)
        tilt(x_servo, max)

def tilt_min():
        tilt(y_servo, min)
        tilt(x_servo, min)

def init_axis():
	tilt_min()
	time.sleep(3)
	
        tilt_max()
        time.sleep(3)

#start of program
y_servo=init_servo(y_pin, home)
x_servo=init_servo(x_pin, home)

tilt_neutral()
#tilt_max()
#tilt_min()
while(True):
	pass
