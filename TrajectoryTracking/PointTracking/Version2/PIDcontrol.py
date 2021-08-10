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

PORT = 8000
      # 创建一个套接字socket对象，用于进行通讯
      # socket.AF_INET 指明使用INET地址集，进行网间通讯
      # socket.SOCK_DGRAM 指明使用数据协议，即使用传输层的udp协议
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ("192.168.3.10", PORT)  
server_socket.bind(address)  # 为服务器绑定一个固定的地址，ip和端口
server_socket.settimeout(10)  #设置一个时间提示，如果10秒钟没接到数据进行提示

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
def PID_norm(pid_output):
    if pid_output >= 0:
        norm_output = math.ceil(pid_output)
    if pid_output < 0:
        norm_output = math.floor(pid_output)
    return norm_output

# control thread
def control_threading():
    # create the boat
    USV = HOMES()
    print("Init HOMES USV.")
    
    PID_orient_smlangle = PID(20,0,0.5) # adjust the orientation
    PID_orient_midangle = PID(6,0,0.5) 
    PID_orient_bigangle = PID(7,0,0.5)
    
    PID_forback = PID(5,0,0) # adjust the forward / backward position
    PID_side = PID(5.3,0,0) # adjust the sideward position
    print("Init PID.")
    
    sml_angle = 10 * math.pi/180
    big_angle = 90 * math.pi/180
    
    # target point
    target_pos = [0,0,0] # x, y, attitude : -180~180
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
    while True:
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
        
        azimuth = math.atan2(y - y_t, x - x_t) # position angle -180~180
        inter_angle = angle_norm(math.pi + yaw - azimuth)
        
        #print('inter angle:  ', inter_angle)
        
        PID_forback.update(distance * math.cos(inter_angle)) # >0 forward
        
        # sideward feedback
        PID_side.update(distance * math.sin(inter_angle)) # >0 rightward
        
        #print('Boat yaw: ', yaw, '   target angle: ', h_angle)    
        
        # execute
        if angle_error > -sml_angle and angle_error < sml_angle:
            control_orient = PID_norm(PID_orient_smlangle.output)
        elif angle_error < -big_angle or angle_error > big_angle:
            control_orient = PID_norm(PID_orient_bigangle.output)
        else:
            control_orient = PID_norm(PID_orient_midangle.output)
        print('rotate: ', control_orient)
        
        
        control_fb = PID_norm(PID_forback.output)
        #print('forward/backward: ', control_fb)
        control_side = PID_norm(PID_side.output)
        #print('sideward: ', control_side)
        
        pwm_front = 90 - control_side - control_orient
        pwm_back = 90 - control_side + control_orient
        pwm_left = 90 + control_fb #+ control_orient
        pwm_right = 90 + control_fb #- control_orient
        
        fp.write("State: " + str(State) + "\nControl: "
             + str([pwm_front, pwm_back, pwm_left, pwm_right]) + '\n\n')
        
        print("command:  ", pwm_front, pwm_back, pwm_left, pwm_right)
        
        USV.propeller(pwm_right, pwm_back, pwm_front, pwm_left)

if __name__=='__main__':
    #
    dataThread = threading.Thread(target = data_threading)
    dataThread.setDaemon(True)
    dataThread.start()
    #
    controlThread = threading.Thread(target = control_threading)
    controlThread.setDaemon(True)
    controlThread.start()
    
    
    