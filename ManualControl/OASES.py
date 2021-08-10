# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 21:32:37 2020

@author: CUHKSZ

Servo: A:2, B:4, C:3, D:1,
value:2800~3450,
resolution = 10

Propeller: E:2, F:1, G:3, H:4,
value:0~180

192.168.3.3
80

"""
import time
import re
import socket
import serial

#
push_forward = 60
push_back = 120
stop = 90

#
servo_bound = [2800, 3450]
prop_bound = [40, 140]

class OASES():
    def __init__(self):
        # open serial
        self.ser1 = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5) # 4 propellers, 1 servo
        self.ser2 = serial.Serial('/dev/ttyUSB1', 115200, timeout=0.5) # 3 servo
        
        # intial variable
        self.thruster_speed = [0, 0, 0, 0]
        
        self.servo_pos = [servo_bound[0], servo_bound[0], servo_bound[0], servo_bound[0]]
        self.inquiry_all_servo()
        
        print("The initial values of servo motors are:")
        print(self.servo_pos)
        
    # motors control
    def inquiry_servo(self, servo_index):
        #s = time.time()
        if servo_index == 1:
            ser = self.ser1
            #print(bytes([253, servo_index, 0, 0, 0, 250]).hex())
            ser.write(bytes.fromhex(bytes([253, servo_index, 0, 0, 0, 250]).hex()))
        elif servo_index >= 2 and servo_index <= 4:
            ser = self.ser2
            #print(bytes([253, servo_index, 0, 0, 250]).hex())
            ser.write(bytes.fromhex(bytes([253, servo_index, 0, 0, 250]).hex()))
        else:
            print ("No such servo motor!")
            return -1
        #time.sleep(0.5)
        servo_position = ""
        for i in range(100): 
            #print("Waiting servo position ......")
            servo_position = ser.readline().decode()
            if len(servo_position):
                break
        #print(servo_position)
        servo_load = ""
        for i in range(10):  
            #print("Waiting servo load ......")
            servo_load = ser.readline().decode()
            if len(servo_load):
                break
        #print(servo_load)
        if bool(re.search(r'\d', servo_position)) and bool(re.search(r'\d', servo_load)):
            servo_position = int(re.findall(r'-?\d+', servo_position)[0])
            servo_load = int(re.findall(r'-?\d+', servo_load)[0])
            if servo_position >= servo_bound[0] and servo_position <= servo_bound[1]:
                #print(time.time()-s)
                self.servo_pos[servo_index - 1] = servo_position
                return servo_position, servo_load
            else:
                return -1, -1
            
    def inquiry_all_servo(self):
        #s = time.time()
        # 1 
        servo1 = self.inquiry_servo(1) # pos, load
        # 2,3,4
        self.ser2.write(bytes.fromhex(bytes([253, 2, 3, 4, 250]).hex()))
        pos_msgs = []
        load_msgs = []
        for i in range(3):
            pos_msg = ""
            for i in range(10):   
                pos_msg = self.ser2.readline().decode()
                if len(pos_msg):
                    break
            pos_msgs.append(pos_msg)
            load_msg = ""
            for i in range(10): 
                load_msg = self.ser2.readline().decode()
                if len(load_msg):
                    break
            load_msgs.append(load_msg)
        #print(pos_msgs)
        #print(load_msgs)
        #
        servo_pos_list = [servo1[0]]
        for pos_msg in pos_msgs:
            if bool(re.search(r'\d', pos_msg)):
                one_servo_position = int(re.findall(r'-?\d+', pos_msg)[0])
                if one_servo_position >= servo_bound[0] and one_servo_position <= servo_bound[1]: 
                    servo_pos_list.append(one_servo_position)
        servo_load_list = [servo1[1]]
        for load_msg in load_msgs:
            if bool(re.search(r'\d', load_msg)):
                one_servo_load = int(re.findall(r'-?\d+', load_msg)[0])
                servo_load_list.append(one_servo_load)
        #print(servo_pos_list)
        #print(servo_load_list)
        #print(time.time()-s)
        self.servo_pos = servo_pos_list
        return servo_pos_list, servo_load_list
        
    def servo(self, a_data, b_data, c_data, d_data):
        self.servo_pos = [a_data, b_data, c_data, d_data]
        a_data = int((a_data - servo_bound[0]) / 10) + 1
        b_data = int((b_data - servo_bound[0]) / 10) + 1
        c_data = int((c_data - servo_bound[0]) / 10) + 1
        d_data = int((d_data - servo_bound[0]) / 10) + 1
        print("Servo: ", bytes([254, a_data, b_data, c_data, d_data, 250]).hex())
        #time.sleep(0.005)
        self.ser1.write(bytes.fromhex(bytes([254, a_data, 0, 0, 0, 250]).hex())) # head: 254 0xff, tail: 250 0xfa
        self.ser2.write(bytes.fromhex(bytes([254, b_data, c_data, d_data, 250]).hex())) # head: 254 0xff, tail: 250 0xfa
    
    def propeller(self, e_data, f_data, g_data, h_data):
        if e_data != self.thruster_speed[0] or f_data != self.thruster_speed[1] or g_data != self.thruster_speed[2] or h_data != self.thruster_speed[3]:
            self.thruster_speed = [e_data, f_data, g_data, h_data]
            e_data = e_data - prop_bound[0]
            f_data = f_data - prop_bound[0]
            g_data = g_data - prop_bound[0]
            h_data = h_data - prop_bound[0]
            print("Propeller: ", bytes([255, e_data, f_data, g_data, h_data, 250]).hex())
            time.sleep(0.005)
            self.ser1.write(bytes.fromhex(bytes([255, e_data, f_data, g_data, h_data, 250]).hex())) # head: 255 0xff, tail: 250 0xfa
    
    # movement
    def forward(self):
        self.propeller(stop, push_forward, stop, push_forward)
        
    def backward(self):
        self.propeller(stop, push_back, stop, push_back)
        
    def leftward(self):
        self.propeller(push_back, stop, push_back, stop)
        
    def rightward(self):
        self.propeller(push_forward, stop, push_forward, stop)

    def turnleft(self):
        #self.propeller(push_forward, push_forward, push_back, push_back)
        #self.propeller(push_forward, stop, push_back, stop)
        self.propeller(stop, push_forward, stop, push_back)
        
    def turnright(self):
        #self.propeller(push_back, push_back, push_forward, push_forward)
        #self.propeller(push_back, stop, push_forward, stop)
        self.propeller(stop, push_back, stop, push_forward)
        
    def stop(self):
        self.propeller(stop,stop,stop,stop)
        #self.propeller(0,0,0,0)

    # shape shifting
    def extend(self):
        self.servo_pos = [i + 10 for i in self.servo_pos]
        for i in range(len(self.servo_pos)):
            if self.servo_pos[i] < servo_bound[0]:
                self.servo_pos[i] = servo_bound[0]
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
    def contract(self):
        self.servo_pos = [i - 10 for i in self.servo_pos]
        for i in range(len(self.servo_pos)):
            if self.servo_pos[i] < servo_bound[0]:
                self.servo_pos[i] = servo_bound[0]
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
# Test script
if __name__ == "__main__":
    #
    USV = OASES()
    #USV.inquiry_servo(1)
    #USV.inquiry_all_servo()