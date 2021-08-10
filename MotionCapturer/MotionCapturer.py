#Copyright © 2018 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# OptiTrack NatNet direct depacketization sample for Python 3.x
#
# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.
import socket
import pymysql
import time
import math
import numpy
import struct

from NatNetClient import NatNetClient

def floatToBytes(f):
    bs = struct.pack("f",f)
    print("pkg:",bs[0])
    print("pkg:",bs[1])
    print("pkg:",bs[2])
    print("pkg:",bs[3])
    print("b="+str(bs))
    return bs


#client 发送端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PORT = 1324
count=0
now_t=0

#global command=''
mcapPosition=(0,0,0)
mcapRotation=(0,0,0,0)


#The origin of the pool
origin = (1625,300,-287)

# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
	Received=""
	#print( "Received frame", frameNumber )

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
	global count
	global now_t
	
	global mcapPosition
	global mcapRotation
	
	if id==21:
		print(id)
		mcapPosition=position
		mcapRotation=rotation
		
# 	try:
# 		db=pymysql.connect("10.60.18.38","root","root","star")
# 	except:
# 		time.sleep(0.01)      #加大采样频率 保证实时性； 单位 秒
# 		db=pymysql.connect("10.60.18.38","root","root","star")
	
	#print("rotation: " + str(mcapRotation))
	count+=1
	if (1)==1:
		last_t=now_t
		now_t = time.time()  #获取当前时间
		print(now_t-last_t)
		
		bytes_d=floatToBytes(1.23456)
		start1=bytes(0xAA)
		start2=bytes(0xAF)
		msg=start1#(start1+start2+bytes_d+bytes_d+bytes_d)
		server_address = ("192.168.3.11", PORT)    # 接收方 服务器的ip地址和端口号
		client_socket.sendto(msg, server_address) # 将msg内容发送给指定接收方
		print("run_count: ",count)
		#print("  position: " + str(mcapPosition))
		#print("\n")
		
	

# This will create a new NatNet client
streamingClient = NatNetClient()
streamingClient.localIPAddress="192.168.3.10"

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()


