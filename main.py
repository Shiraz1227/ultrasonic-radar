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
maxObjects = 180

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
fig = plt.figure(figsize=(16, 9))
fig.canvas.manager.set_window_title("Ultrasonic Radar Scope")
gs = fig.add_gridspec(1, 2, wspace=0.45, left=0.08, right=0.94, top=0.88, bottom=0.15) #Manually lays out. 
#Polar axes on the left hand side
polarAxes = fig.add_subplot(gs[0,0], projection="polar") #111 means how many rows, columns and position within made grid. 
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

#Serial plotter axes comparing filtered distance and actual distance
serialAxes = fig.add_subplot(gs[0,1])
serialAxes.set_title("Raw distance vs Hampel Filtered Distance")
serialAxes.set_xlabel("Last 100 readings",color="white",labelpad=8)
serialAxes.set_ylabel("Distance (cm)",color="white",labelpad=8)
plotSamples = 100
serialAxes.set_xlim(0,plotSamples)
serialAxes.set_ylim(0,maxRange)
serialAxes.grid(True,color="#004400",linestyle="--",linewidth=0.7)
serialAxes.set_facecolor("#0B0F19")
serialAxes.tick_params(colors="white")

rawDistanceLine, = serialAxes.plot([],[],color="red",alpha=0.7,lw=1.5,label="Raw distance data")
filteredDistanceLine, = serialAxes.plot([],[],color="green",lw=1.5,label="Filtered distance data")
rawDistanceHistory = deque(maxlen=plotSamples)
filteredDistanceHistory = deque(maxlen=plotSamples)
fps = 30.0
frameInterval = 1 / 30.0
previousTime = 0

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
        filteredDistance = hampelFilter(1.0)
        print(f"{filteredDistance:.2f}")
        #Adds data to respective arrays
        angleRadians = np.radians(int(angle))
        angles_rad.append(angleRadians)
        distances_cm.append(filteredDistance)
        rawDistanceHistory.append(float(distance))
        filteredDistanceHistory.append(filteredDistance)
        #Draws the both axes when time interval has passed (30fps) so it doesn't keep refreshing
        currentTime = time.time()
        if (currentTime - previousTime) >= frameInterval:
            #Polar axes artists
            sweepLine.set_data([angleRadians,angleRadians],[0,np.pi])
            target_dots.set_data(list(angles_rad),list(distances_cm))
            #Serial axes artists
            x_coords = list(range(len(rawDistanceHistory)))
            rawDistanceLine.set_data(x_coords,list(rawDistanceHistory))
            filteredDistanceLine.set_data(x_coords,list(filteredDistanceHistory))
            #Refreshes the figure/canvas
            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            previousTime = currentTime