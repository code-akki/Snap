import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import json
import os
import random
import nfc

#/snap/home/door1/status payload {locked: boolean, userId: userid, method: nfc/android/remote} sub pub
#/snap/home/door1/auth {guestid:guestid, auth: boolean} sub
#/snap/home/door1/user sub
#/snap/hoome/door1/key sub
#snap/home/door1/image pub

broker_address="172.16.73.39"
port=8883

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

    if topic is "snap/home/door1/auth":
        #data_dict = json.loads([payload])
        auth_arr=payload.split('_')
        if auth_arr[0] == 'True':
            #unlock the door
            if status.locked == True:
                SetAngle(180)
                status.locked = False
                #send the opened locked status
                # data_json = json.dumps({'locked': False, 'userId': guesId, 'method': 'remote'})
                pub_payload='False_'+auth_arr[2]+'_remote'
                client.publish("snap/home/door1/status",pub_payload)
                print(str(status.locked))
                auto_lock()
            else:
                pass
    
    elif topic is "snap/home/door1/user":
        file_user=open("assets/users.txt","a+")
        f.seek(0)
        if payload in file_user.read():
            pass
        else:
           file_user.write("\n"+payload)

    elif topic is "snap/home/door1/key":
        #store the key
        file_key = open("assets/key.txt","w+")
        file_key.write(payload)

    
def on_disconnect(client, userdata, rc=0):
    client.loop_stop()

def auto_lock():
    countdown= 5
    while countdown>0:
        countdown-=1
        if countdown==0:
            SetAngle(0)
            status.locked = True                   
            #dummy={'locked': True}
            #db.child("status").set(dummy)
            #data_json = json.dumps({'locked': True, 'userId': 'null', 'method': 'null'})
            pub_payload='True_'
            client.publish("snap/home/door1/status",str(data_json))

if __name__=='__main__':
    client = mqtt.Client("Rasp")
    client.tls_set("/home/pi/Desktop/Snap/assets/ca.crt")
    client.on_connect = on_connect
    client.on_message=on_message
    client.on_disconnect=on_disconnect
    client.connect(broker_address,port)
    #Subscribe to all the required topics
    client.subscribe("snap/home/door1/status")
    client.subscribe("snap/home/door1/auth")
    client.subscribe("snap/home/door1/user")
    client.subscribe("snap/home/door1/key")
    client.loop_forever()
    while True:
        clf=nfc.ContactlessFrontend()
        assert clf.open('tty:USB0') is True
        tag=clf.connect(rdwr={'on-connect': lambda tag: False})
        print tag
        cla=0x00
        ins=0xA4
        p1=0x04
        p2=0x00
        data=bytearray.fromhex('asd')
        tag.send_apdu(cla, ins, p1, p2, data, check-status=False)

