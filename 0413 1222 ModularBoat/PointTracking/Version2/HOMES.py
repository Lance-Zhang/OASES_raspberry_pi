# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 21:32:37 2020

@author: CUHKSZ

Servo: A:2, B:4, C:3, D:1, value:800~1550
Propeller: E:2, F:1, G:3, H:4, value:0~180

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

class HOMES():
    
    def __init__(self):
        # open serial
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
        #self.ser.open()
        
        # intial variable
        self.thruster_speed = [90, 90, 90, 90]
        
        #self.servo_pos = [self.inquiry_servo(1), self.inquiry_servo(2), \
        #                  self.inquiry_servo(3), self.inquiry_servo(4)]
        self.servo_pos = [800, 800, 800, 800]
        print("The initial values of servo motors are:")
        print(self.servo_pos)
        
    # motors control
    def inquiry_servo(self, servo_index):
        if servo_index >= 1 and servo_index <= 4:
            known = False
        else:
            print ("No such servo motor!")
            return 0
        
        while not known:
            self.ser.write(('R'+str(int(servo_index))).encode('utf-8'))
            recv_data = self.ser.read(1024).decode()
            print(recv_data)
            if bool(re.search(r'\d', recv_data)):
                servo_position = int(re.findall(r'\d+', recv_data)[0])
                if servo_position >= 700 and servo_position <= 1550: 
                    known = True
                    return servo_position
    
    def servo(self, a_data, b_data, c_data, d_data):
        self.ser.write(('A'+str(a_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
        self.ser.write(('B'+str(b_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
        self.ser.write(('C'+str(c_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
        self.ser.write(('D'+str(d_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
    
    def propeller(self, e_data, f_data, g_data, h_data):
        self.ser.write(('E'+str(e_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
        self.ser.write(('F'+str(f_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
        self.ser.write(('G'+str(g_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
        self.ser.write(('H'+str(h_data)+'\n').encode('utf-8'))
        time.sleep(0.1)
    
    def update_servo_position(self):
        self.servo_pos = [self.inquiry_servo(1), self.inquiry_servo(2), \
                          self.inquiry_servo(3), self.inquiry_servo(4)]
    
    # movement
    def forward(self):
        self.propeller(push_forward, stop, stop, push_forward)
        
    def backward(self):
        self.propeller(push_back, stop, stop, push_back)
        
    def leftward(self):
        self.propeller(stop, push_forward, push_forward, stop)
        
    def rightward(self):
        self.propeller(stop, push_back, push_back, stop)
        
    def turnleft(self):
        self.propeller(push_forward, push_back, push_forward, push_back)
        
    def turnright(self):
        self.propeller(push_back, push_forward, push_back, push_forward)
        
    def stop(self):
        self.propeller(stop,stop,stop,stop)
        
    # shape shifting
    def extend(self):
        self.servo_pos = [i + 10 for i in self.servo_pos]
        for i in self.servo_pos:
            if i > 1550:
                i = 1550
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
    def contract(self):
        self.servo_pos = [i - 10 for i in self.servo_pos]
        for i in self.servo_pos:
            if i < 800:
                i = 800
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
        