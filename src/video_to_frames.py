import cv2
import sys
import os

VIDEO_PATH = os.path.join(os.path.join(os.path.dirname(__file__), os.path.pardir), "tests")
EXPORT_PATH = os.path.join(os.path.join(os.path.dirname(__file__), os.path.pardir), "tests\\outputs\\images\\")


class avi2jpg:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def convert(self):
        vidcap = cv2.VideoCapture(self.input_path)
        success, image = vidcap.read()
        count = 0
        while success:
            framecount = "{number:06}".format(number=count)
            cv2.imwrite(self.output_path + framecount + ".jpg", image)
            success, image = vidcap.read()
            if (count % 100 == 0):
                print(f'Reading frame {count}: ', success)
            count += 1


if __name__ == "__main__":
    print(f"Place your video file in the directory {VIDEO_PATH}")
    filename = input("Please enter the filename with file extension: ")
    print(os.path.join(VIDEO_PATH, filename))
    converter = avi2jpg(os.path.join(VIDEO_PATH, filename), EXPORT_PATH)
    converter.convert()
