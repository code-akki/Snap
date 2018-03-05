import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_UP)
pwm=GPIO.PWM(3,50)
pwm.start(0)
count=0

class status:
    locked=True
    
def SetAngle(angle):
    duty = angle/18 + 2
    GPIO.output(3,True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3,False)
    pwm.ChangeDutyCycle(0)

def auto_lock():
    print "JI"
    countdown= 5
    while countdown>0:
        print countdown
        countdown-=1
        sleep(1)
        if countdown==0:
            SetAngle(0)
            status.locked = True



while True:
    button_state = GPIO.input(23)
    if button_state == False:
        if status.locked == True:
            SetAngle(180)
            status.locked = False
            print status.locked
            auto_lock()
    
            



pwm.stop()
GPIO.cleanup()

