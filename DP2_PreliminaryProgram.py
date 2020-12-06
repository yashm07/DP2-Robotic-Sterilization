import time
import sys
import random
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)

##Objective: Move six containers of different sizes and colors to their respective autoclave bin for sterilization.
##Raising Left arm corresponds to open_control_gripper(), raising right arm corresponds to move_end_effector(), raising both arms correspond to open_drawer()

##Functions
def autoclave_bin_location(container_id): ##Identify autoclave bin location based on container ID
    if container_id == 1:
        autoclave_location = [-0.5898, 0.2353, 0.3994] ##Dropoff location for small red container
    elif container_id == 2:
        autoclave_location = [0, -0.635, 0.3994] ##Dropoff location for small green container
    elif container_id == 3:
        autoclave_location = [0, 0.635, 0.3994] ##Dropoff location for small blue container
    elif container_id == 4:
        autoclave_location = [-0.3836, 0.1529, 0.3422] ##Dropoff location for large red container
    elif container_id == 5:
        autoclave_location = [0.0, -0.3993, 0.3095] ##Dropoff location for large green container
    elif container_id == 6:
        autoclave_location = [0.0, 0.3993, 0.3095] ##Dropoff location for large blue container
    else: ##If the container ID are not any of the above, return to home location
        autoclave_location = [0.4064, 0.0, 0.4826] ##Home location
        print("Invalid ID. Returning to home position.")
       
    return autoclave_location

def open_control_gripper(action): #Open or close control gripper
    if(arm.emg_left() >= threshold and arm.emg_right() == 0): ##If left arm passes threshold and right arm remains outstretched, open or close control gripper based on boolean input
        if(action == True): ##This closes gripper
            arm.control_gripper(40)
        elif(action == False): ##This opens gripper
            arm.control_gripper(-40)

def move_end_effector(coordinates): #Move end effector to coordinates specified in the input if right arm exceeds threshold and left arm remains outstreched 
    if (arm.emg_left() == 0 and arm.emg_right() >= threshold):
        arm.move_arm(coordinates[0],coordinates[1],coordinates[2])

def open_drawer(action): #Open or close autoclave bin if both arms exceed threshold and current position equates to one of three dropoff locations for large containers
    if (arm.emg_left() >= threshold and arm.emg_right() >= threshold):
        if (list(arm.effector_position()) == autoclave_bin_location(4)): ##List function converts tuples to lists to compare current location to location of the autoclave bins
            arm.open_red_autoclave(action) ##Open or close red drawer
        elif (list(arm.effector_position()) == autoclave_bin_location(5)):
            arm.open_green_autoclave(action) ##Open or close green drawer
        elif (list(arm.effector_position()) == autoclave_bin_location(6)):
            arm.open_blue_autoclave(action) ##Open or close blue drawer

##Main Function
total_cage_num = 6 #set variable for total number of cages
pickup_platform = [0.5055, 0.0, 0.0227] #Coordinates for pickup platform
home = [0.4064, 0.0, 0.4826] #Coordinates for home location
threshold = 0.3 #Threshold that needs to be passed in order for tasks to be performed
container_stored = [] #List for container IDs that have been stored


for i in range(0, total_cage_num): #for loop that runs from 0 to total number of cages, terminates at total_cage_num - 1

    while True: #while loop that will continue until a new cage_num appears
        cage_num = random.randint(1,6) #get a random integer between one to six
        if cage_num not in container_stored: #if current cage ID is not in the list of container IDs that have been stored, then break the loop, else continue the loop
            break


    autoclave_location = (autoclave_bin_location(cage_num)) #set variable for autoclave location based on current cage ID
    arm.spawn_cage(cage_num) #Spawns a container
    
    time.sleep(2)
    move_end_effector(pickup_platform) #Effector moves to pickup platform
    time.sleep(2)
    open_control_gripper(True) #Control gripper closes
    time.sleep(2)
    move_end_effector(home) #Effector to home location
    time.sleep(2)
    move_end_effector(autoclave_location) #Effector moves to autoclave location
    time.sleep(2)
    open_drawer(True) #Check if drawer needs to be opened, if so, open appropiate drawer
    print("open_drawer Function passed")
    time.sleep(2)
    open_control_gripper(False) #Control gripper opens
    time.sleep(2)
    open_drawer(False) #Check if drawer needs to be closed, if so, close appropiate drawer
    print("open_drawer Function passed")
    container_stored.append(cage_num) #Append the current cage ID to the container_stored list
    time.sleep(2)
    move_end_effector(home) #Move effector to home location
