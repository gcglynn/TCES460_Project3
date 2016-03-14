import mraa
import time

#short side = y
#long side = x

y_home=1000
y_max=1700
y_min=400
y_pin=9

x_home=900
x_max=1500
x_min=500
x_pin=5

x_servo=0
y_servo=0

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
	tilt(y_servo, y_home)
        tilt(x_servo, x_home)
	
def init_axis():
	tilt(y_servo, y_max)
	tilt(x_servo, x_max)
	time.sleep(3)
	
#        tilt(short_servo, short_min)
#        tilt(long_servo, long_max)
#        time.sleep(2)

        tilt(y_servo, y_min)
        tilt(x_servo, x_min)
        time.sleep(3)

#        tilt(short_servo, short_max)
#        tilt(long_servo, long_min)
#        time.sleep(2)


y_servo=init_servo(y_pin, y_home)
x_servo=init_servo(x_pin, x_home)

tilt_neutral()
time.sleep(2)
init_axis()
tilt_neutral()
while(True):
	pass
