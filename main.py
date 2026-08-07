import serial # type: ignore
import time
import numpy as np

ser = serial.Serial(port="COM3",baudrate=115200,timeout=1)
time.sleep(2)
ser.reset_input_buffer() #As the python script is starting up, the Arduino sends random/old data in the buffer so this removes it. 
distanceArray = np.array([0.0,0.0,0.0,0.0,0.0]) #Every 60ms, we will add a distance onto this array. 
currentIndex = 0

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

while True:
    if (ser.in_waiting != 0): #Checks if stuff is in serial buffer
        rawBytes = ser.readline() #Retrieves items in the buffer
        serialString = rawBytes.decode("utf-8",errors="ignore")
        serialString.strip()
        serialStringArray = serialString.split(",")
        distance = serialStringArray[0]
        angle = serialStringArray[1]

        #print(f"The distance is {distance}cm and the angle is {angle} degrees")
        distanceArray[currentIndex] = distance
        currentIndex = (currentIndex + 1) % 5 #Adds each measured distance onto the array in circular fashion. 
        filteredDistance = hampelFilter(3.0)
        #print(f"{filteredDistance:.2f}")