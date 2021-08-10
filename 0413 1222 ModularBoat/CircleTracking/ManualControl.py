# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 23:35:59 2020

@author: CUHKSZ

ip: 192.168.3.3
port: 80
"""

import pygame
import sys
from HOMES import HOMES

# create the boat
HOMES_boat = HOMES()
print("Init HOMES boat.")

# initial pygame
pygame.display.set_caption("PyGame")
pygame.display.set_mode((640, 480))
pygame.init()
print("Init Pygame.")

# catch keyboard event
Flag = True
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
                HOMES_boat.stop()
                pygame.quit()
                sys.exit()
                break
            
            if event.key == pygame.K_u:
                print("Update servo motor position.")
                HOMES_boat.update_servo_position()
            
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
                HOMES_boat.reset()
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
        HOMES_boat.forward()
        print("Forward.")
    if long_press["S"] == True:
        HOMES_boat.backward()
        print("Backward.")
    if long_press["A"] == True:
        HOMES_boat.leftward()
        print("Leftward.")
    if long_press["D"] == True:
        HOMES_boat.rightward()
        print("Rightward.")
        
    if long_press['J'] == True:
        HOMES_boat.turnleft()
        print("Turn left.")
    if long_press["L"] == True:
        HOMES_boat.turnright()
        print("Turn right.")

    if long_press["I"] == True:
        HOMES_boat.extend()
        print("Extend.")
    if long_press["K"] == True:
        HOMES_boat.contract()
        print("Contract.")
    
    # no key pressed     
    if all(value == 0 for value in long_press.values()):
        HOMES_boat.stop()
        print("Reset boat.")
    
    pygame.time.delay(10) # delay 10ms       

