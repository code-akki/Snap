from pyfcm import FCMNotification
from flask_mqtt import Mqtt
from flask import Flask
from flask_socketio import SocketIO
from os.path import basename
import base64
import json
import pyrebase
import random
import datetime

app = Flask(__name__)
app.config['MQTT_BROKER']="172.16.73.4"
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME']='snap_lock'
app.config['MQTT_PASSWORD']='Sn@pCDI'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'disconnected'
app.config['MQTT_LAST_WILL_QOS'] = 2
# # Parameters for ssl encryption
# app.config['MQTT_BROKER_PORT']=8883
# app.config['MQTT_TLS_ENABLED']=True
# app.config['MQTT_TLS_CA_CERTS ']='/assets/ca.crt'
mqtt = Mqtt(app)
socketio = SocketIO(app)


config = {
  "apiKey": "AIzaSyDpXXiXKrHB4EX0WtrrLGVaCxiJInEHToE",
  "authDomain": "snap-8a7b3.firebaseapp.com",
  "databaseURL": "https://snap-8a7b3.firebaseio.com",
  "projectId": "snap-8a7b3",
  "storageBucket": "snap-8a7b3.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

@mqtt.on_connect()
def handle_connect():
    socketio.emit('subscribe')

@socketio.on('publish')
def handle_publish(json_str):
    data=json.loads(json_str)
    mqtt.publish(data['topic'],data['message'],data['qos'])

@socketio.on('subscribe')
def handle_subscribe():
    mqtt.subscribe("snap/home/door1/image")
    mqtt.subscribe("snap/home/door1/android")
    mqtt.subscribe("snap/home/door1/status")
    mqtt.subscribe("snap/home/door1/")

@mqtt.on_message()
def handle_mqtt_message(client,userdata,message):
    data = dict(
        topic = message.topic,
        payload = message.payload,
        qos = message.qos
    )
    topic = data['topic']
    payload = data['payload']
    if topic is "snap/home/door1/images":
        # Send the notification with Image src
        sendNotification(payload ,1)
    
    elif topic is "snap/home/door1/user/android":
        # 1st time configuration
        # send the key to the device and android
        random_key = random.getrandbits(128)
        # send the userId to device
        data_publish = json.dumps({'topic': 'snap/home/door1/user','message': payload,'qos':'2'})
        socketio.emit("publish",data=data_publish)
        # publish the random generated key to MQTT
        data_publish = json.dumps({'topic': 'snap/home/door1/key','message': str(random_key),'qos':'2'})
        socketio.emit("publish",data=data_publish)
    
    elif topic is "snap/home/door1/status":
        #store the locked value in fireabse to show on android
        data_dict = json.loads(payload)
        dummy={'locked':data_dict['locked']=='True'}
        db.child("status").set(dummy)
        if data_dict['locked']==False:
            dummy={'time_in':datetime.datetime.now().time()}
            db.child("logs").child(data_dict['userId']).set(dummy)
            if data_dict['method']=='nfc':
                # send the user id as in payload who used NFC
                sendNotification(payload,3)
            else:
                # normal entry
                sendNotification(payload,2)

    elif topic is "snap/home/door1/auth":
        arr = payload.split("_")
        if arr[1]=='True':
            db_data = {'time_in':datetime.datetime.now().time(), "time_out":""}
            db.child("logs").child(arr[0]).set(db_data)
            db.child("guests").child(arr[0])
    

def sendNotification(some_id,case):
    # API key can be found at firebase console -> Settings -> Cloud messaging -> Server Key
    push_service = FCMNotification(api_key="AAAARXD4tc8:APA91bF--czU1L658-tCk8E4sQaguamIFapxjiZ1pFqzjIPj6j5hG-_yE__DPXLgq_tt_oHmE0fonw1HzpTwy90QMsVv4-okWJqPHZHfsqAtvJFiV902AUm4yQt1bipcETlzL0YsjbWB")
    # Sending to multiple devices using registration ids
    # registration_ids = [] 
    registration_id = "d_Ir6wzFH90:APA91bGTmlb74dx40_L43Njr6tRQCn3z8B07RE7iItvF4e2zeLw7r-hZucMSvCob6HQWCMkwmcpM1yPlEJpNbvx2cPRRaVDj4S4x-c2HrqKvEiDaNqv6V0jPrIgilncceOvwgZ0UCjCK"  
    # Set the notification title and body
    message_title = "Door Notification"
    message_body1 = "Somebody is at your door."
    message_body2 = "User {} has opened the door.".format(some_id)
    message_body3 = "User {} has used the NFC tag.".format(some_id)
    # Create a data message for the client to process data
    data_message = {
        "image_child": some_id
    }
    # Add priority
    extra_kwargs = {
        'priority' : 'high'
    }

    if case == 1:
        # result = push_service.notify_multiple_devices(registration_ids=registration_ids,
        #     message_title=message_title,message_body=message_body1,
        #     data_message=data_message,extra_kwargs=extra_kwargs)
        result = push_service.notify_single_device(registration_id=registration_id,
            message_title=message_title,message_body=message_body1,
            data_message=data_message,extra_kwargs=extra_kwargs)    
    elif case ==2:
        # result = push_service.notify_multiple_devices(registration_ids=registration_ids,
        #     message_title=message_title,message_body=message_body2,
        #     data_message=data_message,extra_kwargs=extra_kwargs)
        result = push_service.notify_single_device(registration_id=registration_id,
            message_title=message_title,message_body=message_body2,
            data_message=data_message,extra_kwargs=extra_kwargs)  
    else:
        # result = push_service.notify_multiple_devices(registration_ids=registration_ids,
        #     message_title=message_title,message_body=message_body3,
        #     data_message=data_message,extra_kwargs=extra_kwargs)
        result = push_service.notify_single_device(registration_id=registration_id,
            message_title=message_title,message_body=message_body3,
            data_message=data_message,extra_kwargs=extra_kwargs)  

    print(result)

# add logic to trust the android client


if __name__ == '__main__':
    socketio.run(app, debug=True)