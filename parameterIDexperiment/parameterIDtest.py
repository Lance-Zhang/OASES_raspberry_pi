# -*- coding: utf-8 -*-
"""

@author: CUHKSZ

ip: 192.168.3.10
port: 80
"""

##### parameters #####
File_name = 'sine'
Power_Meter_port = 'COM7'

Server_address = "192.168.3.10" # for robot localization

# PWM
PWM_forward = 60
PWM_backward = 120
PWM_stop = 90


# new a data file
import csv
f = open(File_name + '.csv','w', encoding='utf-8', newline="")
csv_writer = csv.writer(f)
csv_writer.writerow(["Time", "Voltage", "PWM1", "PWM2", "PWM3", "PWM4", "X", "Y", "W"])

##### read the voltage #####
import serial
import time
import binascii

Voltage_preset = 12.3
waiting_time = 0.05 # (second) if smaller, there might be lost data
Voltage = 0.0
def voltage_threading():
    global Voltage
    try:
        # open the power meter serial port
        power_meter = serial.Serial(Power_Meter_port,9600)
        power_inquiry = bytes.fromhex('01 03 00 00 00 03 05 CB') # voltage, current, power
        power_meter.write(power_inquiry)
        
        time.sleep(waiting_time)
        
        # read current data
        n = power_meter.inWaiting()
        if n: 
            power_data= str(binascii.b2a_hex(power_meter.read(n)))[8:-5]
            try:
                voltage = int(power_data[0:4], 16)/10000*60
            except:
                voltage = 0.0
            print("voltage: ", voltage)
            
    except Exception as e:
        voltage = Voltage_preset
        print("---ERROR---：",e)




##### robot localization #####
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
server_socket.bind(("192.168.3.10", 8000)) 
server_socket.settimeout(10) 

State = [0,0,0]
def pos_threading():
    global State
    while True:
      try:  
          now = time.time() 
          receive_data, client = server_socket.recvfrom(1024)
          receive_data = receive_data.decode()
          #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(now))) #以指定格式显示时间
          #print("来自客户端%s,发送的%s\n" % (client, receive_data))  #打印接收的内容
          State = [float(s) for s in re.findall(r'[-+]?\d+\.?\d*', receive_data)]   
      except socket.timeout:  #如果10秒钟没有接收数据进行提示（打印 "time out"）
          print('time out')
      

##### start test #####
import sys
import math
import pygame
from OASES import OASES

# create the boat
Boat = OASES(PWM_forward, PWM_backward, PWM_stop)
print("Init HOMES boat.")

# initial pygame
pygame.display.set_caption("PyGame")
pygame.display.set_mode((640, 480))
pygame.init()
print("Init Pygame.")

# catch keyboard event
Flag = True
PWM_command = [0, 0, 0, 0]
long_press = {'W': False, 'S': False, 'A': False, 'D': False, 
              'I': False, 'J': False, 'K': False, 'L': False} # For movement and action

while Flag:
    
    for event in pygame.event.get():
        # if event.type == QUIT:
            # sys.exit()
        # print("event get")
        
        # press key
        if event.type == pygame.KEYDOWN:
            # quit
            if event.key == pygame.K_q:
                print("Quit manual control.")
                Flag = False
                f.close()
                
                Boat.reset()
                pygame.quit()
                sys.exit()
                break
            
            if event.key == pygame.K_u:
                print("Update servo motor position.")
                Boat.update_servo_position()
            
            if event.key == pygame.K_w:
                long_press['W'] = True
            if event.key == pygame.K_a:
                long_press['A'] = True
            if event.key == pygame.K_s:
                long_press['S'] = True
            if event.key == pygame.K_d:
                long_press['D'] = True
            if event.key == pygame.K_i:
                long_press['I'] = True
            if event.key == pygame.K_j:
                long_press['J'] = True
            if event.key == pygame.K_k:
                long_press['K'] = True
            if event.key == pygame.K_l:
                long_press['L'] = True
            if event.key == pygame.K_r:
                Boat.reset()
                print("Reset boat.")
                
                
        # release key
        if event.type == pygame.KEYUP:
            
            if event.key == pygame.K_w:
                long_press['W'] = False
            if event.key == pygame.K_a:
                long_press['A'] = False
            if event.key == pygame.K_s:
                long_press['S'] = False
            if event.key == pygame.K_d:
                long_press['D'] = False
            if event.key == pygame.K_i:
                long_press['I'] = False
            if event.key == pygame.K_j:
                long_press['J'] = False
            if event.key == pygame.K_k:
                long_press['K'] = False
            if event.key == pygame.K_l:
                long_press['L'] = False
            
    # handle the keyboard event
    if long_press['W'] == True:
        PWM_command = Boat.forward()
        print("Forward.")
    if long_press["S"] == True:
        PWM_command = Boat.backward()
        print("Backward.")
    if long_press["A"] == True:
        PWM_command = Boat.leftward()
        print("Leftward.")
    if long_press["D"] == True:
        PWM_command = Boat.rightward()
        print("Rightward.")
        
    if long_press['J'] == True:
        PWM_command = Boat.turnleft()
        print("Turn left.")
    if long_press["L"] == True:
        PWM_command = Boat.turnright()
        print("Turn right.")

    if long_press["I"] == True:
        Boat.extend()
        print("Extend.")
    if long_press["K"] == True:
        Boat.contract()
        print("Contract.")
    
    # no key pressed     
    if all(value == 0 for value in long_press.values()):
        PWM_command = Boat.halt()
        print("Boat halts.")
    
    # write to file
    csv_writer.writerow([str(time.time()),str(voltage),
                         str(PWM_command[0]),str(PWM_command[1]),
                         str(PWM_command[2]),str(PWM_command[3]),
                         str(State[0]),str(State[1]),str(State[2])])
    
    # next loop
    pygame.time.delay(1) # delay 10ms 

