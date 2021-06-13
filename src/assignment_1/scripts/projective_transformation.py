import numpy as np

def compute_transform_matrix(point1,point2,point3,point4):

    '''
    Takes input four points of the form [x,y]
    Outputs a 3x3 transformation matrix for projective transformation
    '''

    # Step 1
    # e * f = g
    # f = inv(e) * g
    e = np.matrix([[point1[0],point2[0],point3[0]],[point1[1],point2[1],point3[1]],[1,1,1]])
    g = np.matrix([[point4[0]],[point4[1]],[1]])
    
    inv_e = np.linalg.inv(e)
    f = np.matmul(inv_e,g)
    
    # Step 2
    # Scale the columns by the coefficients computed
    lamb = np.asscalar(f[0])
    mu = np.asscalar(f[1])
    tao = np.asscalar(f[2])
    result = np.matrix([[lamb*point1[0],mu*point2[0],tao*point3[0]],[lamb*point1[1],mu*point2[1],tao*point3[1]],[lamb,mu,tao]])

    return result

def image_world_coordinates(image_points, Cam_Offset = 10):

    '''
    Takes input the image pixel coordinates of the form [x,y] and outputs
    the world cooridnates of the form [x,y]. This code implements a projective
    transformation using the four projected points of the green table.
    '''

    image1 = [101.4-Cam_Offset,98] # Top Left w.r.t to Camera Image FoR
    image2 = [101.4-Cam_Offset,370] # Bottom Left
    image3 = [534-Cam_Offset,370] # Bottom Right
    image4 = [534-Cam_Offset,98] # Top Right
    A = compute_transform_matrix(image1,image2,image3,image4)

    world1 = [1125.5,375] 
    world2 = [1125.5,-375]
    world3 = [0,-375]
    world4 = [0,375]

    B = compute_transform_matrix(world1,world2,world3,world4)

    # Step 4 and 5
    inv_A = np.linalg.inv(A)
    C = np.matmul(B,inv_A)

    # Step 6
    image_coord = np.matrix([[image_points[0]],[image_points[1]],[1]])
    res = np.matmul(C,image_coord) # Original result is [x, y, 1]

    # Note, robot axis is different orientation
    # Therefore, swap x and y    
    return [np.asscalar(res[1]), np.asscalar(res[0])]






