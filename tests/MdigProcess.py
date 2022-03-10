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
import ctypes
import mil as MIL

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
   MilDigitizer = MIL.MdigAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)

   SizeX = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_X, None)
   SizeY = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_Y, None)

   MilImageDisp = MIL.MbufAlloc2d(MilSystem,
                                     SizeX,
                                     SizeY, 
                                     8 + MIL.M_UNSIGNED, 
                                     MIL.M_IMAGE + 
                                     MIL.M_PROC + MIL.M_DISP + MIL.M_GRAB, 
                                     None)

   MIL.MbufClear(MilImageDisp, MIL.M_COLOR_BLACK)
   MIL.MdispSelect(MilDisplay, MilImageDisp)
     
   # Print a message.
   print("\nMULTIPLE BUFFERED PROCESSING.")
   print("-----------------------------\n")

   # Grab continuously on the display and wait for a key press
   MIL.MdigGrabContinuous(MilDigitizer, MilImageDisp)
   get_input("Press <Enter> to start processing.\n")

   # Halt continuous grab. 
   MIL.MdigHalt(MilDigitizer)

   # Allocate the grab buffers and clear them.
   MilGrabBufferList = (MIL.MIL_ID * BUFFERING_SIZE_MAX)()
   MilGrabBufferListSize = 0
   MIL.MappControl(MIL.M_DEFAULT, MIL.M_ERROR, MIL.M_PRINT_DISABLE)
   for n in range(0, BUFFERING_SIZE_MAX):
      MilGrabBufferList[n] = (MIL.MbufAlloc2d(MilSystem, SizeX, SizeY, 8 + MIL.M_UNSIGNED, MIL.M_IMAGE + MIL.M_GRAB + MIL.M_PROC, None))
      if (MilGrabBufferList[n] != MIL.M_NULL):
         MIL.MbufClear(MilGrabBufferList[n], 0xFF)
         MilGrabBufferListSize += 1
      else:
         break
   MIL.MappControl(MIL.M_DEFAULT, MIL.M_ERROR, MIL.M_PRINT_ENABLE)

   # Initialize the user's processing function data structure.
   UserHookData = HookDataStruct(MilDigitizer, MilImageDisp, 0)

   # Start the processing. The processing function is called with every frame grabbed.
   ProcessingFunctionPtr = MIL.MIL_DIG_HOOK_FUNCTION_PTR(ProcessingFunction)
   MIL.MdigProcess(MilDigitizer, MilGrabBufferList, MilGrabBufferListSize, MIL.M_START, MIL.M_DEFAULT, ProcessingFunctionPtr, ctypes.byref(UserHookData))

   # Here the main() is free to perform other tasks while the processing is executing.
   # ---------------------------------------------------------------------------------

   # Print a message and wait for a key press after a minimum number of frames.
   get_input("Press <Enter> to stop.                    \n\n")

   # Stop the processing.
   MIL.MdigProcess(MilDigitizer, MilGrabBufferList, MilGrabBufferListSize, MIL.M_STOP, MIL.M_DEFAULT, ProcessingFunctionPtr, ctypes.byref(UserHookData))

   # Print statistics.
   ProcessFrameCount = MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_COUNT, None)
   ProcessFrameRate = MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_RATE, None)
   print("\n{:d} frames grabbed at {:.1f} frames/sec ({:.1f} ms/frame)".format(ProcessFrameCount, ProcessFrameRate, 1000.0/ProcessFrameRate))
   get_input("Press <Enter> to end.\n")
      
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