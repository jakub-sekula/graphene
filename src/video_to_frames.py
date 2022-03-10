import cv2
import sys
import os

VIDEO_PATH="C:\\Users\\UVis\\Desktop\\graphene\\videos\\"
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
            cv2.imwrite(self.output_path+framecount+".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]) 
            success,image = vidcap.read()
            if (count % 10 == 0): print('Read a new frame: ', count, success)
            count += 1

if __name__ == "__main__":
    filename = str(input("Enter filename: "))

    converter = avi2jpg(os.path.join(VIDEO_PATH,filename), EXPORT_PATH)
    converter.convert()

        
        
        