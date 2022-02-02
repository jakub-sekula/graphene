import cv2
import numpy as np
import glob

OUTPUT_PATH="C:\\Users\\UVis\\Desktop\\test\\video_slowed2.mp4"
IMAGES_PATH="C:\\Users\\UVis\\Desktop\\test\\images\\*.jpg"


def main():
    frameSize = (640, 480)

    out = cv2.VideoWriter(OUTPUT_PATH,cv2.VideoWriter_fourcc(*'MP4V'), 30, frameSize)

    for filename in glob.glob(IMAGES_PATH):
        print(filename)
        img = cv2.imread(filename)
        img_resized = cv2.resize(img, frameSize)
        out.write(img_resized)

    out.release()

if __name__=='__main__':
    main()