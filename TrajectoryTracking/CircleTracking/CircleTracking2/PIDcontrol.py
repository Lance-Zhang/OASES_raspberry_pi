# -*- coding: utf-8 -*-
"""

@author: CUHKSZ

ip: 192.168.3.10
port: 80
"""

# Receive robot state

import re
import threading
import socket  #导入socket模块
import time #导入time模块
      #server 接收端
      # 设置服务器默认端口号
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
        #正常情况下接收数据并且显示，如果10秒钟没有接收数据进行提示（打印 "time out"）
        #当然可以不要这个提示，那样的话把"try:" 以及 "except"后的语句删掉就可以了
      try:  
          now = time.time()  #获取当前时间
                          # 接收客户端传来的数据 recvfrom接收客户端的数据，默认是阻塞的，直到有客户端传来数据
                          # recvfrom 参数的意义，表示最大能接收多少数据，单位是字节
                          # recvfrom返回值说明
                          # receive_data表示接受到的传来的数据,是bytes类型
                          # client  表示传来数据的客户端的身份信息，客户端的ip和端口，元组
          receive_data, client = server_socket.recvfrom(1024)
          receive_data = receive_data.decode()
          #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(now))) #以指定格式显示时间
          #print("来自客户端%s,发送的%s\n" % (client, receive_data))  #打印接收的内容
          State = [float(s) for s in re.findall(r'[-+]?\d+\.?\d*', receive_data)]
          
      except socket.timeout:  #如果10秒钟没有接收数据进行提示（打印 "time out"）
          print('time out')
      
dataThread = threading.Thread(target = data_threading)
dataThread.setDaemon(True)
dataThread.start()


# PID
import sys
import math
from HOMES import HOMES
from PID import PID


def angle_norm(old_angle): # to -180~180
    if old_angle > math.pi:
        return old_angle - 2 * math.pi
    elif old_angle <= -math.pi:
        return old_angle + 2 * math.pi
    else:
        return old_angle

# create the boat
USV = HOMES()
print("Init HOMES USV.")
PID_orient = PID(5.3,0,0.2) # p, i, d
PID_drift = PID(12000,0,0) # decrease the drift velocity 
print("Init PID.")

# circle
radius = 1.3
velocity = 80 # < 90 forward, > 90 backward

# PID
PID_orient.setGoal(0) # setpoint
PID_drift.setGoal(0)

last_x = State[0]
last_y = State[1]
last_time = time.time()

while True:
    # measurement
    #time.sleep(0.05)
    #print('State: ', State[0], State[1], State[2]*180/math.pi)
    x = State[0]
    y = State[1]
    now = time.time()
    yaw = State[2] # yaw
    
    v_value = math.sqrt(math.pow(x-last_x,2) + math.pow(y-last_y,2))/(now-last_time)
    v_angle = math.atan2(y-last_y,x-last_x) # -180 ~ 180
    last_x = x
    last_y = y
    
    # heading feedback
    cur_distance = math.sqrt(math.pow(x,2) + math.pow(y,2))
    cur_azimuth = math.atan2(y,x) # position angle -180~180
    
    if cur_distance >= radius: # -180~180
        h_angle = angle_norm(math.pi + cur_azimuth - math.asin(radius/cur_distance)) # target heading angle
    else:
        h_angle = angle_norm(cur_azimuth + math.pi/2)
    #print('Boat yaw: ', yaw, '   target angle: ', h_angle)    
    PID_orient.update(angle_norm(yaw - h_angle)) # if yaw > h_angle, turn right
    
    # drift feedback
    inter_angle = v_angle - yaw # <0 left shift, >0 right shift
    if inter_angle <= -math.pi:
        inter_angle += 2*math.pi
    if inter_angle > math.pi:
        inter_angle -= 2*math.pi
    
    PID_drift.update(v_value * math.sin(inter_angle)) # if error > 0, move rightward
    #print('shift velocity: ', v_value , v_value * math.sin(inter_angle) )
    #print('PID output: ', PID_orient.output)
    # execute
    if PID_orient.output >= 0:
        control_orient = math.ceil(PID_orient.output)
    if PID_orient.output < 0:
        control_orient = math.floor(PID_orient.output)
    pwm_front = 90 - int(PID_drift.output) #- control_orient 
    pwm_back = 90 + control_orient - int(PID_drift.output) 
    
    pwm_right = velocity
    pwm_left = velocity
    
    #print("command:  ", pwm_front, pwm_back, pwm_left, pwm_right)
    
    USV.propeller(pwm_right, pwm_back, pwm_front, pwm_left)

