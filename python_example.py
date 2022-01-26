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
from datetime import datetime
import contextlib

# Get correct .dcf config file for the camera
DCF_FILENAME = "[WORKING CONFIG] MV2-D1280-640-CL-8_1280x1024_8Taps8bitCon.dcf"
DCF_PATH = os.path.join(os.getcwd(),"configs", DCF_FILENAME)
IMAGES_PATH = os.path.join(os.getcwd(), "images")
VIDEOS_PATH = os.path.join(os.getcwd(), "videos")

def generate_filename(file_extension):
   time = datetime.now ().strftime ("%H-%M-%S")
   
   if file_extension != "":
      fname = f"Capture-{time}.{str(file_extension)}"
      return fname

   return f"Capture-{time}"

# Text input function differs from 2.7 to 3.0. 
if sys.hexversion >= 0x03000000:
    get_input = input
else:
    get_input = raw_input


#Annotation flag. Set to M_YES to draw the frame number in the saved image. */
FRAME_NUMBER_ANNOTATION = MIL.M_YES

#Archive flag. Set to M_NO to disable AVI Import/Export to disk. */
SAVE_SEQUENCE_TO_DISK = MIL.M_YES

# User's processing function hook data structure.
class HookDataStruct(ctypes.Structure):
   _fields_ = [
      ("MilSystem", MIL.MIL_ID),
      ("MilDisplay", MIL.MIL_ID),
      ("MilImageDisp", MIL.MIL_ID),
      ("MilCompressedImage", MIL.MIL_INT),
      ("SaveSequenceToDisk", MIL.MIL_INT),
      ("NbGrabbedFrames", MIL.MIL_INT),
      ("NbArchivedFrames", MIL.MIL_INT)]

# Number of images in the buffering grab queue.
# Generally, increasing this number gives a better real-time grab.
BUFFERING_SIZE_MAX = 100

# User's processing function called every time a grab buffer is ready.
# --------------------------------------------------------------------

# Local defines. 
STRING_POS_X       = 20 
STRING_POS_Y       = 20 

def ArchiveFunction(HookType, HookId, HookDataPtr):
      
   # Retrieve the MIL_ID of the grabbed buffer. 
   ModifiedImage = MIL.MIL_ID(0)
   MIL.MdigGetHookInfo(HookId, MIL.M_MODIFIED_BUFFER + MIL.M_BUFFER_ID, ctypes.byref(ModifiedImage))
   
   # Extract the userdata structure
   UserData = ctypes.cast(ctypes.c_void_p(HookDataPtr), ctypes.POINTER(HookDataStruct)).contents
   
   # Increment the frame counter.
   UserData.NbGrabbedFrames += 1

   if(UserData.SaveSequenceToDisk):
      MIL.MbufExportSequence(os.path.join(VIDEOS_PATH, filename_video), MIL.M_DEFAULT, ctypes.byref(ModifiedImage),
                             1,MIL.M_DEFAULT,MIL.M_WRITE)

      UserData.NbArchivedFrames += 1

   #Copy the new grabbed image to the display
   # MIL.MbufCopy(ModifiedImage, UserData.MilImageDisp)
   
   return 0

# Main function.
# ---------------

def MdigProcessExample():
   # Allocate defaults.
   SaveSequenceToDisk = MIL.MIL_ID(SAVE_SEQUENCE_TO_DISK)
   MilCompressedImage = MIL.MIL_ID(MIL.M_NULL)
   MilGrabImages = []
   NbFrames, n = MIL.MIL_INT(0), MIL.MIL_INT(0)
   FrameCount, FrameMissed, NbFramesReplayed, Exit = MIL.MIL_INT(0), MIL.MIL_INT(0), MIL.MIL_INT(0), MIL.MIL_INT(0)
   FrameRate = ctypes.c_double(0)

   MilApplication = MIL.MappAlloc(MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)
   MilSystem = MIL.MsysAlloc(MIL.M_DEFAULT, MIL.M_SYSTEM_DEFAULT, MIL.M_DEFAULT, MIL.M_DEFAULT, None)
   MilDisplay = MIL.MdispAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)
   MilDigitizer = MIL.MdigAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT(DCF_PATH), MIL.M_DEFAULT, None)

   SizeX = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_X, None)
   SizeY = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_Y, None)

   MilImageDisp = MIL.MbufAlloc2d(MilSystem,SizeX,SizeY, 8 + MIL.M_UNSIGNED, MIL.M_IMAGE + MIL.M_PROC + MIL.M_DISP + MIL.M_GRAB, None)

   MIL.MbufClear(MilImageDisp, MIL.M_COLOR_BLACK)
   MIL.MdispSelect(MilDisplay, MilImageDisp)

   # Grab continuously on the display and wait for a key press
   MIL.MdigGrabContinuous(MilDigitizer, MilImageDisp)  
   # Print a message.
   print("\nSEQUENCE ACQUISITION SCRIPT")
   print("-----------------------------\n")
   print(f"Using configuration file from:\n{DCF_PATH}\n")

   
   
   # Halt continuous grab. 
   get_input("Press <Enter> to start capture.\n")

   global filename_video, filename_image 
   filename = generate_filename("")
   filename_video = filename+".avi"
   filename_image = filename+".png"

   save_path = os.path.join(os.getcwd(), "images")

   with change_directory(save_path):
      MIL.MdigHalt(MilDigitizer)
      MIL.MbufExport(f"{filename}.png", MIL.M_PNG, MilImageDisp)

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

   if(SaveSequenceToDisk.value):
      print(f"Saving sequence to file {filename_video}\n")
      MIL.MbufExportSequence(os.path.join(VIDEOS_PATH, filename_video), MIL.M_AVI_DIB, MIL.M_NULL,
                             MIL.M_NULL, MIL.M_DEFAULT, MIL.M_OPEN);

   # Initialize the user's processing function data structure.
   UserHookData = HookDataStruct(MilSystem, MilDisplay, MilImageDisp,
      MilCompressedImage, SaveSequenceToDisk, 0,0)

   ArchiveFunctionPtr = MIL.MIL_DIG_HOOK_FUNCTION_PTR(ArchiveFunction)

   MIL.MdigProcess(MilDigitizer, MilGrabBufferList, MilGrabBufferListSize,
                   MIL.M_START, MIL.M_DEFAULT, ArchiveFunctionPtr,
                   ctypes.byref(UserHookData))

   # Print a message and wait for a key press after a minimum number of frames.
   get_input("Press <Enter> to stop.                    \n")

   # Stop the processing.
   MIL.MdigProcess(MilDigitizer, MilGrabBufferList, MilGrabBufferListSize,
                   MIL.M_STOP, MIL.M_DEFAULT, ArchiveFunctionPtr,
                   ctypes.byref(UserHookData))

   # Get processing statistics
   MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_RATE, ctypes.byref(FrameRate));
   MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_COUNT, ctypes.byref(FrameCount));
   MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_MISSED, ctypes.byref(FrameMissed));

   print(f"{FrameCount.value} frames saved ({FrameMissed.value} missed), at {FrameRate.value:.2f} fps\n")
   print(f"Image file saved to {os.path.join(IMAGES_PATH, filename_image)}")
   print(f"Video file saved to {os.path.join(VIDEOS_PATH, filename_video)}\n")

   if(SaveSequenceToDisk.value):
      MIL.MbufExportSequence(os.path.join(VIDEOS_PATH, filename_video), MIL.M_DEFAULT, MIL.M_NULL, MIL.M_NULL, FrameRate, MIL.M_CLOSE);

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


@contextlib.contextmanager
def change_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)
   
if __name__ == "__main__":
   MdigProcessExample()