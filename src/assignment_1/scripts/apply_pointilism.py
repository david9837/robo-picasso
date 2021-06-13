import cv2 
import numpy as np
import matplotlib.pyplot as plt

def find_pointilism_coords(img, pixel_width = 50):

    '''
    Function which takes an input raw RGB image
    and outputs a text file containing pointilism coordinates.
    It first performs face cropping and uses edge detection to find the points.
    Note: must require the file 'haarcascade_frontalface_alt2.xml' in the same
    working directory as the script.
    '''

    # Step 1: Face detection and cropping
    # Assumption - only one face in the image
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
    faces = face_cascade.detectMultiScale(img, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        faces = img[y:y + h, x:x + w]

    
    # Step 2: Resize the image to the num_pixels.
    # Default resolution is 0.5 cm for 25 x 25 cm canvas
    faces = cv2.resize(faces, (pixel_width,pixel_width), interpolation = cv2.INTER_CUBIC)

    # Step 3: Edge detection using Canny filter
    faces = cv2.normalize(faces,None,0,255,cv2.NORM_MINMAX)
    edges = cv2.Canny(faces,140,150)

    # Step 4: Create a boundary of empty values 2 pixels wide
    edges[0] = np.zeros((len(edges[0]),), dtype=int)
    edges[1] = np.zeros((len(edges[0]),), dtype=int)
    edges[-2] = np.zeros((len(edges[0]),), dtype=int)
    edges[-1] = np.zeros((len(edges[0]),), dtype=int)

    for line in edges:
        line[0] = 0
        line[1] = 0
        line[-2] = 0
        line[-1] = 0

    # To view the output
    '''
    plt.subplot(121),plt.imshow(faces,cmap='gray')
    plt.title('Original Image'),plt.xticks([]),plt.yticks([])
    plt.subplot(122),plt.imshow(edges,cmap='gray')
    plt.title('Edge Image'),plt.xticks([]),plt.yticks([])
    plt.show()
    '''

    # Step 5: Extract coordinates
    x_coord = np.where(edges==255)[1]
    y_coord = np.where(edges==255)[0]
    
    # Coordinates must exist for the robot arm to begin painting
    if len(x_coord) == 0:
        raise Exception("No pointilism coordinates detected to draw!")
    else:
        
        # Note: need to convert from image x-y frame
        # to the regular cartesian frame with the origin
        # being at the bottom left hand corner of the canvas.
        file1 = open("coords.txt","w")
        for i in range(0,len(x_coord)):
            y_value = (50 - y_coord[i])*0.5
            x_value = (x_coord[i])*0.5

            file1.write(str(x_value)+","+str(y_value)+"\n")


if __name__ == "__main__":

    # face_image = cv2.imread('image_1.jpeg',0)
 #img = cv2.imread('image_1.jpeg',0)

    find_pointilism_coords(face_image)

