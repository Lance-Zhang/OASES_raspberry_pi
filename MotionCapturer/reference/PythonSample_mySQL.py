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

import time
import math
import os
from NatNetClient import NatNetClient



# global command=''
mcap8807=(0,0,0)
mcap2=(0,0,0)
mcap3=(0,0,0)
mcap7=(0,0,0)
mcap8=(0,0,0)
mcap9=(0,0,0)
rot8807=(0,0,0,0)
rot2=(0,0,0,0)
rot3=(0,0,0,0)

mcapPosition=(0,0,0)
mcapRotation=(0,0,0,0)



# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
	Received=""
	#print( "Received frame", frameNumber )

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
	global mcap8807
	global mcap2
	global mcap3
	global mcap7
	global mcap8
	global mcap9
	global rot8807
	global rot2
	global rot3
	if id==11:# we set boat itself as no.1 rigid body
		mcap8807=position
		rot8807=rotation
	if id==2:# we set jib sail as no.2 rigid body
		mcap2=position
		rot2=rotation
	if id==3:# we set main sail as no.3 rigid body
		mcap3=position
		rot3=rotation
	if id==7:# we set buoy as no.7 rigid body
		mcap7=position
		# rot7=rotation
	if id==8:# we set buoy as no.8 rigid body
		mcap8=position
		# rot8=rotation
	if id==9:# we set buoy as no.9 rigid body
		mcap9=position
		# rot9=rotation

	# }
	global mcapPosition
	global mcapRotation
	mcapPosition=mcap8807
	mcapRotation=rot8807
	
	print(mcapPosition)
	print(mcapRotation)



# This function change radians to degree

	

# This will create a new NatNet client
streamingClient = NatNetClient()
streamingClient.localIPAddress="192.168.3.10"

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()


