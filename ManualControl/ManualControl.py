# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 23:35:59 2020

@author: CUHKSZ

ip: 192.168.3.3
port: 80
"""

import pygame
import sys
import time
import copy
from OASES import OASES
from UDPserver import DockingSystem

# create the boat
USV = OASES()
print("Init boat.")

# create the docking system
DS = DockingSystem('BOAT_1', 1)
time.sleep(5)

# initial pygame
pygame.display.set_caption("PyGame")
pygame.display.set_mode((640, 480))
pygame.init()
print("Init Pygame.")

# catch keyboard event
Flag = True
long_press = {'W': False, 'S': False, 'A': False, 'D': False, 
              'I': False, 'J': False, 'K': False, 'L': False} # For movement and action
long_press_last = copy.copy(long_press) # remember the last time
count = 0
reset_waittime = 10

while Flag:
    
    for event in pygame.event.get():
        # if event.type == QUIT:
            # sys.exit()
        #print("event get")

        # press key
        if event.type == pygame.KEYDOWN:
            # quit
            # print("key down, key: ", event.key == pygame.K_w)
            if event.key == pygame.K_q:
                print("Quit manual control.")
                Flag = False
                USV.stop()
                pygame.quit()
                sys.exit()
                break
            
            if event.key == pygame.K_u:
                print("Update servo motor position.")
                USV.update_servo_position()
            
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
                USV.reset()
                print("Reset boat.")
            if event.key == pygame.K_y:
                DS.ON('BOAT_1_DOCK_1')
                DS.ON('BOAT_1_DOCK_1')
            if event.key == pygame.K_n:
                DS.OFF('BOAT_1_DOCK_1')
                DS.OFF('BOAT_1_DOCK_1')
        # release key
        elif event.type == pygame.KEYUP:
            # print("key up, key: ", event.key == pygame.K_w)
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
    if long_press['W'] == True and long_press_last['W'] == False: 
        USV.forward()
        print("Forward.")
    if long_press["S"] == True and long_press_last['S'] == False:
        USV.backward()
        print("Backward.")
    if long_press["A"] == True and long_press_last['A'] == False:
        USV.leftward()
        print("Leftward.")
    if long_press["D"] == True and long_press_last['D'] == False:
        USV.rightward()
        print("Rightward.")
        
    if long_press['J'] == True and long_press_last['J'] == False:
        USV.turnleft()
        print("Turn left.")
    if long_press["L"] == True and long_press_last['L'] == False:
        USV.turnright()
        print("Turn right.")

    if long_press["I"] == True and long_press_last['I'] == False:
        USV.extend()
        print("Extend.")
    if long_press["K"] == True and long_press_last['K'] == False:
        USV.contract()
        print("Contract.")
    
    # no key pressed, wait for several rounds     
    if all(value == 0 for value in long_press.values()):
        if long_press != long_press_last:
            count += 1
            #print(long_press)
            #print(long_press_last)
            if count > reset_waittime:
                USV.stop()
                print("Reset boat.")
                count = 0
                long_press_last = copy.copy(long_press)
                
    else:
        long_press_last = copy.copy(long_press)
    
    #pygame.time.delay(0) # delay 10ms       

