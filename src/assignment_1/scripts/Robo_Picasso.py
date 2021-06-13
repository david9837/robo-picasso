#! /usr/bin/env python

# This program is the main ROS node
# to run the Robo Picasso Systm
# 

# last revision 3.6.21

# import all required librariers and ROS message tyoes
import rospy
import geometry_msgs.msg

import math

from move_group_interface import MoveGroupPythonInteface
from std_msgs.msg import Float32MultiArray

from gazebo_msgs.msg import ModelStates

import numpy as np
import matplotlib
matplotlib.use('TKAgg')
from matplotlib import pyplot as plt

import tf

import random

import message_filters

from apply_pointilism import find_pointilism_coords

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import cv2

from Canvas_corner import canvas_coord_angle

from projective_transformation import image_world_coordinates
from projective_transformation import compute_transform_matrix

import imutils

import matplotlib.image as mpimg

from ErrorCalc import ErrorCalc

# Instantiate CvBridge
bridge = CvBridge()

# Create Globals

# stores the name of the models and links
names = []

# set a constant for the model array size
MODEL_ARRAY_SIZE = 5

# stores the X and Y posiion of each model
X_Pos = [None] * MODEL_ARRAY_SIZE
Y_pos = [None] * MODEL_ARRAY_SIZE



# store the home position value in radians
home_pos = [1.433268904884939, -1.9368049930777511, 1.3095792766008287, -0.944100938382439, -1.5714370887387554, -1.0372421978685198]

canvas_home_pos = [1.3600772265809002, -1.0391962676159618, 1.706823891541248, -2.2663017105564283, -1.5488515125996853, 2.931808912786085]


# global target_pose
target_pose = geometry_msgs.msg.Pose()

# The number of dots to print between checks
CHECK_FREQUNECY = 15

# The number of dots to print before skipping a dot
SKIP_FREQUNECY = 30

# These constants are the simualted error values
# in cm
X_ERROR_MAX = 0
Y_ERROR_MAX = 0

# The offset correcton values between the tip of the marker and the origin of the
# marker model
X_OFFSET = -0.07
Y_OFFSET = 0.03
Z_OFFSET = -0.035

# This constant is the length of half the canvas
Canvas_Half_Length = 14.25

# these global values are used to store the
# centre of the canvas in the world frame
# default values are given
global Canvas_Centre_X_World_Frame
Canvas_Centre_X_World_Frame = 0

global Canvas_Centre_Y_World_Frame
Canvas_Centre_Y_World_Frame = 0.65


# This callback subscribes to the image topic
# of the virtual camera and creates a cv2 image
def image_callback(msg):

    try:
        # Convert ROS Image message to OpenCV2
        global cv2_img
        cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError, e:
        print(e)

    return



# this is the callback for the model states subscriber
# calls a function to update the stored model state
# information and passes the input message to it
def callback_models(input_msg_models):

    update(input_msg_models)

    return


# this function updates the stored model states info
# with the latest values
# updates the model name array
# also updates the x and y position of each model
# one by one
# is also used to get the actual yaw rotation
# of the canvas
def update(inbound):

    names = inbound.name

    #print(names)

    for i in range(0,len(names)):

        global X_Pos
        X_Pos[i] = inbound.pose[i].position.x
        
        global Y_Pos
        Y_pos[i] = inbound.pose[i].position.y


    # get actual rotation of canvas
    quaternion = (
    inbound.pose[4].orientation.x,
    inbound.pose[4].orientation.y,
    inbound.pose[4].orientation.z,
    inbound.pose[4].orientation.w)
    
    # convert quaterion into euler values
    euler = tf.transformations.euler_from_quaternion(quaternion)
    
    
    # save the actual yaw as according to gazebo
    # save the value to be wrap to 1.57 radians
    global yaw_gazebo
    yaw_gazebo = euler[2]

    global yaw_gazebo_scaled
    yaw_gazebo_scaled = (yaw_gazebo)%(math.pi/2)

    if yaw_gazebo_scaled > 1.56:
        yaw_gazebo_scaled = yaw_gazebo_scaled - math.pi/2



    return


# when called this function moves the arm to the set home position
def Move_Home():

    mgpi.move_to_joint_state(home_pos)

    return


# This function when called reads in the postion
# of the dots on a canvas from a text file
# also counts the number of lines
# data in the text file is of the form 'x,y'
def Load_coords():

    global file_lines
    file_lines = 0

    global raw_coords
    raw_coords = []
    
    coord_file = open('coords.txt','r')
    
    for line in coord_file.readlines():
        
        raw_coords.append( [ float (x) for x in line.split(',') ] )
        
        file_lines += 1

    coord_file.close()


    return

# This function when called moves the arm to 
# a specified x and y position
def Move_Arm_Horizontal(i,x,y):

    Check_Joint_Okay()

    target_pose.position.x = x + X_OFFSET
    target_pose.position.y = y + Y_OFFSET

    mgpi.move_eef_to_pose(target_pose)

    return

# This function when called moves the arm down to plot
def Move_Arm_Down_to_Plot():

    Check_Joint_Okay()

    target_pose.position.z = 0.01 + Z_OFFSET
    mgpi.move_eef_to_pose(target_pose)

    return

# This function when called moves the arm up
# after plotting
def Move_Arm_Up():

    Check_Joint_Okay()

    target_pose.position.z = 0.02 + Z_OFFSET
    mgpi.move_eef_to_pose(target_pose)

    return

# This function when called moves the arm
# to the home position just above the canvas
def Move_to_Canvas_Home():

    mgpi.move_to_joint_state(canvas_home_pos)

    return


# This function when called moves the arm out of the camera FOV
# Takes a picture and then passes it to the corner funding
# module that returns the x and y position of the origin of the canvas
# and the rotation of the canvas
def Check_Painting():
    
    print('checking')



    Move_Home()

    # save image from virtual camera
    cv2.imwrite('camera_image.jpeg', cv2_img)

    print("New Image Taken")

    imageName= "camera_image.jpeg"
    
    # Reading the raw RGB image
    raw_image = cv2.cvtColor(cv2.imread(imageName), cv2.COLOR_BGR2RGB)
    result = canvas_coord_angle(raw_image)


    print("Centre Coordaintes (Camera Pixel FoR): ({},{}), Angle (rad): {}".format(result[0][0],result[0][1],result[1]))

    # get new centre and angle
    image_pixels_centre = [result[0][0],result[0][1]]
    world_coords_centre = image_world_coordinates(image_pixels_centre)

    # update angle
    global yaw
    yaw = result[1]
    print('yaw')
    print(yaw)

    # update centre position and scale to metres from mm
    global Canvas_Centre_X_World_Frame
    Canvas_Centre_X_World_Frame = world_coords_centre[0] / 1000

    global Canvas_Centre_Y_World_Frame
    Canvas_Centre_Y_World_Frame = world_coords_centre[1] / 1000

    print('canvas centre in world frame')
    print(Canvas_Centre_X_World_Frame)
    print(Canvas_Centre_Y_World_Frame)

    
    # These lines save the actual vs predicted pose of th canvas to a file
    file_object = open('sample.txt', 'a')


    file_object.write(str(yaw_gazebo))

    file_object.write(" ")

    file_object.write(str(yaw))

    file_object.write(" ")

    file_object.write(str(X_Pos[4]))

    file_object.write(" ")

    file_object.write(str(Canvas_Centre_X_World_Frame))

    file_object.write(" ")

    file_object.write(str(Y_pos[4]))

    file_object.write(" ")

    file_object.write(str(Canvas_Centre_Y_World_Frame))

    file_object.write("\n")

    file_object.close()


    return

# This function when called converts the world frame to the canvas frame
def Convert_World_to_Canvas(i,world_input_x,world_input_y):


    # reverse the direction of rotation to make gazebo and our code consistent
    theta = (2*math.pi)-yaw_gazebo

    # perform transformation for x value
    canvas_output_x =  ((100*world_input_x)-(100*Canvas_Centre_X_World_Frame)+(math.sin(theta)*(raw_coords[i][1]-Canvas_Half_Length))/math.cos(theta)) +(Canvas_Half_Length)
    
    # round to nearest 0.5cm
    canvas_output_x = Round_to_0_5(canvas_output_x)

    # repeat above but for y
    canvas_output_y = -1*(((100*world_input_y)-(100*Canvas_Centre_Y_World_Frame)+(math.sin(theta)*raw_coords[i][0])-(Canvas_Half_Length*math.sin(theta))-(Canvas_Half_Length*math.cos(theta)))/(math.cos(theta)))
    canvas_output_y = Round_to_0_5(canvas_output_y)


    return canvas_output_x,canvas_output_y

# This function when called converts the dots from canvas frame to world frame
def Convert_Canvas_to_World(i):

    theta = (2*math.pi)-yaw



    world_output_x = (Canvas_Centre_X_World_Frame) + ((raw_coords[i][0]-Canvas_Half_Length)*math.cos(theta)-(raw_coords[i][1]-Canvas_Half_Length)*math.sin(theta))/100

    world_output_y = (Canvas_Centre_Y_World_Frame) + -1*((raw_coords[i][0]-Canvas_Half_Length)*math.sin(theta)+(raw_coords[i][1]-Canvas_Half_Length)*math.cos(theta))/100


    return world_output_x,world_output_y

# This function when called converts the error dots from canvas frame to world frame
def Convert_Errors_to_World(i):

    theta = (2*math.pi)-yaw


    world_output_x = (Canvas_Centre_X_World_Frame) + ((error_coords[i][0]-Canvas_Half_Length)*math.cos(theta)-(error_coords[i][1]-Canvas_Half_Length)*math.sin(theta))/100

    world_output_y = (Canvas_Centre_Y_World_Frame) + -1*((error_coords[i][0]-Canvas_Half_Length)*math.sin(theta)+(error_coords[i][1]-Canvas_Half_Length)*math.cos(theta))/100


    return world_output_x,world_output_y

# This function when called aims to check if a collision between the arm
# and the table is liekly. It does this by checking if joint 0 and 2
# have different polariites and if so, sends a warning and tries
# to get the arm to return to th home position
def Check_Joint_Okay():
  
    # Get joint states
    joints = mgpi.get_current_joint_state()



    if joints[0] > 0 and joints[2] < 0:

        print("Joint collision likely. Moving to Safety!!!")
        Move_to_Canvas_Home()


    if joints[2] > 0 and joints[0] < 0:

        print("Joint collision likely. Moving to Safety!!!")
        Move_to_Canvas_Home()



    return

# This function is called on startup
# to intialise evrything and first find the canvas pose
def Startup():

    img = cv2.imread('Image_1.jpeg',0)
    find_pointilism_coords(img, pixel_width = 50)

    Move_Home()

    print("Starting")

    # take virtual image of canvas
    cv2.imwrite('start.jpeg', cv2_img)

    print("First Image Taken")

    imageName= "start.jpeg"
    # Reading the raw RGB image
    
    #read virtual camera image and pass to module to get position and anlge
    raw_image = cv2.cvtColor(cv2.imread(imageName), cv2.COLOR_BGR2RGB)
    result = canvas_coord_angle(raw_image)

    print("Centre Coordaintes (Camera Pixel FoR): ({},{}), Angle (rad): {}".format(result[0][0],result[0][1],result[1]))

    # sort results
    image_pixels_centre = [result[0][0],result[0][1]]
    world_coords_centre = image_world_coordinates(image_pixels_centre)
    

    # update angle
    global yaw
    yaw = result[1]
    print('yaw')
    print(yaw)

    # udate and scale canvas centre XY position
    # gazebo uses metres
    global Canvas_Centre_X_World_Frame
    Canvas_Centre_X_World_Frame = world_coords_centre[0] / 1000
    
    global Canvas_Centre_Y_World_Frame
    Canvas_Centre_Y_World_Frame = world_coords_centre[1] / 1000

    print('canvas centre in world frame')
    print(Canvas_Centre_X_World_Frame)
    print(Canvas_Centre_Y_World_Frame)


    return


# This function controls the main plotting process
def Plot_Process():

    # These constants define limits for the plots
    canvas_minimum_lim = 0
    canvas_maximum_lim = 25

    # first setup the initial end-effector rotation
    Setup_end_quat()

    # move to above the canvas
    Move_to_Canvas_Home()

    # get the desired plot values
    Get_Initial_Plot_Values()

    # set up plots to act as canvas
    # all these lines below set up the four plots
    # 1. the desired plot in world frame
    # 2. the desired plot in canvas frame
    # 3. the actual plot in canvas frame
    # 4. the actual plot in world frame
    plt.ion()
    global fig
    global ax
    fig, ax = plt.subplots(2,2)


    plot_world_x, plot_world_y = [],[]
    
    global plot_can_x,plot_can_y
    plot_can_x,plot_can_y = [],[]

    sc = ax[0,0].scatter(initial_World_X, initial_World_Y)
    ax[0,0].set_xlabel("World X")
    ax[0,0].set_ylabel("World Y")
    
    sb = ax[1,0].scatter(initial_Canvas_X, initial_Canvas_Y)
    ax[1,0].set_xlabel("Canvas X")
    ax[1,0].set_ylabel("Canvas Y")
    ax[1,0].set_xlim(canvas_minimum_lim,canvas_maximum_lim)
    ax[1,0].set_ylim(canvas_minimum_lim,canvas_maximum_lim)
    
    global se
    se = ax[0,1].scatter(plot_can_x,plot_can_y)
    ax[0,1].set_xlabel("Actual Canvas X")
    ax[0,1].set_ylabel("Actual Canvas Y")
    ax[0,1].set_xlim(canvas_minimum_lim,canvas_maximum_lim)
    ax[0,1].set_ylim(canvas_minimum_lim,canvas_maximum_lim)

    
    sd = ax[1,1].scatter(plot_world_x,plot_world_y)
    ax[1,1].set_xlabel("Actual World X")
    ax[1,1].set_ylabel("Actual World Y")
    ax[1,1].set_xlim(-0.5,0.5)
    ax[1,1].set_ylim(0.5,1)


    
    # for each of the points
    for i in range(0,file_lines):

        print('i')
        print(i)

        # convert from canvas to world frame
        dots_pos = Convert_Canvas_to_World(i)

        # check if we need to reclaibrate canvas
        if (i%CHECK_FREQUNECY==0) and (i != 0):

            print("check")
            Check_Painting()

            Move_to_Canvas_Home()

        # check if this dot is t be skipped
        if (i%SKIP_FREQUNECY==0) and (i != 0):

            print("Dot Missed")

        # otherwise plot it
        else:
    
            # these three function calls control the plotting movements
            Move_Arm_Horizontal(i,dots_pos[0],dots_pos[1])

            Move_Arm_Down_to_Plot()

            Move_Arm_Up()

            # convert the actual world plotting point of the arm back to the actual canvas frame
            actual_canvas_resilts= Convert_World_to_Canvas(i,dots_pos[0],dots_pos[1])

            # update plots
            plot_can_x.append(actual_canvas_resilts[0])
            plot_can_y.append(actual_canvas_resilts[1])
            se.set_offsets(np.c_[plot_can_x,plot_can_y])

            print('desired')
            print(raw_coords[i][0])
            print(raw_coords[i][1])

            print("actual")
            print(actual_canvas_resilts[0])
            print(actual_canvas_resilts[1])


            plot_world_x.append(dots_pos[0])
            plot_world_y.append(dots_pos[1])
            # sc.set_offsets(np.c_[x,y])
            sd.set_offsets(np.c_[plot_world_x,plot_world_y])
            fig.canvas.draw_idle()
            plt.pause(0.001)

    # save the desired and the actual canvas as images to for the missing dot detection module 
    extent_1 = ax[1,0].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig('reference_out.png', bbox_inches=extent_1)

    extent_2 = ax[0,1].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig('error_out.png', bbox_inches=extent_2)

    


    # call the function to fix errors
    Fix_Errors()

    plt.waitforbuttonpress()



    return

# When called this function sets up the inital rotation
# and z values
def Setup_end_quat():

    target_pose.orientation.x = 0
    target_pose.orientation.y = 0.707
    target_pose.orientation.z = 0
    target_pose.orientation.w = 0.707

    target_pose.position.z = 0.02 + Z_OFFSET

    return

# This function when called, takes an image of the actual canvas
# as oppose to the desired canvas and calls an external function to check for errors
# the lcoation of missing dots is saved to a text file, is then read in
# and then this function goes through each missing dot and plots it
def Fix_Errors():

    Ideal="reference_out.png"
    Current="error_out.png"

    ErrorCalc(Ideal,Current)

    Load_error_coords()

    for i in range(0,error_lines):

        print('error i')
        print(i)

        error_pos = Convert_Errors_to_World(i)

    
        Move_Arm_Horizontal(i,error_pos[0],error_pos[1])

        Move_Arm_Down_to_Plot()

        Move_Arm_Up()

        plot_can_x.append(error_coords[i][0])
        plot_can_y.append(error_coords[i][1])
        se.set_offsets(np.c_[plot_can_x,plot_can_y])

        fig.canvas.draw_idle()
        plt.pause(0.001)




    return
# This function when called sets up arrays to hold points
# in the world and canvas frme, and also reads what the plot should
# look like into the arrays for the purpose of plotting
def Get_Initial_Plot_Values():

    global initial_Canvas_X
    initial_Canvas_X = []

    global initial_Canvas_Y
    initial_Canvas_Y = []

    global initial_World_X
    initial_World_X = []

    global initial_World_Y
    initial_World_Y = []

    for i in range(0,file_lines):

        initial_Canvas_X.append(raw_coords[i][0])
        initial_Canvas_Y.append(raw_coords[i][1])



        temp_world = Convert_Canvas_to_World(i)

        initial_World_X.append(temp_world[0])
        initial_World_Y.append(temp_world[1])



    return

# This function when called loads the error values
# from a text file
def Load_error_coords():

    global error_lines
    error_lines = 0

    global error_coords
    error_coords = []
    
    error_file = open('Failed_points.txt','r')
    
    for line in error_file.readlines():
        
        error_coords.append( [ float (x) for x in line.split(',') ] )
        
        error_lines += 1

    error_file.close()


    return

# This function rounds a number to 0.5
def Round_to_0_5(number):

    return round(number * 2) / 2


# main function of the program
# controls the flow of the program
def main():
    try:


        # Create and Initialize the interface
        # also make it global so other functions can see it
        global mgpi
        mgpi = MoveGroupPythonInteface()    


        # wait for user input
        raw_input("Press Enter to Start Painting")

        # set up a subscriber for the model states from gazebo
        rospy.Subscriber("/gazebo/model_states", ModelStates, callback_models)

        image_topic = "/camera/color/image_raw"

        rospy.Subscriber(image_topic, Image, image_callback)


        # wait for two seconds to give plent of time for the subscriber to 
        # get the model states on the topic
        rospy.sleep(2)

        # call startup function
        Startup()

        # load in canvas coordinates
        Load_coords()
        

        # intiate main plot process
        Plot_Process()

        print('done')


        
        rospy.spin()

    except rospy.ROSInterruptException:
        return
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()