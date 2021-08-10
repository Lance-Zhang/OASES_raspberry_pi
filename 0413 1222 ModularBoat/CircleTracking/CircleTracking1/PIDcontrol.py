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
          State = [float(s) for s in re.findall(r'\d+\.?\d*', receive_data)]
          
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

# create the boat
USV = HOMES()
print("Init HOMES USV.")
PID_mv = PID(4,0,0) # p, i, d
PID_dft = PID(7,0,0) # decrease the drift velocity 
print("Init PID.")

# circle
radius = 1
velocity = 60 # < 90 forward, > 90 backward
max_range = 1.5 * radius
min_range = 0.5 * radius

# PID
PID_mv.setGoal(radius) # setpoint
PID_dft.setGoal(0)

last_x = State[0]
last_y = State[1]
last_time = time.time()

while True:
    # measurement
    print(State)
    x = State[0]
    y = State[1]
    now = time.time()
    w = State[2] # yaw
    v_value = math.sqrt(math.pow(x-last_x,2) + math.pow(y-last_y,2))/(now-last_time)
    v_angle = math.atan2(y-last_y,x-last_x) # -180 ~ 180
    last_x = x
    last_y = y
    
    # movement feedback
    #central_angle = math.atan2(y,x)*180/math.pi
    cur_distance = math.sqrt(math.pow(x,2) + math.pow(y,2))
    if cur_distance > max_range:
        cur_distance = max_range
#     if cur_distance < min_range:
#         cur_distance = min_range
    
    PID_mv.update(cur_distance)
    
    # drift feedback
    inter_angle = v_angle - w
    if inter_angle <= -math.pi:
        inter_angle += 2*math.pi
    if inter_angle > math.pi:
        inter_angle -= 2*math.pi
    
    PID_dft.update(v_value * math.sin(inter_angle))
    
    # execute
    
    if cur_distance > radius:
        pwm_right = velocity + int(PID_mv.output)
        pwm_left = velocity 
    if cur_distance < radius:
        pwm_right = velocity + int(2.5*PID_mv.output)
        pwm_left = velocity 
    
    pwm_drift = 90 + int(PID_dft.output)
    
    print("command:  ", pwm_left, pwm_right, pwm_drift)
    
    USV.propeller(pwm_right, pwm_drift, pwm_drift, pwm_left)

