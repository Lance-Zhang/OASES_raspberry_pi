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
        
        #self.servo_pos = self.inquiry_all_servo()
        self.servo_pos = [servo_bound[0], servo_bound[0], servo_bound[0], servo_bound[0]]
        print("The initial values of servo motors are:")
        print(self.servo_pos)
        
    # motors control
    def inquiry_servo(self, servo_index):
        if servo_index == 1:
            ser = self.ser1
        elif servo_index >= 2 and servo_index <= 4:
            ser = self.ser2
        else:
            print ("No such servo motor!")
            return -1
        
        known = False
        while not known:
            ser.write(bytes.fromhex(bytes([253, servo_index, 0, 0, 0, 250]).hex()))
            recv_data = ser.read(1024).decode()
            print(recv_data)
            if bool(re.search(r'\d', recv_data)):
                servo_position = int(re.findall(r'\d+', recv_data)[0])
                if servo_position >= servo_bound[0] and servo_position <= servo_bound[1]: 
                    known = True
                    return servo_position
        
        
    def inquiry_all_servo(self):
        # 1 
        recv_msgs = []
        self.ser1.write(bytes.fromhex(bytes([253, 1, 0, 0, 0, 250]).hex()))
        recv_msgs.append(self.ser1.read(1024).decode())
        # 2,3,4
        for i in range(3):
            self.ser2.write(bytes.fromhex(bytes([253, i+2, 0, 0, 0, 250]).hex()))
            recv_msgs.append(self.ser2.read(1024).decode())
        print(recv_msgs)
        #
        servo_position = []
        for recv_data in recv_msgs:
            if bool(re.search(r'\d', recv_data)):
                one_servo_position = int(re.findall(r'\d+', recv_data)[0])
                if one_servo_position >= servo_bound[0] and one_servo_position <= servo_bound[1]: 
                    servo_position.append(one_servo_position)
        print(servo_position)
        return servo_position
        
    def servo(self, a_data, b_data, c_data, d_data):
        self.servo_pos = [a_data, b_data, c_data, d_data]
        a_data = (a_data - servo_bound[0]) / 10
        b_data = (b_data - servo_bound[0]) / 10
        c_data = (c_data - servo_bound[0]) / 10
        d_data = (d_data - servo_bound[0]) / 10
        print(bytes([254, a_data, b_data, c_data, d_data, 250]).hex())
        time.sleep(0.005)
        self.ser1.write(bytes.fromhex(bytes([254, a_data, 0, 0, 0, 250]).hex())) # head: 254 0xff, tail: 250 0xfa
        self.ser2.write(bytes.fromhex(bytes([254, b_data, c_data, d_data, 250]).hex())) # head: 254 0xff, tail: 250 0xfa
    
    def propeller(self, e_data, f_data, g_data, h_data):
        if e_data != self.thruster_speed[0] or f_data != self.thruster_speed[1] or g_data != self.thruster_speed[2] or h_data != self.thruster_speed[3]:
            self.thruster_speed = [e_data, f_data, g_data, h_data]
            e_data = e_data - prop_bound[0]
            f_data = f_data - prop_bound[0]
            g_data = g_data - prop_bound[0]
            h_data = h_data - prop_bound[0]
            print(bytes([255, e_data, f_data, g_data, h_data, 250]).hex())
            time.sleep(0.005)
            self.ser1.write(bytes.fromhex(bytes([255, e_data, f_data, g_data, h_data, 250]).hex())) # head: 255 0xff, tail: 250 0xfa
        
    def update_servo_position(self):
        self.servo_pos = [self.inquiry_servo(1), self.inquiry_servo(2), \
                          self.inquiry_servo(3), self.inquiry_servo(4)]
    
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
        for i in self.servo_pos:
            if i > servo_bound[1]:
                i = servo_bound[1]
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
    def contract(self):
        self.servo_pos = [i - 10 for i in self.servo_pos]
        for i in self.servo_pos:
            if i < servo_bound[0]:
                i = servo_bound[0]
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
        