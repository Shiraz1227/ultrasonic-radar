import serial # type: ignore
import time

ser = serial.Serial(port="COM3",baudrate=115200,timeout=1)
time.sleep(2)
