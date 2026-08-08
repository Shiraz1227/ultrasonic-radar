import serial # type: ignore
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

ser = serial.Serial(port="COM3",baudrate=115200,timeout=1)
time.sleep(2)
ser.reset_input_buffer() #As the python script is starting up, the Arduino sends random/old data in the buffer so this removes it. 
distanceArray = np.array([0.0,0.0,0.0,0.0,0.0]) #Every 60ms, we will add a distance onto this array. 
currentIndex = 0
maxRange = 30  #max range for cm. 
maxObjects = 60

def hampelFilter(outlierFactor):
    median = np.median(distanceArray)
    MAD_array = [0.0,0.0,0.0,0.0,0.0]
    for i in range(5):
        difference = median - distanceArray[i]
        MAD_array[i] = difference
    np.abs(MAD_array)
    mad = np.median(MAD_array)
    sd = 1.4826 * mad
    mask = np.abs(median - distanceArray) <= (outlierFactor * sd) #Creates an array like [True, True, False, False, True]
    validData = distanceArray[mask]
    return np.mean(validData)

#Matplotlib runs in 3 sections, Figure (the window), Axes (the graph area in the window) and Artists (the actual paint/lines on the graph). 
plt.ion() #Allows script to run. 
fig = plt.figure(figsize=(8, 8))
fig.canvas.manager.set_window_title("Ultrasonic Radar Scope")
polarAxes = fig.add_subplot(111, projection="polar") #111 means how many rows, columns and position within made grid. 
polarAxes.set_theta_zero_location("E")
polarAxes.set_theta_direction(1) #orientation of the graph. -1 turns it upside down
polarAxes.set_ylim(0,maxRange)
polarAxes.set_xlim(0,np.pi)
sweepLine, = polarAxes.plot([],[],color="#00FF00",lw=2) #Trailing comma is able to return the actual line from a list. 
target_dots, = polarAxes.plot([],[],"o",color="#FF0000",ms=5) #For both, instead of clearing and then redrawing, set_data modifies the geometry once thus much quicker. 

polarAxes.set_facecolor("#0B0F19")
fig.patch.set_facecolor("#0B0F19")
polarAxes.tick_params(colors="#00FF00")
polarAxes.grid(color="#005500",linestyle="--",linewidth=0.7)

angles_rad = deque(maxlen=maxObjects) #as the radar sweeps, once it hits 180 degrees it then forgets/erases the blips. 
distances_cm = deque(maxlen=maxObjects)   

while True:
    if (ser.in_waiting != 0): #Checks if stuff is in serial buffer
        #Retrieves distance and angle from the arduino
        rawBytes = ser.readline() 
        serialString = rawBytes.decode("utf-8",errors="ignore")
        serialString.strip()
        serialStringArray = serialString.split(",")
        distance = serialStringArray[0]
        angle = serialStringArray[1]
        #Applies hampelFilter with window size of 5
        print(f"The distance is {distance}cm and the angle is {angle} degrees")
        distanceArray[currentIndex] = distance
        currentIndex = (currentIndex + 1) % 5 #Adds each measured distance onto the array in circular fashion. 
        filteredDistance = hampelFilter(3.0)
        print(f"{filteredDistance:.2f}")
        #Draws artists for matplotlib
        angleRadians = np.radians(int(angle))
        angles_rad.append(angleRadians)
        distances_cm.append(filteredDistance)
        sweepLine.set_data([angleRadians,angleRadians],[0,180])
        target_dots.set_data(list(angles_rad),list(distances_cm))
        fig.canvas.draw_idle()
        fig.canvas.flush_events()