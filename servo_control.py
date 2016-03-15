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

def tilt(servo, pulse):
	servo.pulsewidth_us(pulse)

def tilt_neutral(x_servo, y_servo, home):
	tilt(y_servo, home)
        tilt(x_servo, home)

def tilt_max(x_servo, y_servo, max):
        tilt(y_servo, max)
        tilt(x_servo, max)

def tilt_min(x_servo, y_servo, min):
        tilt(y_servo, min)
        tilt(x_servo, min)
	
def init_axis(x_servo, y_servo, min, max):
	tilt_min(x_servo, y_servo, min)
	time.sleep(3)
	
        tilt_max(x_servo, y_servo, max)
        time.sleep(3)

def move_towards_center(servo, position, change, wait):
	if position > 0:

		pulse = home+change
		tilt(servo,pulse)
		time.sleep(wait) 
	elif position < 0:
                pulse = home-change
                tilt(servo,pulse)
                time.sleep(wait)

#start of program
#x_servo=init_servo(x_pin, home)
y_servo=init_servo(y_pin, home)
