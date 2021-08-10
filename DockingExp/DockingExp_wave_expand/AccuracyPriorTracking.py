# -*- coding: utf-8 -*-
"""

@author: CUHKSZ

ip: 192.168.3.10
port: 80
"""

# Receive robot state

import re
import threading
import socket 
import time
# PID
import sys
import math
from HOMES import HOMES
from PID import PID
from UDPserver import DockingSystem
# 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
server_socket.bind(("192.168.3.10", 8000)) 
server_socket.settimeout(10)  

State = [0,0,0]
def data_threading():
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

# limit the angle to -180~180
def angle_norm(old_angle): 
    if old_angle > math.pi:
        return old_angle - 2 * math.pi
    elif old_angle <= -math.pi:
        return old_angle + 2 * math.pi
    else:
        return old_angle

# adjust PID to ceiling value
def int_norm(pid_output):
    if pid_output >= 0:
        norm_output = math.ceil(pid_output)
    if pid_output < 0:
        norm_output = int(pid_output)
    return norm_output

def PID_norm(pid_value):
    r = [80, 87, 93, 100]
    norm_output = pid_value
    if pid_value < r[0]:
        norm_output = r[0]
    if pid_value > r[1] and pid_value < 90:
        norm_output = r[1]
    if pid_value > 90 and pid_value < r[2]:
        norm_output = r[2]
    if pid_value > r[3]:
        norm_output = r[3]
    return norm_output

# control thread
def control_threading(target_pos, pid_fb, pid_sd):
    # create the boat
    USV = HOMES()
    print("Init HOMES USV.")
    
    PID_orient_smlangle = PID(20,0,0.5) # adjust the orientation
    PID_orient_midangle = PID(6,0,0.5) 
    PID_orient_bigangle = PID(5,0,0.5)
    
    PID_forback = PID(pid_fb[0],pid_fb[1],pid_fb[2]) # adjust the forward / backward position
    PID_side = PID(pid_sd[0],pid_sd[1],pid_sd[2]) # adjust the sideward position
    print("Init PID.")
    
    sml_angle = 10 * math.pi/180
    big_angle = 90 * math.pi/180
    
    # target point # x, y, attitude : -180~180
    x_t = target_pos[0]
    y_t = target_pos[1]
    yaw_t = target_pos[2] * math.pi/180 # 
    
    # PID setpoint
    PID_orient_smlangle.setGoal(0)
    PID_orient_midangle.setGoal(0)
    PID_orient_bigangle.setGoal(0) 
    PID_forback.setGoal(0)
    PID_side.setGoal(0)
    
    global State
    fp = open("data.txt","w",encoding="utf-8")
    
    reach = False
    while not reach:
        # measurement
        #time.sleep(0.05)
        print('State: ', State[0], State[1], State[2]*180/math.pi)
        x = State[0]
        y = State[1]
        #now = time.time()
        yaw = State[2] 
        
        # heading feed back
        angle_error = angle_norm(yaw - yaw_t) # >0 on the left
        PID_orient_smlangle.update(angle_error) 
        PID_orient_midangle.update(angle_error)
        PID_orient_bigangle.update(angle_error)
        
        # forward, backward feedback
        distance = math.sqrt(math.pow(x - x_t, 2) + math.pow(y - y_t, 2)) # from current to target
        print('distance: ', distance)
        if distance < 0.1 and abs(angle_error) < 10: # < 5cm and < 5 degree
            reach = True
            break
        
        azimuth = math.atan2(y - y_t, x - x_t) # position angle -180~180
        inter_angle = angle_norm(math.pi + yaw - azimuth)
        
        #print('inter angle:  ', inter_angle)
        
        PID_forback.update(distance * math.cos(inter_angle)) # >0 forward
        
        # sideward feedback
        PID_side.update(distance * math.sin(inter_angle)) # >0 rightward
        
        #print('Boat yaw: ', yaw, '   target angle: ', h_angle)    
        
        # execute
        if angle_error > -sml_angle and angle_error < sml_angle:
            control_orient = int_norm(PID_orient_smlangle.output)
        elif angle_error < -big_angle or angle_error > big_angle:
            control_orient = int_norm(PID_orient_bigangle.output)
        else:
            control_orient = int_norm(PID_orient_midangle.output)
        print('rotate: ', control_orient)
        
        
        control_fb = int_norm(PID_forback.output)
        #print('forward/backward: ', control_fb)
        control_side = int_norm(PID_side.output)
        #print('sideward: ', control_side)
        
        pwm_front = PID_norm(90 - control_side - control_orient)
        pwm_back = PID_norm(90 - control_side + control_orient)
        pwm_left = PID_norm(90 + control_fb) #+ control_orient
        pwm_right = PID_norm(90 + control_fb) #- control_orient
        
        fp.write("State: " + str(State) + "\nControl: "
             + str([pwm_front, pwm_back, pwm_left, pwm_right]) + '\n\n')
        
        print("command:  ", pwm_front, pwm_back, pwm_left, pwm_right)
        
        USV.propeller(pwm_right, pwm_back, pwm_front, pwm_left)


def navigation_threading():
    # docker
    DS = DockingSystem('BOAT_1', 2)
    time.sleep(5)
    
    # points
    pid_fb = [[8,0,5],[9,0,5],[9,0,5],[15,0,5],]
    pid_sd = [[8,0,5],[9,0,5],[8,0,5],[13,0,5],]
    
    target_pos = [[-1.78, 1.75, 180],[0.78, -1, 180],[0.78, -1.25, 180],[0.78, -1.65, 180],]
    
    
    exp = 1 # experiment counts
    while exp < 21:
        # initial position
        count = 0
        control_threading(target_pos[count], pid_fb[count], pid_sd[count])
        print('Initial point: ', target_pos[count])
        time.sleep(1)
        
        count = 1
        control_threading(target_pos[count], pid_fb[count], pid_sd[count])
        print('Mid point: ', target_pos[count])
        
        # ready position
        count = 2
        
        control_threading(target_pos[count], pid_fb[count], pid_sd[count])
        print('Ready point: ', target_pos[count])
        DS.ON('BOAT_1_DOCK_1')
        DS.ON('BOAT_1_DOCK_1')
        time.sleep(1)
        DS.ON('BOAT_1_DOCK_2')
        DS.ON('BOAT_1_DOCK_2')
        time.sleep(1)
        
        # dock position
        count = 3
        control_threading(target_pos[count], pid_fb[count], pid_sd[count])
        print('Dock point: ', target_pos[count])
        time.sleep(5)
        DS.OFF('BOAT_1_DOCK_1')
        DS.OFF('BOAT_1_DOCK_1')
        time.sleep(1)
        DS.OFF('BOAT_1_DOCK_2')
        DS.OFF('BOAT_1_DOCK_2')
        time.sleep(3)
        exp += 1


if __name__=='__main__':
    #
    dataThread = threading.Thread(target = data_threading)
    dataThread.setDaemon(True)
    dataThread.start()
    #
    navThread = threading.Thread(target = navigation_threading)
    navThread.setDaemon(True)
    navThread.start()
    
    
    