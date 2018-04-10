import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from time import sleep
import json
import os
import random
import nfc
import requests

#/snap/home/door1/status payload {locked: boolean, userId: userid, method: nfc/android/remote} sub pub
#/snap/home/door1/auth {guestid:guestid, auth: boolean} sub
#/snap/home/door1/user sub
#/snap/hoome/door1/key sub
#snap/home/door1/image pub

broker_address="172.16.73.4"
port=1883

#configuring the pins for Button and servomotor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_UP)
pwm=GPIO.PWM(3,50)
pwm.start(0)


class status:
    locked=True


def SetAngle(angle):
    duty = angle/18 + 2
    GPIO.output(3,True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3,False)
    pwm.ChangeDutyCycle(0)

def on_connect(client, userdata, flags, rc):
    print("Connected")

def on_message(client, userdata,  message):
    print("on_message")
    print("message received", str(message.payload.decode("utf-8")))
    print("message topic", message.topic)

    #put in business logic

    topic = message.topic
    payload = message.payload.decode("utf-8")
    print payload

    if topic == "snap/home/door1/auth":
        #data_dict = json.loads([payload])
        auth_arr=payload.split('_')
        print payload
        if auth_arr[1] == 'True':
            #unlock the door
            r=requests.get('http://172.16.226.31:5000/auth?guest='+auth_arr[0]+'_'+auth_arr[2])
            if status.locked == True:
                SetAngle(180)
                status.locked = False
                #send the opened locked status
                #data_json = json.dumps({'locked': False, 'userId': guesId, 'method': 'remote'})
                #client.publish("snap/home/door1/status","False_"+auth_arr[2]+"_remote")
                r=requests.get('http://172.16.226.31:5000/status?lock=False_'+auth_arr[2]+'_remote')
                print(str(status.locked))
                auto_lock()
            else:
                pass
    
    elif topic == "snap/home/door1/user":
        file_user=open("assets/users.txt","a+")
        f.seek(0)
        if payload in file_user.read():
            pass
        else:
           file_user.write("\n"+payload)

    elif topic == "snap/home/door1/key":
        #store the key
        file_key = open("assets/key.txt","w+")
        file_key.write(payload)

    elif topic == "snap/home/door1/open":
        #open  using servo motor
        print payload
        lock_arr=payload.split("_")
        if lock_arr[0] == "yes":
            print "publish"
            #client.publish("snap/home/door1/status","False_"+lock_arr[1]+"_android")
            r=requests.get('http://172.16.226.31:5000/status?lock=False_'+lock_arr[1]+'_android')
            print r
            SetAngle(180)
            status.locked=False
            auto_lock()

    
def on_disconnect(client, userdata, rc=0):
    client.loop_stop()
    print("disconnetecd")

def on_publish(client,userdata,mid):
    print "publish data"


def auto_lock():
    countdown= 10
    while countdown>0:
        countdown-=1
        sleep(1)
        if countdown==0:
            SetAngle(0)
            status.locked = True                   
            #dummy={'locked': True}
            #db.child("status").set(dummy)
            #client.publish("snap/home/door1/status","True_''_''")
            r=requests.get('http://172.16.226.31:5000/status?lock=True')

if __name__=='__main__':
    client = mqtt.Client("Rasp123")
    #client.tls_set("/home/pi/Desktop/Snap/assets/ca.crt")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message=on_message
    client.on_disconnect=on_disconnect
    client.connect(broker_address,port)
    #Subscribe to all the required topics
    client.subscribe("snap/home/door1/status")
    client.subscribe("snap/home/door1/auth")
    client.subscribe("snap/home/door1/user")
    client.subscribe("snap/home/door1/key")
    client.subscribe("snap/home/door1/open")
    client.loop_forever()
    while True:
        clf=nfc.ContactlessFrontend()
        assert clf.open('tty:USB0') is True
        tag=clf.connect(rdwr={'on-connect': lambda tag: False})
        print tag
        if status.locked == True:
            SetAngle(180)
            status.locked=False
            client.publish("snap/home/door1/status","False_user123_nfc")
            auto_lock()

