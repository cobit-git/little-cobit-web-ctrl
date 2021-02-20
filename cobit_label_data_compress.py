# -*- coding: utf-8 -*-
"""
Scripts to use

Usage:
    cobit_label_data_compress.py data/

Description:
    This script find all PNG files in data folder and compress it.

"""

import sys
import os 
import glob
import zipfile

class CobitLabelDataCompress:

    def __init__(self):
        self.target_folder = "./data"
        self.files = os.listdir(self.target_folder)
        print(self.files)
        self.condition = self.target_folder+"/*.png"

    def compress(self):
        png_files = glob.glob(self.condition)
        print(png_files)
        with zipfile.ZipFile("car_image_angle.zip", 'w') as my_zip:
            for file in png_files:
                my_zip.write(file)
        my_zip.close()

    def download_zip_file(self):
        print("download zip file")

if __name__ == '__main__':
    comp = CobitLabelDataCompress()
    comp.compress()

'''
target_folder = sys.argv[1]

files = os.listdir(target_folder)

condition = target_folder+ "/*.png"

png_files = glob.glob(condition)
print(png_files)

with zipfile.ZipFile("car_image_angle.zip", 'w') as my_zip:
#my_zip = zipfile.ZipFile("car_image_angle.zip", 'w')
    for file in png_files:
        my_zip.write(file)
my_zip.close()
'''


