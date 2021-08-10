# -*- coding: utf-8 -*-
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)

head = 255 # 254, 253
tail = 250
PWM1 = 100
PWM2 = 100
PWM3 = 100
PWM4 = 100
print(hex(PWM1))

p1_b = bytes([head, PWM1, PWM2, PWM3, PWM4, tail]).hex()
p2 = bytes([PWM4]).hex()
print(p1_b)

p1_c = bytes.fromhex(p1_b)
p2 = bytes.fromhex(p2)
print(p1_c)
# print(str(hex(data))[2:4])
# 
# data = bytes.fromhex(str(hex(data))[2:4].zfill(2))
# print(data)

while True:
    time.sleep(0.005)
    ser.write(p1_c)
    #ser.write(p2)