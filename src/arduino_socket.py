from pyduino import *
import time
import sys

def lights_on(arduino,pin, delay):
    arduino.digital_write(pin,1)
    print("Lights turned on!")
    time.sleep(delay)
    return True

def lights_off(arduino,pin, delay):
    arduino.digital_write(pin,0)
    print("Lights turned off!")
    time.sleep(delay)
    return False

if __name__ == '__main__':
    
    a = Arduino(serial_port='/COM4')
    # if your arduino was running on a serial port other than '/dev/ttyACM0/'
    # declare: a = Arduino(serial_port='/dev/ttyXXXX')

    time.sleep(3)
    # sleep to ensure ample time for computer to make serial connection 

    PIN = 13
    a.set_pin_mode(PIN,'O')
    # initialize the digital pin as output

    time.sleep(1)
    # allow time to make connection

    a.digital_write(PIN,0) # initialise off 
    print(sys.executable)
    while True:
        user_input = input("Do you want to turn the lights on? [y/n]\n")


        if (user_input == "y"):  
            lights_on(a,PIN,0) # turn LED on 

            user_input = input("Press any key to turn the lights off")
            lights_off(a,PIN,0) # turn LED on
