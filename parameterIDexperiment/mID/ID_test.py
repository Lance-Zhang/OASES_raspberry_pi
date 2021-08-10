# -*- coding: utf-8 -*-
"""

@author: CUHKSZ

ip: 192.168.3.10
port: 80
"""

##### start test #####
import sys
import math
import time
import pygame
from OASES import OASES

# round 1
# forward
PWM2 = 60
PWM4 = 60

# rightward
PWM1 = 90
PWM3 = 90

# round 2
# forward
PWM2_ = 120
PWM4_ = 120

# rightward
PWM1_ = 90
PWM3_ = 90


# create the boat
Boat = OASES()
print("Init HOMES boat.")

# initial pygame
pygame.display.set_caption("PyGame")
pygame.display.set_mode((640, 480))
pygame.init()
print("Init Pygame.")

# catch keyboard event
Flag = True

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
                Boat.reset()
                pygame.quit()
                sys.exit()
                break
            
            if event.key == pygame.K_w:
                Boat.propeller(PWM1, PWM2, PWM3, PWM4)
                
                time.sleep(2) # delay 10ms
                
                Boat.propeller(PWM1_, PWM2_, PWM3_, PWM4_)
                
                time.sleep(2) # delay 10ms
                
            if event.key == pygame.K_r:
                Boat.stop()
                print("Reset boat.")
                
    
    # next loop
    pygame.time.delay(10) # delay 10ms 


