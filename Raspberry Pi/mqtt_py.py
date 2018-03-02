import paho.mqtt.client as mqtt
import time
import json

broker_address="172.16.73.39"
port=8883

#/snap/home/door1/status payload {locked: boolean, userId: userid, method: nfc/android} sub pub
#/snap/home/door1/auth {guesid:guestid, auth: boolean} sub
#/snap/home/door1/user sub
#/snap/home/door1/images pub
#/snap/hoome/door1/key sub


def on_connect(client, userdata, flags, rc):
    print "Connected"

def on_message(client, userdata,  message):
    print "on_message"
    print "message received", str(message.payload.decode("utf-8"))
    print "message topic", message.topic

def status_callback(client, userdata, message):
    print "status-callback"
    print "message received", str(message.payload.decode("utf-8"))
    print "message topic", message.topic
def auth_callback(client, userdata, message):
    print "auth_callback", str(message.payload.decode("utf-8"))
    print "on_message"
    print "message topic", message.topic
    
def on_disconnect(client, userdata, rc=0):
    client.loop_stop()

#def on_publish(client, ):
    
    
client = mqtt.Client("Rasp")
client.tls_set("/home/pi/Desktop/Snap/assets/ca.crt")
client.on_connect = on_connect
client.message_callback_add("status",status_callback)
client.message_callback_add("auth",auth_callback)
client.on_message=on_message
client.on_disconnect=on_disconnect
client.connect(broker_address,port)
client.loop_start()
#print "Subscribing to topic: ", "test"
client.subscribe("#")
#client.loop_forever()
#dict_data={'topic': 'test', 'payload': 'Hello', 'qos': 2 }
#json_data=json.dumps(data_dict)
#print "Publsihing to topic: ", ""
#client.publish("mqtt","hello")
time.sleep(10000)
client.loop_stop()

