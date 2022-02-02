import cv2
import sys
import os

VIDEO_PATH="C:\\Users\\UVis\\Desktop\\graphene\\tests\\outputs\\video.avi"
EXPORT_PATH="C:\\Users\\UVis\\Desktop\\graphene\\tests\\outputs\\images\\"

class avi2jpg:
    def __init__(self,input_path,output_path):
        self.input_path = input_path
        self.output_path = output_path

    def convert(self):
        vidcap = cv2.VideoCapture(self.input_path)
        success,image = vidcap.read()
        count = 0
        while success:
            framecount = "{number:06}".format(number=count)
            cv2.imwrite(self.output_path+framecount+".jpg", image) 
            success,image = vidcap.read()
            print('Read a new frame: ', success)
            count += 1

if __name__ == "__main__":
    converter = avi2jpg(VIDEO_PATH, EXPORT_PATH)
    converter.convert()

        