import paho.mqtt.client as mqtt
from time import sleep

broker_address="172.16.73.39"
port=8883

def on_connect(client,userdata,flags,rc):
    print("Connected to broker")

def on_disconnect(client,userdata,rc=0):
    print("Disconnected")

def on_message(client, userdata, message):
    topic=message.topic
    payload=message.payload.decode("utf-8")

    if topic == "snap/home/door1/image":
        # Send the notification with Image src
        #sendNotification(payload ,1)
        print(payload)
    
    # elif topic == "snap/home/door1/user/android":
    #     print(payload)
    #     # 1st time configuration
    #     # send the key to the device and android
    #     random_key = random.getrandbits(128)
    #     # send the userId to device
    #     #data_publish = json.dumps({'topic': 'snap/home/door1/user','message': payload,'qos':'2'})
    #     #socketio.emit("publish",data=data_publish)
    #     # publish the random generated key to MQTT
    #     #data_publish = json.dumps({'topic': 'snap/home/door1/key','message': str(random_key),'qos':'2'})
    #     #socketio.emit("publish",data=data_publish)
    
    # elif topic == "snap/home/door1/status":
    #     #store the locked value in fireabse to show on android
    #     # data_dict = json.loads(payload)
    #     pass
       

    # elif topic == "snap/home/door1/auth":
    #     # data_dict=json.loads(payload)
    #     auth_arr=payload.split('_')
    #     if auth_arr[1]=='True':
    #         db_data = {'time_in':datetime.datetime.now().time(), "time_out":""}
    #         db.child("logs").child(auth_arr[0]).set(db_data)
    #         db.child("guests").child(auth_arr[0]

if __name__=='__main__':
    client=mqtt.Client("Flask_mqtt")
    client.tls_set('/Users/apple/Desktop/Akhil/assets/ca.crt')
    client.on_connect=on_connect
    client.on_message=on_message
    client.on_disconnect=on_disconnect 
    client.connect(broker_address,port)
    #client.subscribe('snap/home/door1/status')
    #client.loop_start()
    client.subscribe('snap/home/door1/image')
    #client.loop_stop()
    #client.subscribe('snap/home/door1/auth')
    client.loop_forever()