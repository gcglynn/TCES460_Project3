import mraa
import time

short_home=1000
short_max=1700
short_min=500
short_pin=9
short_servo=short_pin

long_home=900
long_max=1500
long_min=500
long_pin=5
long_servo=long_pin

def move_to_side(servo, degree):
	servo=mraa.Pwm(servo)
	servo.period_ms(20)
	servo.write(.2)
	servo.pulsewidth_us(degree)
	servo.enable(True)
	time.sleep(.5)

def move_to_neutral():
	move_to_side(short_servo, short_home)
        move_to_side(long_servo, long_home)
        time.sleep(2)
	
def init_axis():
	move_to_side(short_servo, short_max)
	move_to_side(long_servo, long_max)
	time.sleep(2)
	
        move_to_side(short_servo, short_min)
        move_to_side(long_servo, long_max)
        time.sleep(2)

        move_to_side(short_servo, short_min)
        move_to_side(long_servo, long_min)
        time.sleep(2)

        move_to_side(short_servo, short_max)
        move_to_side(long_servo, long_min)
        time.sleep(2)

	move_to_neutral()

move_to_neutral()
init_axis()
