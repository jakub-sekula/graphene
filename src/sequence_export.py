#!/usr/bin/env python3
from __future__ import print_function

import sys
import os
import ctypes
import mil as MIL
import contextlib
import shutil
import myutils
import time
from threading import Timer

# Config and filesystem path settings
DCF_FILENAME = "[WORKING CONFIG] MV2-D1280-640-CL-8_1280x1024_8Taps8bitCon.dcf"
DCF_PATH = os.path.join("C:\\Users\\UVis\\Desktop\\graphene\\configs", DCF_FILENAME)
TEMP_PATH = "D:\\"
IMAGES_PATH = "C:\\Users\\UVis\\Desktop\\graphene\\images"
VIDEOS_PATH = "C:\\Users\\UVis\\Desktop\\graphene\\videos"

#Annotation flag. Set to M_YES to draw the frame number in the saved image. */
FRAME_NUMBER_ANNOTATION = MIL.M_YES

#Archive flag. Set to M_NO to disable AVI Import/Export to disk. */
SAVE_SEQUENCE_TO_DISK = MIL.M_YES

# Number of images in the buffering grab queue.
# Generally, increasing this number gives a better real-time grab.
BUFFERING_SIZE_MAX = 500



# User's processing function hook data structure.
class HookDataStruct(ctypes.Structure):
   _fields_ = [
      ("MilSystem", MIL.MIL_ID),
      ("MilDisplay", MIL.MIL_ID),
      ("MilImageDisp", MIL.MIL_ID),
      ("SaveSequenceToDisk", MIL.MIL_INT),
      ("NbGrabbedFrames", MIL.MIL_INT),
      ("NbArchivedFrames", MIL.MIL_INT)]


def ArchiveFunction(HookType, HookId, HookDataPtr):
      
   # Retrieve the MIL_ID of the grabbed buffer. 
   ModifiedImage = MIL.MIL_ID(0)
   MIL.MdigGetHookInfo(HookId, MIL.M_MODIFIED_BUFFER + MIL.M_BUFFER_ID, ctypes.byref(ModifiedImage))
   
   # Extract the userdata structure
   UserData = ctypes.cast(ctypes.c_void_p(HookDataPtr), ctypes.POINTER(HookDataStruct)).contents
   
   # Increment the frame counter.
   UserData.NbGrabbedFrames += 1

   if(UserData.SaveSequenceToDisk):
      MIL.MbufExportSequence(os.path.join(TEMP_PATH, filename_video), MIL.M_DEFAULT, ctypes.byref(ModifiedImage),
                             1,MIL.M_DEFAULT,MIL.M_WRITE)

      UserData.NbArchivedFrames += 1

   #Copy the new grabbed image to the display
   #MIL.MbufCopy(ModifiedImage, UserData.MilImageDisp)
   
   return 0

# Main function.
def sequence_export():

   # Allocate defaults.
   SaveSequenceToDisk = MIL.MIL_ID(SAVE_SEQUENCE_TO_DISK)
   MilGrabImages = []
   NbFrames, n = MIL.MIL_INT(0), MIL.MIL_INT(0)
   FrameCount, FrameMissed, NbFramesReplayed, Exit = MIL.MIL_INT(0), MIL.MIL_INT(0), MIL.MIL_INT(0), MIL.MIL_INT(0)
   FrameRate = ctypes.c_double(0)

   MilApplication = MIL.MappAlloc(MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)
   MilSystem = MIL.MsysAlloc(MIL.M_DEFAULT, MIL.M_SYSTEM_DEFAULT, MIL.M_DEFAULT, MIL.M_DEFAULT, None)
   MilDisplay = MIL.MdispAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT("M_DEFAULT"), MIL.M_DEFAULT, None)
   MilDigitizer = MIL.MdigAlloc(MilSystem, MIL.M_DEFAULT, MIL.MIL_TEXT(DCF_PATH), MIL.M_DEFAULT, None)

   SizeX = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_X, None) # Should be 1280
   SizeY = MIL.MdigInquire(MilDigitizer, MIL.M_SIZE_Y, None) # Should be 1024

   MilImageDisp = MIL.MbufAlloc2d(MilSystem,SizeX,SizeY, 8 + MIL.M_UNSIGNED, MIL.M_IMAGE + MIL.M_PROC + MIL.M_DISP + MIL.M_GRAB, None)

   MIL.MbufClear(MilImageDisp, MIL.M_COLOR_BLACK)
   MIL.MdispSelect(MilDisplay, MilImageDisp)

   # Grab continuously on the display and wait for a key press
   MIL.MdigGrabContinuous(MilDigitizer, MilImageDisp)  
   

   print("\nSEQUENCE ACQUISITION SCRIPT")
   print("-----------------------------\n")
   print(f"Using configuration file from:\n{DCF_PATH}\n")
   
   
   # input("Press <Enter> to start capture.\n")
   time_limit=float(input("Enter recording time (maximum 8.50 seconds) and start capture: "))

   # Generate filenames for image and video files
   global filename_video, filename_image
   filename = myutils.generate_filename("")
   filename_video = "Video"+filename+".avi"
   filename_image = "Image"+filename+".png"

   # Halt continuous grab and save static image
   MIL.MdigHalt(MilDigitizer)
   MIL.MbufExport(os.path.join(IMAGES_PATH,filename_image), MIL.M_PNG, MilImageDisp)

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
      MIL.MbufExportSequence(os.path.join(TEMP_PATH, filename_video), MIL.M_AVI_DIB, MIL.M_NULL,
                             MIL.M_NULL, MIL.M_DEFAULT, MIL.M_OPEN);

   # Initialize the user's processing function data structure.
   UserHookData = HookDataStruct(MilSystem, MilDisplay, MilImageDisp,
                                 SaveSequenceToDisk, 0,0)

   ArchiveFunctionPtr = MIL.MIL_DIG_HOOK_FUNCTION_PTR(ArchiveFunction)

   MIL.MdigProcess(MilDigitizer, MilGrabBufferList, MilGrabBufferListSize,
                   MIL.M_START, MIL.M_DEFAULT, ArchiveFunctionPtr,
                   ctypes.byref(UserHookData))

   # start_time = time.time()
   # while(True):
   #    current_time= time.time()
   #    elapsed_time = current_time-start_time
   #    if(elapsed_time < 5):
   #       continue
   #    else:
   #       break

   prompt = "Press Enter to stop capture               \n"

   # t = Timer(input_time, exit)
   # t.start()
   # input("Press <Enter> to stop.                    \n")
   # # prompt = "You have %d seconds to choose the correct answer.................\n" % input_time
   # # answer = input(prompt)
   # t.cancel()


   try:
      myutils.input_with_timeout(prompt, time_limit)
   except myutils.TimeoutExpired:
      print(f'Time limit of {time_limit:.2f} seconds reached, saving file')
   else:
      pass

   # Print a message and wait for a key press after a minimum number of frames.
   # input("Press <Enter> to stop.                    \n")


   # Stop the processing.
   MIL.MdigProcess(MilDigitizer, MilGrabBufferList, MilGrabBufferListSize,
                   MIL.M_STOP, MIL.M_DEFAULT, ArchiveFunctionPtr,
                   ctypes.byref(UserHookData))

   # Get processing statistics
   MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_RATE, ctypes.byref(FrameRate));
   MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_COUNT, ctypes.byref(FrameCount));
   MIL.MdigInquire(MilDigitizer, MIL.M_PROCESS_FRAME_MISSED, ctypes.byref(FrameMissed));


   print(f"{FrameCount.value} frames saved ({FrameMissed.value} missed), at {FrameRate.value:.2f} fps\n")

   if(SaveSequenceToDisk.value):
      MIL.MbufExportSequence(os.path.join(TEMP_PATH, filename_video), MIL.M_DEFAULT, MIL.M_NULL, MIL.M_NULL, FrameRate, MIL.M_CLOSE);
      myutils.movefile(TEMP_PATH, VIDEOS_PATH, filename_video)

   print(f"Image file saved to {os.path.join(IMAGES_PATH, filename_image)}")
   print(f"Video file saved to {os.path.join(VIDEOS_PATH, filename_video)}\n")

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
   sequence_export()