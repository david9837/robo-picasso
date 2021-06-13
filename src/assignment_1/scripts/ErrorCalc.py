import imutils
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def ErrorCalc(Ideal_Image,Current_Image):
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Replace these with the cam topic and the ideal image plot 
  resized_orig = cv2.imread(Ideal_Image)
  resized_mod = cv2.imread(Current_Image)




#Change colour and then apply GaussianBlur to accomidate for slight inaccuracys 
  first_gray = cv2.cvtColor(resized_orig, cv2.COLOR_BGR2GRAY)
  first_gray = cv2.GaussianBlur(first_gray, (7, 7), 0)
  gray_frame = cv2.cvtColor(resized_mod,cv2.COLOR_BGR2GRAY)
  blurFrame = cv2.GaussianBlur(gray_frame, (7, 7), 0)

 
#Computing the difference between two frames is a simple subtraction
 
  diff = cv2.absdiff(blurFrame,first_gray)
 

# threshold the difference image, followed by finding contours to
# obtain the regions of the two input images that differ
  thresh = cv2.threshold(diff,25, 255, cv2.THRESH_BINARY| cv2.THRESH_OTSU)[1]
  

#Go through the thresh image to find the countors( coords for changed areas)
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  cnts = imutils.grab_contours(cnts)

# loop over the contours
  a_file = open("Failed_points.txt", "w")
  for c in cnts:
# compute the bounding box of the contour and then draw the
# bounding box on both input images to represent where the two
# images differ
    
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(resized_orig, (x, y), (x + w, y + h), (0, 0, 255), 1)
    cv2.rectangle(resized_mod, (x, y), (x + w, y + h), (0, 0, 255), 1)

    print("centre = ", (x+(x+w))/2,(y+(y+h))/2)
    centerX =float((x+(x+w))/2)
    centerY = float((y+(y+h))/2)
  #  print("arrays that have be checked are", x,y,"through",x + w, y + h)

    X_position =float(((centerX-3.0)*(25.0-0.0))/((683.0-3)-3.0))
    X_position=format(X_position, '.1f')
    Y_position =float(((centerY-4)*(25.0-0.0))/((331.0-3)-3)) 
    
    Y_position= 25-Y_position
    Y_position =round(Y_position*2)/2
    Y_position=format(Y_position, '.1f')

    print(X_position)
    print(Y_position)
    a_file.write(str(X_position))
    a_file.write(',')
    a_file.write(str(Y_position))
    a_file.write('\n')


  a_file.close()


  return(x,y)