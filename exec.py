#!/usr/bin/env python


import sys
import copy
import time
import rospy


import numpy as np
from lab5_header import *
from lab5_func import *
from blob_search import *




# ========================= Student's code starts here =========================


# Position for UR3 not blocking the camera
go_away = [270*PI/180.0, -90*PI/180.0, 90*PI/180.0, -90*PI/180.0, -90*PI/180.0, 135*PI/180.0]


# Store world coordinates of green and yellow blocks
xw_yw_G = []
xw_yw_B = []


# Any other global variable you want to define
# Hints: where to put the blocks?




# ========================= Student's code ends here ===========================


################ Pre-defined parameters and functions no need to change below ################


# 20Hz
SPIN_RATE = 20


# UR3 home location
home = [0*PI/180.0, 0*PI/180.0, 0*PI/180.0, 0*PI/180.0, 0*PI/180.0, 0*PI/180.0]


# UR3 current position, using home position for initialization
current_position = copy.deepcopy(home)


thetas = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


digital_in_0 = 0
analog_in_0 = 0.0


suction_on = True
suction_off = False


current_io_0 = False
current_position_set = False


image_shape_define = False












"""
Whenever ur3/position publishes info, this callback function is called.
"""
def position_callback(msg):


   global thetas
   global current_position
   global current_position_set


   thetas[0] = msg.position[0]
   thetas[1] = msg.position[1]
   thetas[2] = msg.position[2]
   thetas[3] = msg.position[3]
   thetas[4] = msg.position[4]
   thetas[5] = msg.position[5]


   current_position[0] = thetas[0]
   current_position[1] = thetas[1]
   current_position[2] = thetas[2]
   current_position[3] = thetas[3]
   current_position[4] = thetas[4]
   current_position[5] = thetas[5]


   current_position_set = True








"""
Move robot arm from one position to another
"""
def move_arm(pub_cmd, loop_rate, dest, vel, accel):


   global thetas
   global SPIN_RATE


   error = 0
   spin_count = 0
   at_goal = 0


   driver_msg = command()
   driver_msg.destination = dest
   driver_msg.v = vel
   driver_msg.a = accel
   driver_msg.io_0 = current_io_0
   pub_cmd.publish(driver_msg)


   loop_rate.sleep()


   while(at_goal == 0):


       if( abs(thetas[0]-driver_msg.destination[0]) < 0.0005 and \
           abs(thetas[1]-driver_msg.destination[1]) < 0.0005 and \
           abs(thetas[2]-driver_msg.destination[2]) < 0.0005 and \
           abs(thetas[3]-driver_msg.destination[3]) < 0.0005 and \
           abs(thetas[4]-driver_msg.destination[4]) < 0.0005 and \
           abs(thetas[5]-driver_msg.destination[5]) < 0.0005 ):


           at_goal = 1
           #rospy.loginfo("Goal is reached!")


       loop_rate.sleep()


       if(spin_count >  SPIN_RATE*5):


           pub_cmd.publish(driver_msg)
           rospy.loginfo("Just published again driver_msg")
           spin_count = 0


       spin_count = spin_count + 1


   return error


################ Pre-defined parameters and functions no need to change above ################




class ImageConverter:


   def __init__(self, SPIN_RATE):


       self.bridge = CvBridge()
       self.image_pub = rospy.Publisher("/image_converter/output_video", Image, queue_size=10)
       self.image_sub = rospy.Subscriber("/cv_camera_node/image_raw", Image, self.image_callback)
       self.loop_rate = rospy.Rate(SPIN_RATE)


       # Check if ROS is ready for operation
       while(rospy.is_shutdown()):
           print("ROS is shutdown!")




   def image_callback(self, data):


       global xw_yw_G # store found green blocks in this list
       global xw_yw_B # store found yellow blocks in this list
       global maze1


       try:
         # Convert ROS image to OpenCV image
           raw_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
       except CvBridgeError as e:
           print(e)
           pass


       cv_image = cv2.flip(raw_image, -1)
       cv2.line(cv_image, (0,50), (640,50), (0,0,0), 5)


       # You will need to call blob_search() function to find centers of green blocks
       # and yellow blocks, and store the centers in xw_yw_G & xw_yw_B respectively.


       # If no blocks are found for a particular color, you can return an empty list,
       # to xw_yw_G or xw_yw_B.


       # Remember, xw_yw_G & xw_yw_B are in global coordinates, which means you will
       # do coordinate transformation in the blob_search() function, namely, from
       # the image frame to the global world frame.


       # xw_yw_G = blob_search(cv_image, "green")
       # xw_yw_B = blob_search(cv_image, "blue")
       maze1 = blob_search(cv_image, "green")






# def move_block(pub_cmd, loop_rate, start_loc, start_height, \
#                end_loc, end_height):




  
#     error = 0
#     return error




def BFS(maze, maze_path, start, end):
 queue = [start]
 directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
 while queue:
     current_cell = queue.pop(0)
     if current_cell == end:
         return True
     for direction in directions:
         next_cell = (current_cell[0] + direction[0], current_cell[1] + direction[1])
         if 0 <= next_cell[0] < len(maze) and 0 <= next_cell[1] < len(maze[0]):
           if maze[next_cell[0]][next_cell[1]] == 1:
             queue.append(next_cell)
             maze[next_cell[0]][next_cell[1]] = 2
             maze_path[next_cell[0]][next_cell[1]] = current_cell
 return False


def find_path(maze_path, start, end):
 path = []
 path.append(end)
 cell = end
 while (cell != start):
   cell = maze_path[cell[0]][cell[1]]
   path.append(cell)
 return path


"""
Program run from here
"""
def main():


   global go_away
   global maze1


   # Initialize ROS node
   rospy.init_node('lab5node')


   # Initialize publisher for ur3/command with buffer size of 10
   pub_command = rospy.Publisher('ur3/command', command, queue_size=10)


   # Initialize subscriber to ur3/position & ur3/gripper_input and callback fuction
   # each time data is published
   sub_position = rospy.Subscriber('ur3/position', position, position_callback)


   # Check if ROS is ready for operation
   while(rospy.is_shutdown()):
       print("ROS is shutdown!")


   # Initialize the rate to publish to ur3/command
   loop_rate = rospy.Rate(SPIN_RATE)


   vel = 4.0
   accel = 4.0
   move_arm(pub_command, loop_rate, go_away, vel, accel)


   ic = ImageConverter(SPIN_RATE)
   time.sleep(5)


   # ========================= Student's code starts here =========================


   """
   Hints: use the found xw_yw_G, xw_yw_B to move the blocks correspondingly. You will
   need to call move_block(pub_command, loop_rate, start_xw_yw_zw, target_xw_yw_zw, vel, accel)
   """
  
   maze_positions = [
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],],
   [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],]]
   for i in range(0, 15):
       for j in range(0, 15):
           maze_positions[i][j][0] = 165/1000 + 14/1000 * i
           maze_positions[i][j][1] = -15/100 + 26/1000 * j


   maze_path = [
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),],
   [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),]]
   start = (0, 7)
   end = (14, 7)


   while(not BFS(maze1, maze_path, start, end)):
       print("Path not Found")
       pass
   path = find_path(maze_path, start, end)


   for i in range(0, len(path)):
       x = path[len(path) - i - 1][0]
       y = path[len(path) - i - 1][1]
       angles = lab_invk(maze_positions[x][y][0], maze_positions[x][y][1], 4/100, 0)
       move_arm(pub_command, loop_rate, angles, vel, accel)
   time.sleep(5)


   # ========================= Student's code ends here ===========================


   move_arm(pub_command, loop_rate, go_away, vel, accel)
   rospy.loginfo("Task Completed!")
   print("Use Ctrl+C to exit program")
   rospy.spin()


if __name__ == '__main__':


   try:
       main()
   # When Ctrl+C is executed, it catches the exception
   except rospy.ROSInterruptException:
       pass





