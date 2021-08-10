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

#
servo_up = 3450
servo_low = 2800

class OASES():
    
    def __init__(self):
        # open serial
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
        #self.ser.open()
        
        # intial variable
        self.thruster_speed = [stop, stop, stop, stop]
        
        #self.servo_pos = [self.inquiry_servo(1), self.inquiry_servo(2), \
        #                  self.inquiry_servo(3), self.inquiry_servo(4)]
        self.servo_pos = [servo_low, servo_low, servo_low, servo_low]
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
            self.ser.write(('R'+str(int(servo_index))+'E').encode('utf-8'))
            recv_data = self.ser.read(1024).decode()
            print(recv_data)
            if bool(re.search(r'\d', recv_data)):
                servo_position = int(re.findall(r'\d+', recv_data)[0])
                if servo_position >= servo_low and servo_position <= servo_up: 
                    known = True
                    return servo_position
    
    def servo(self, a_data, b_data, c_data, d_data):
        time.sleep(0.01)
        print('D' + str(a_data).zfill(4) + str(b_data).zfill(4) + str(c_data).zfill(4) + str(d_data).zfill(4) +'E')
        self.ser.write(('D' + str(a_data).zfill(4) + str(b_data).zfill(4) + str(c_data).zfill(4) + str(d_data).zfill(4) +'E').encode('utf-8'))
    
    def propeller(self, e_data, f_data, g_data, h_data):
        #time.sleep(0.01)
        #print('T' + str(e_data).zfill(4) + str(f_data).zfill(4) + str(g_data).zfill(4) + str(h_data).zfill(4) +'E')
        #self.ser.write(('T' + str(e_data).zfill(4) + str(f_data).zfill(4) + str(g_data).zfill(4) + str(h_data).zfill(4) +'E').encode('utf-8'))
        #self.ser.write(('T' + str(e_data).zfill(4) + 'E').encode('utf-8'))
        t = 0.02
        time.sleep(t)
        self.ser.write('T'.encode('utf-8'))
        time.sleep(t)
        self.ser.write(str(e_data).zfill(4).encode('utf-8'))
        time.sleep(t)
        self.ser.write(str(f_data).zfill(4).encode('utf-8'))
        time.sleep(t)
        self.ser.write(str(g_data).zfill(4).encode('utf-8'))
        time.sleep(t)
        self.ser.write(str(h_data).zfill(4).encode('utf-8'))
        time.sleep(t)
        self.ser.write('E'.encode('utf-8'))
        
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
            if i > servo_up:
                i = servo_up
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
    def contract(self):
        self.servo_pos = [i - 10 for i in self.servo_pos]
        for i in self.servo_pos:
            if i < servo_low:
                i = servo_low
        self.servo(self.servo_pos[0], self.servo_pos[1], 
                   self.servo_pos[2], self.servo_pos[3])
        
        