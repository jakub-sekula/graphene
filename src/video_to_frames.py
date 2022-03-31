import cv2
import sys
import os

VIDEO_PATH = "C:\\Users\\UVis\\Desktop\\graphene\\videos\\"
EXPORT_PATH = "C:\\Users\\UVis\\Desktop\\graphene\\tests\\outputs\\images\\"

VIDEO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'Particle tracking', 'Videos'))
EXPORT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'Particle tracking', 'Images'))


class avi2jpg:
    def __init__(self, input_path, output_path, original_filename):
        self.input_path = input_path
        self.output_path = output_path
        self.original_filename = os.path.splitext(original_filename)[0]
        print(self.original_filename)

    def convert(self):

        self.export_folder = os.path.join(self.output_path, self.original_filename)

        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
            print(f"Created new folder {self.export_folder}")

        vidcap = cv2.VideoCapture(self.input_path)
        success, image = vidcap.read()
        count = 0
        while success:
            framecount = "{number:06}".format(number=count)
            cv2.imwrite(os.path.join(self.export_folder, framecount) + ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            success, image = vidcap.read()
            if (count % 10 == 0):
                print('Read a new frame: ', count, success)
            count += 1


if __name__ == "__main__":
    filename = str(input("Enter filename of input video file (with extension): "))

    converter = avi2jpg(os.path.join(VIDEO_PATH, filename), EXPORT_PATH, filename)
    converter.convert()
