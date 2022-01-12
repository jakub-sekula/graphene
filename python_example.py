#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##########################################################################
#
# 
#  File name: MdigProcess.py  
#
#   Synopsis:  This program shows the use of the MdigProcess() function and its multiple
#              buffering acquisition to do robust real-time processing.           
#  
#              The user's processing code to execute is located in a callback function 
#              that will be called for each frame acquired (see ProcessingFunction()).
#    
#        Note: The average processing time must be shorter than the grab time or some
#              frames will be missed. Also, if the processing results are not displayed
#              and the frame count is not drawn or printed, the CPU usage is reduced 
#              significantly.
#
#  Copyright (C) Matrox Electronic Systems Ltd., 1992-2020.
#  All Rights Reserved

# Supporting the print function prototype from 3.0
from __future__ import print_function

import sys
import os
import ctypes
import mil as MIL

# Get correct .dcf config file for the camera
DCF_FILENAME = "[WORKING CONFIG] MV2-D1280-640-CL-8_1280x1024_8Taps8bitCon.dcf"
DCF_PATH = os.path.join(os.getcwd(),DCF_FILENAME)
print(f"The config file in use is located at {DCF_PATH}")

# Text input function differs from 2.7 to 3.0. 
if sys.hexversion >= 0x03000000:
    get_input = input
else:
    get_input = raw_input

# User's processing function hook data structure.
class HookDataStruct(ctypes.Structure):
   _fields_ = [
      ("MilDigitizer", MIL.MIL_ID),
      ("MilImageDisp", MIL.MIL_ID),
      ("ProcessedImageCount", MIL.MIL_INT)]

# Number of images in the buffering grab queue.
# Generally, increasing this number gives a better real-time grab.
BUFFERING_SIZE_MAX = 20

# User's processing function called every time a grab buffer is ready.
# --------------------------------------------------------------------

# Local defines. 
STRING_POS_X       = 20 
STRING_POS_Y       = 20 

def ProcessingFunction(HookType, HookId, HookDataPtr):
   
   # Retrieve the MIL_ID of the grabbed buffer. 
   ModifiedBufferId = MIL.MIL_ID(0)
   MIL.MdigGetHookInfo(HookId, MIL.M_MODIFIED_BUFFER + MIL.M_BUFFER_ID, ctypes.byref(ModifiedBufferId))
   
   # Extract the userdata structure
   UserData = ctypes.cast(ctypes.c_void_p(HookDataPtr), ctypes.POINTER(HookDataStruct)).contents
   
   # Increment the frame counter.
   UserData.ProcessedImageCount += 1
   
   # Print and draw the frame count (remove to reduce CPU usage).
   print("Processing frame #{:d}.\r".format(UserData.ProcessedImageCount), end='')
   MIL.MgraText(MIL.M_DEFAULT, ModifiedBufferId, STRING_POS_X, STRING_POS_Y, MIL.MIL_TEXT("{:d}".format(UserData.ProcessedImageCount)))
   
   # Execute the processing and update the display.
   MIL.MimArith(ctypes.c_double(ModifiedBufferId.value), 0.0, UserData.MilImageDisp, MIL.M_NOT)
   
   return 0
   
# Main function.
# ---------------

def MdigProcessExample():
   # Allocate defaults.
   MilApplication = MIL.MappAlloc(MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)
   MilSystem = MIL.MsysAlloc(MIL.M_DEFAULT, MIL.M_SYSTEM_DEFAULT, MIL.M_DEFAULT, MIL.M_DEFAULT, None)
   MilDisplay = MIL.MdispAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)
   MilDigitizer = MIL.MdigAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT(DCF_PATH), MIL.M_DEFAULT, None)

   SizeX = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_X, None)
   SizeY = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_Y, None)

   MilImageDisp = MIL.MbufAlloc2d(MilSystem,SizeX,SizeY, 8 + MIL.M_UNSIGNED, MIL.M_IMAGE + MIL.M_PROC + MIL.M_DISP + MIL.M_GRAB, None)

   MIL.MbufClear(MilImageDisp, MIL.M_COLOR_BLACK)
   MIL.MdispSelect(MilDisplay, MilImageDisp)
     
   # Print a message.
   print("\nMULTIPLE BUFFERED PROCESSING.")
   print("-----------------------------\n")

   # Grab continuously on the display and wait for a key press
   MIL.MdigGrabContinuous(MilDigitizer, MilImageDisp)
   
   
   # with open("kappa.jpg", 'wb') as f:
   #    f.write(image)
   # MIL.MdigGrabContinuous(MilDigitizer, MilImageDisp)
   
   # get_input("Press <Enter> to start capture.\n")
   
   # MIL.MbufExportSequence(MIL.MIL_TEXT("video.avi"), MIL.M_DEFAULT, 0, MIL.M_DEFAULT,MIL.M_DEFAULT,MIL.M_OPEN)
   # MIL.MbufExportSequence(MIL.MIL_TEXT("video.avi"), MIL.M_DEFAULT, MilImageDisp, MIL.M_DEFAULT,MIL.M_DEFAULT,MIL.M_WRITE)
   # MIL.MbufExportSequence(MIL.MIL_TEXT("video.avi"), MIL.M_DEFAULT, MilImageDisp, MIL.M_DEFAULT,MIL.M_DEFAULT,MIL.M_CLOSE)

   # Halt continuous grab. 
   get_input("Press <Enter> to stop capture.\n")

   MIL.MdigHalt(MilDigitizer)#
   MIL.MbufExport("random.png", MIL.M_PNG, MilImageDisp)
   # Allocate the grab buffers and clear them.
   MilGrabBufferList = (MIL.MIL_ID * BUFFERING_SIZE_MAX)()
   MilGrabBufferListSize = 0
      
   # Free the grab buffers.
   for id in range(0, MilGrabBufferListSize):
      MIL.MbufFree(MilGrabBufferList[id])
      
   # Release defaults.
   MIL.MbufFree(MilImageDisp)
   MIL.MdispFree(MilDisplay)
   MIL.MdigFree(MilDigitizer)
   MIL.MsysFree(MilSystem)
   MIL.MappFree(MilApplication)
   
   return
   
if __name__ == "__main__":
   MdigProcessExample()