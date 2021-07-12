import numpy as np
import serial
import time
import cv2
from math import *

# All params are in m. Calculation are done for our setup, may vary.

# Distance of screen from camera = D
D=1.46

# Height of the camera = H
H= 0.70

# Height of the nozzle = h
h=0.21

# Distance of the nozzle from screen
d=0.79

# m/pixel ratio= D/640 for a distance D of the screen from camera
fact= D/640         

#velocity = 4m/s
u=4

#gravity
g = 9.81

arduino = serial.Serial(port='COM7', baudrate=9600, timeout=0.1) #port number may vary

def find_centre2(white_loc):
    n = len(white_loc)
    if n<120:
        print("No Flame Detected")
        cv2.imshow('display', img)
        return 0
    arr = np.array(white_loc)
    x,y = np.sum(arr,axis=0)/n
    return (round(y),round(x))


def operate(img):
    img_in = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img_out = np.zeros(img_in.shape)
    img_out[img_in>230]=255
    return img_out

def find_white_loc(img_in):
    white_loc=[]
    m,n = img_in.shape
    for i in range(m):
        for j in range(n):
            if img_in[i,j]==255:
                white_loc.append([i,j])
    return white_loc

def plane_theta(centre):
        ## coordinates with respect to camera
        x = centre[0]*fact
        y = centre[1]*fact

        ## coordinates with respect to nozzle. Obtained by shifting of origin
        X = sqrt(d**2+(x)**2)
        Y = y + H - h
        print("X:",X, "Y: ", Y)

        Q1 = ( atan( ( (u**2) + sqrt( u**4 - 2*Y*g*u**2 - (g**2)*(X**2) ) ) / (g*X) ) ) * 180/3.1415
        Q2 = ( atan( ( (u**2) - sqrt( u**4 - 2*Y*g*u**2 - (g**2)*(X**2) ) ) / (g*X) ) ) * 180/3.1415

        if (abs(Q1)<abs(Q2)):
            angle = Q1
        else:
            angle = Q2
        print("Vertical Angle is : ",angle) 
        return angle
	
	
def z_rotation(centre):

	## coordinates with respect to camera
        x = centre[0]*fact
        y = centre[1]*fact
        

        ## coordinates with respect to nozzle. Obtained by shifting of origin
        X = x
        Y = y + H - h

        angle=(atan(X/d))*180/3.1415
        
        print("Horizontal Angle is :", angle)
        return angle
        
	
	

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame,1)
    if not ret:
        print("Can't receive frame . Exiting ...")
        break
    img = np.copy(frame)
    img_mat = operate(frame)
    white_loc = find_white_loc(img_mat)
    centre = find_centre2(white_loc)
    

    if centre!=0:
	    adj_centre=(centre[0]-320,-centre[1]+240)
	    if centre!= None:
	        print(adj_centre)
	        img = cv2.circle(img,centre,40,(255,0,0),3)
	        img = cv2.circle(img,centre,0,(255,0,0),5)
	        img = cv2.circle(img,(320,240),0,(255,0,0),5)

	    cv2.imshow('display', img)
	    arduino_out="X"+str(z_rotation(adj_centre))+"Y"+str(plane_theta(adj_centre))+"Z"+str(1)

    else:
        arduino_out="X"+str(360)+"Y"+str(360)+"Z"+str(0)
    
    arduino.write(bytes(arduino_out, 'utf-8'))
    arduino.flush()
    time.sleep(0.5)
    print(arduino_out)       
    if cv2.waitKey(1) == ord('q'):
        break
   	
cap.release()
cv2.destroyAllWindows()




