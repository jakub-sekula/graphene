import cv2
import numpy as np
import glob
import os

OUTPUT_PATH="C:\\Users\\UVis\\Desktop\\graphene\\tests\\outputs\\"
IMAGES_PATH="C:\\Users\\UVis\\Desktop\\graphene\\tests\\outputs\\images\\*.jpg"


def main():
    f = str(input("Enter output filename: "))

    frameSize = (1280,1024)

    out = cv2.VideoWriter(os.path.join(OUTPUT_PATH,f+".mp4"),cv2.VideoWriter_fourcc(*'MP4V'), 30, frameSize)
    count = 0

    for filename in glob.glob(IMAGES_PATH):
        if (count % 10 == 0): print(filename)
        img = cv2.imread(filename)
        img_resized = cv2.resize(img, frameSize)
        out.write(img_resized)
        count += 1

    out.release()

    os.chdir(os.path.join(OUTPUT_PATH,"images"))

    for file in os.listdir():
        os.remove(file)


if __name__=='__main__':
    main()