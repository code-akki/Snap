#!/usr/bin/python3
# python code for interfacing to VC0706 cameras and grabbing a photo
# pretty basic stuff
# written by ladyada. MIT license
# revisions for Raspberry Pi by Gordon Rush
# revisions for Raspberry Pi 2 Python 3 by Dipto Pratyaksa

import serial 
import array
from datetime import datetime
import paho.mqtt.client as mqtt
import pyrebase
import random

import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BOARD)
GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_UP)

broker_address='172.16.73.4'
port=1883
config ={
    "apiKey": "AIzaSyDpXXiXKrHB4EX0WtrrLGVaCxiJInEHToE",
    "authDomain":"snap-8a7b3.firebaseapp.com",
    "databaseURL": "https://snap-8a7b3.firebaseio.com",
    "projectId": "snap-8a7b3",
    "storageBucket":"snap-8a7b3.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db= firebase.database()
BAUD = 38400
# this is the port on the Raspberry Pi; it will be different for serial ports on other systems.
PORT = "/dev/ttyAMA0"

TIMEOUT = 0.5    # I needed a longer timeout than ladyada's 0.2 value
SERIALNUM = 0    # start with 0, each camera should have a unique ID.

COMMANDSEND = 0x56
COMMANDREPLY = 0x76
COMMANDEND = 0x00

CMD_GETVERSION = 0x11
CMD_RESET = 0x26
CMD_TAKEPHOTO = 0x36
CMD_READBUFF = 0x32
CMD_GETBUFFLEN = 0x34

FBUF_CURRENTFRAME = 0x00
FBUF_NEXTFRAME = 0x01

FBUF_STOPCURRENTFRAME = 0x00

VC0706_640x480=0x00
VC0706_320x240=0x11
VC0706_160x120=0x22

VC0706_READ_DATA=0x30
VC0706_WRITE_DATA=0x31

getversioncommand = [COMMANDSEND, SERIALNUM, CMD_GETVERSION, COMMANDEND]
resetcommand = [COMMANDSEND, SERIALNUM, CMD_RESET, COMMANDEND]
takephotocommand = [COMMANDSEND, SERIALNUM, CMD_TAKEPHOTO, 0x01, FBUF_STOPCURRENTFRAME]
getbufflencommand = [COMMANDSEND, SERIALNUM, CMD_GETBUFFLEN, 0x01, FBUF_CURRENTFRAME]

s = serial.Serial( PORT, baudrate=BAUD, timeout = TIMEOUT )

def on_connect(client,userdata,flags,rc):
        print('CameraModule connected.')

def on_publish(client,userdata,mid):
        print('sent reference id.')

def on_disconnect(client, userdata, rc=0):
        client.loop_stop()

def checkreply(r, b):
	r = list(r)
#	string= u''.join(r).encode('utf-8').strip()
	string = ''.join(list(map(chr,r)))
	try:
		if(len(r)<100):
#			print("the reply:",r)
			print(string[3:])
	except Exception as e:
		print(e)
#		print(string[3:])
#		print("The commmand = " ,b)
	if(r[0] == COMMANDREPLY and r[1] == SERIALNUM and r[2] == b and r[3] == 0x00):
		return True
	return False

def reset():
	cmd = ''.join( list(map( chr, resetcommand )) )
	s.write(bytes(cmd,"UTF-8"))
	reply = s.read(100)
	r = list(reply)
	if checkreply( r, CMD_RESET ):
		return True
	return False

def getversion():
	cmd = ''.join( list(map( chr, getversioncommand )))
	s.write(bytes(cmd,"UTF-8"))
	reply = s.read(17)
	r = list(reply)
#	print (r)
	if checkreply( r, CMD_GETVERSION ):
#		print (r)
		return True
	return True

def setsize(size):
	setsizecommand =  [COMMANDSEND, SERIALNUM, VC0706_WRITE_DATA,0x05, 0x04, 0x01, 0x00, 0x19, size]

	
	cmd = ''.join( list(map( chr, setsizecommand )))
	s.write(bytes(cmd,"UTF-8"))
	print("settting size" , cmd)
	reply = s.read(17)
	r = list(reply)
	print ("setting size", r)
	if checkreply( r, CMD_GETVERSION ):
#               print (r)
        	return True
	return True


def takephoto():
	cmd = ''.join( list(map( chr, takephotocommand )))
	s.write(bytes(cmd,"UTF-8"))
	reply = s.read(5)
	r = list(reply)
	# print r
	if( checkreply( r, CMD_TAKEPHOTO) and r[3] == int(0x0)):
		return True
	return False

def getbufferlength():
	cmd = ''.join( list(map( chr, getbufflencommand )))
	s.write(bytes(cmd,"UTF-8"))
	reply = s.read(10)
	r = list(reply)
#	print("buffer length", r)

	if( checkreply( r, CMD_GETBUFFLEN) and r[4] == int(0x4)):
		l = r[5]
		l <<= 8
		l += r[6]
		l <<= 8
		l += r[7]
		l <<= 8
		l += r[8]
		return l
	return 0

readphotocommand = [COMMANDSEND, SERIALNUM, CMD_READBUFF, 0x0c, FBUF_CURRENTFRAME, 0x0a]


def readbuffer(bytes):
	addr = 0   # the initial offset into the frame buffer
	photo = []

	# bytes to read each time (must be a mutiple of 4)
	inc = 8192

	while( addr < bytes ):
 		# on the last read, we may need to read fewer bytes.
		chunk = min( bytes-addr, inc );

		# append 4 bytes that specify the offset into the frame buffer
		command = readphotocommand + [(addr >> 24) & 0xff, 
				(addr>>16) & 0xff, 
				(addr>>8 ) & 0xff, 
				addr & 0xff]

		# append 4 bytes that specify the data length to read
		command += [(chunk >> 24) & 0xff, 
				(chunk>>16) & 0xff, 
				(chunk>>8 ) & 0xff, 
				chunk & 0xff]

		# append the delay
		command += [1,0]

	#	print(map(hex, command))
		print ("Reading", chunk, "bytes at", addr)

		# make a string out of the command bytes.
#		cmd = ''.join(list(command))
		cmd = array.array('B', command).tostring()
#		s.write(bytes(cmd,"UTF-8"))
		s.write(cmd)

		# the reply is a 5-byte header, followed by the image data
		#   followed by the 5-byte header again.
		reply = s.read(5+chunk+5)

 		# convert the tuple reply into a list
		r = list(reply)
		if( len(r) != 5+chunk+5 ):
			# retry the read if we didn't get enough bytes back.
			print ("Read", len(r), "Retrying.")
			continue

		if( not checkreply(r, CMD_READBUFF)):
			print ("ERROR READING PHOTO")
			return False
		
		# append the data between the header data to photo
		photo += r[5:chunk+5]

		# advance the offset into the frame buffer
		addr += chunk
		print("saving" ,addr, "bytes")

	print (addr, "Bytes written")
	return photo


######## main
def shootlo():

#reset()

	if( not getversion() ):
		print ("Camera not found")
		exit(0)

	print ("VC0706 Camera found")

#setsize(VC0706_640x480)
#	setsize(VC0706_320x240)
	setsize(VC0706_160x120)

	reset()

	if takephoto():
		print ("Snap!")

	bytes_to_read = getbufferlength()

	print (bytes_to_read, "bytes to read")

#bts = array.array('B', bytes_to_read).tostring()
	photo = readbuffer( bytes_to_read )

	foldername = "lowres"

	filename = "photo_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"

	fullpath = foldername+"/"+filename
	f = open(fullpath, 'wb' )

#photodata = ''.join( photo )
	photodata = array.array('B', photo).tostring()

	f.write( photodata )

	f.close()
	return fullpath

def shoothi(pathname):

#reset()

	if( not getversion() ):
		print ("Camera not found")
		exit(0)

	print ("VC0706 Camera found")

	setsize(VC0706_640x480)
#       setsize(VC0706_320x240)
#        setsize(VC0706_160x120)

	reset()

	if takephoto():
		print ("Snap!")

	bytes_to_read = getbufferlength()
	
	print (bytes_to_read, "bytes to read")

#bts = array.array('B', bytes_to_read).tostring()
	photo = readbuffer( bytes_to_read )

	foldername = "/home/pi/Desktop/Snap/RaspberryPi/images"

	filename = "photo_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"

	fullpath = foldername+"/"+filename
	f = open(pathname, 'wb' )
	#f = open("test.jpg","wb")
	

#photodata = ''.join( photo )
	photodata = array.array('B', photo).tostring()

	f.write( photodata )

	f.close()
	return fullpath


if __name__ =="__main__":
	s = serial.Serial( PORT, baudrate=BAUD, timeout = TIMEOUT )
	client=mqtt.Client('CameraMqtt')
	#client.tls_set("/home/pi/Desktop/Snap/assets/ca.crt")
	client.on_connect=on_connect
	client.on_publish=on_publish
	client.on_disconnect=on_disconnect
	client.connect(broker_address,port)
	#shootlo()
	while True:
                button_state=GPIO.input(23)
                if button_state ==False:
                        print('button pressed.')
                        rand_guestid=str(random.getrandbits(64))
                        shoothi('/home/pi/Desktop/Snap/RaspberryPi/images/{}.jpg'.format(rand_guestid))
                        storage=firebase.storage()
                        storageRef='visitors/{}.jpg'.format(rand_guestid)
                        storage.child(storageRef).put('/home/pi/Desktop/Snap/RaspberryPi/images/{}.jpg'.format(rand_guestid))
                        print("Reference {}".format(rand_guestid))
                        client.loop_start()
                        client.publish('snap/home/door1/image',str(storageRef))
                        client.publish('snap/home/door1/auth',rand_guestid+"_False")
