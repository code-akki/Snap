from pyfcm import FCMNotification
#from flask_mqtt import Mqtt
from flask import Flask, request
#from flask_socketio import SocketIO
#from os.path import basename
import base64
import json
import pyrebase
import random
import datetime
import paho.mqtt.client as mqtt
from time import sleep

broker_address="172.16.73.39"
port=8883

config = {
  "apiKey": "AIzaSyDpXXiXKrHB4EX0WtrrLGVaCxiJInEHToE",
  "authDomain": "snap-8a7b3.firebaseapp.com",
  "databaseURL": "https://snap-8a7b3.firebaseio.com",
  "projectId": "snap-8a7b3",
  "storageBucket": "snap-8a7b3.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)

# app.config['MQTT_BROKER_URL']="172.16.73.39"
# #app.config['MQTT_BROKER_PORT'] = 1883
# # # app.config['MQTT_USERNAME']='snap_lock'
# # # app.config['MQTT_PASSWORD']='Sn@pCDI'
# app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
# app.config['MQTT_KEEPALIVE'] = 5
# #app.config['MQTT_TLS_ENABLED'] = False
# app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
# app.config['MQTT_LAST_WILL_MESSAGE'] = 'disconnected'
# app.config['MQTT_LAST_WILL_QOS'] = 2
# # Parameters for ssl encryption
# app.config['MQTT_BROKER_PORT']=8883
# app.config['MQTT_TLS_ENABLED']=True
# app.config['MQTT_TLS_CA_CERTS']='/Users/apple/Desktop/Akhil/assets/ca.crt'
# mqtt = Mqtt(app)
# socketio = SocketIO(app)

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     #socketio.emit('subscribe')
#     mqtt.subscribe("snap/home/door1/image")
#     mqtt.subscribe("snap/home/door1/android")
#     mqtt.subscribe("snap/home/door1/status")
#     mqtt.subscribe("snap/home/door1/auth")
#     print("Connected")

# @socketio.on('publish')
# def handle_publish(json_str):
#     data=json.loads(json_str)
#     mqtt.publish(data['topic'],data['message'],data['qos'])

# @socketio.on('subscribe')
# def handle_subscribe():
#     mqtt.subscribe("snap/home/door1/image")
#     # mqtt.subscribe("snap/home/door1/android")
#     # mqtt.subscribe("snap/home/door1/status")
#     # mqtt.subscribe("snap/home/door1/auth")
#     print("subscribed to topics")

@app.route("/status",methods=['GET'])
def handle_status():
    recv = request.args['lock']
    status_arr=recv.split('_')
    dummy={'locked':status_arr[0]=='True'}
    print(dummy)
    db.child("status").set(dummy)
    if status_arr[0]=='False':
        dummy={'time_in':str(datetime.datetime.now().time())}
        db.child("logs").child(status_arr[1]).set(dummy)
        if status_arr[2]=='nfc':
            # send the user id as in payload who used NFC
            sendNotification(status_arr[1],3)
        elif status_arr[2]=='android':
            # normal entry
            sendNotification(status_arr[1],2)
        elif status_arr[2]=='remote':
            #remote entry
            #send the notification with id who has granted access
            sendNotification(status_arr[1],4)
    print(recv)
    return "Hello"

@app.route("/auth",methods=['GET'])
def handle_auth():
    recv = request.args['guest']
    auth_arr=recv.split('_')
    db_data = {'time_in':str(datetime.datetime.now().time()), "time_out":""}
    db.child("logs").child(auth_arr[0]).set(db_data)
    db.child("guests").child(auth_arr[0])

def on_connect(client,userdata,flags,rc):
    print("Connected to broker")
    client.subscribe('snap/home/door1/image')
    client.subscribe('snap/home/door1/android')

def on_disconnect(client,userdata,rc=0):
    print("Disconnected")

def on_message(client, userdata, message):
    topic=message.topic
    payload=message.payload.decode("utf-8")

    if topic == "snap/home/door1/image":
        # Send the notification with Image src
        sendNotification(payload ,1)
        print(payload)
    
    elif topic == "snap/home/door1/user/android":
        print(payload)
        # 1st time configuration
        # send the key to the device and android
        #random_key = random.getrandbits(128)
        # send the userId to device
        # data_publish = json.dumps({'topic': 'snap/home/door1/user','message': payload,'qos':'2'})
        # socketio.emit("publish",data=data_publish)
        # # publish the random generated key to MQTT
        # data_publish = json.dumps({'topic': 'snap/home/door1/key','message': str(random_key),'qos':'2'})
        # socketio.emit("publish",data=data_publish)
        client.publish("snap/home/door1/user",payload)


# @mqtt.on_message()
# def handle_mqtt_message(client,userdata,message):
#     data = dict(
#         topic = message.topic,
#         payload = message.payload,
#         qos = message.qos
#     )
#     topic = data['topic']
#     payload = str(data['payload'])
    
#     if topic == "snap/home/door1/images":
#         # Send the notification with Image src
#         #sendNotification(payload ,1)
#         print(payload)
    
#     elif topic == "snap/home/door1/user/android":
#         print(payload)
#         # 1st time configuration
#         # send the key to the device and android
#         random_key = random.getrandbits(128)
#         # send the userId to device
#         data_publish = json.dumps({'topic': 'snap/home/door1/user','message': payload,'qos':'2'})
#         socketio.emit("publish",data=data_publish)
#         # publish the random generated key to MQTT
#         data_publish = json.dumps({'topic': 'snap/home/door1/key','message': str(random_key),'qos':'2'})
#         socketio.emit("publish",data=data_publish)
    
#     elif topic == "snap/home/door1/auth":
#         # data_dict=json.loads(payload)
#         auth_arr=payload.split('_')
#         if auth_arr[1]=='True':
#             db_data = {'time_in':datetime.datetime.now().time(), "time_out":""}
#             db.child("logs").child(auth_arr[0]).set(db_data)
#             db.child("guests").child(auth_arr[0])
    

def sendNotification(some_id,case):
    # API key can be found at firebase console -> Settings -> Cloud messaging -> Server Key
    push_service = FCMNotification(api_key="AAAARXD4tc8:APA91bF--czU1L658-tCk8E4sQaguamIFapxjiZ1pFqzjIPj6j5hG-_yE__DPXLgq_tt_oHmE0fonw1HzpTwy90QMsVv4-okWJqPHZHfsqAtvJFiV902AUm4yQt1bipcETlzL0YsjbWB")
    # Sending to multiple devices using registration ids
    # registration_ids = [] 
    registration_id = "cb09uII_1E0:APA91bF0EIEggPhVEAoaFXPfxWSVi1tXfT8gz3xMWr1pl2mxeQDQrDC1yyodVIw_8VJLjuwISQ0FgDQ-hn9H-mGa6WAhfQfPkLmuSUvoO6-l1uYLA49HPnQzhiw00R4Z92DuR-mR8unH"
    message_title="Knock Knock"
    #message_body1="Somebody is at your door."
    message_body2="User {} has opened the door.".format(some_id)
    message_body3="User {} has used the NFC tag.".format(some_id)
    message_body4="User {} has opened the door for guest.".format(some_id)
    # Add priority
    extra_kwargs = {
        'priority' : 'high'
    }
    result={'key':'values'}
    if case == 1:
        # Create a data message for the client to process data
        data_message = {
            "\"Id\"": "\"{}\"".format(some_id),
            "\"message_title\"": "\"Knock Knock\"",
            "\"message_body\"": "\"Somebody is at your door\"",
            "\"time_stamp\"": "\"{}\"".format(datetime.datetime.now().time())
        }
        # result = push_service.notify_multiple_devices(registration_ids=registration_ids,
        #     message_title=message_title,message_body=message_body1,
        #     data_message=data_message,extra_kwargs=extra_kwargs)
        result = push_service.single_device_data_message(registration_id=registration_id,
            data_message=data_message,extra_kwargs=extra_kwargs)    
    elif case ==2:
        # Create a data message for the client to process data
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body2) 
    elif case ==3:
        # Create a data message for the client to process data
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body3)

    elif case==4:
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body4)
    
    print(result)

# add logic to trust the android client

# client=mqtt.Client("Flask")
# client.tls_set('/Users/apple/Desktop/Akhil/assets/ca.crt')
# client.on_connect=on_connect
# client.on_message=on_message
# client.connect(broker_address,port)
# client.subscribe('snap/home/door1/status')
# client.subscribe('snap/home/door1/image')
# client.subscribe('snap/home/door1/auth')
# client.loop_forever()

if __name__ == '__main__':
    client=mqtt.Client("Flask_"+str(datetime.datetime.now().time()))
    client.tls_set('/Users/apple/Desktop/Akhil/assets/ca.crt')
    client.on_connect=on_connect
    client.on_message=on_message
    client.on_disconnect=on_disconnect
    client.connect(broker_address,port)
    client.loop_start()
    sleep(3)
    app.run(host='0.0.0.0', port=5000)