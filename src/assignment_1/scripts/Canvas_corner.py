import cv2
import numpy as np
import matplotlib
matplotlib.use('TKAgg')
from matplotlib import pyplot as plt
import math

def centeroidpython(data):
    x, y = zip(*data)
    l = len(x)
    return sum(x) / l, sum(y) / l

def canvas_coord_angle(raw_image):

    '''
    Takes input the raw image as a cv2 RGB object and outputs an array:
    [[x_centre, y_centre],angle]. Coordinates are in camera pixels FoR and
    angle is radians w.r.t to robot FoR anticlockwise direction.
    '''

    # Convert to grayscale ready for threshold to extract white 
    gray = cv2.cvtColor(raw_image,cv2.COLOR_RGB2GRAY)

    # Apply a bilateral filter which blurs pixels with similar pixel
    # intensity to that of the central pixel, meaing preserves corners/edges
    # of high gradient change.
    gray = cv2.bilateralFilter(gray, 5, 75, 75)

    # Apply the threshold to extract white pixels only
    ret,gray = cv2.threshold(gray,175,255,0)

    # Detect the corners
    corners = cv2.goodFeaturesToTrack(gray, 4, 0.01, 30)
    corners = np.int0(corners)
    
    # plt.figure()

    # plt.imshow(gray,cmap='gray')
    
    # Unravel corners into tuple list
    canvas_corners = []
    for corner in corners:
        x,y = corner.ravel()
        canvas_corners.append([x,y])

        # plt.scatter(x,y,color='red',s=0.4)   
    
    x_centre, y_centre = centeroidpython(canvas_corners)

    # Sort the corners by increasing X values relative to the robot arm world frame
    # This, means the top corner will have the lowest 'X' value, which is represented
    # in the camera field of view is the y value.
    sorted_by_x = sorted(canvas_corners, key=lambda tup: tup[1])

    # Calculate angle between the top two coordaintes in the camera reference.
    # First have to determine which is the furthest along the x axis.
    if sorted_by_x[1][0] >= sorted_by_x[0][0]:
        left_x = sorted_by_x[0][0]
        left_y = sorted_by_x[0][1]
        right_x = sorted_by_x[1][0]
        right_y = sorted_by_x[1][1]
    else:
        left_x = sorted_by_x[1][0]
        left_y = sorted_by_x[1][1]
        right_x = sorted_by_x[0][0]
        right_y = sorted_by_x[0][1]
    angle = math.atan2(right_y-left_y, right_x-left_x)
    
    # To convert into robot frame, absolute value the angle.
    # This means that the angle is anticlockwise from the positive y axis.
    angle = abs(angle)

    # plt.scatter(x_centre,y_centre,color='blue',s=0.4)
    # plt.title(math.degrees(angle))
    # plt.show()

    return [[x_centre, y_centre], angle,sorted_by_x]

if __name__ == "__main__":

    # Reading the raw RGB image
    imageName = "image_1.jpg"
    raw_image = cv2.cvtColor(cv2.imread(imageName),  cv2.COLOR_BGR2RGB)
    result = canvas_coord_angle(raw_image)
    print("Centre Coordaintes (Camera Pixel FoR): ({},{}), Angle (rad): {}".format(result[0][0],result[0][1],result[1]))


    

    