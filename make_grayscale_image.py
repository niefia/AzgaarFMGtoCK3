#!/usr/bin/python3

# Genreates a PNG containing the terrain height in grayscale.

import util
import sys
import os


def conv_grayscale(in_path,out_path):

  input_path = in_path
  
  file_not_present = False
  count = 0
  while (file_not_present == False):
    output_path = os.path.join(out_path, 'simulation'+str(count)+'.png')
    if (os.path.isfile(output_path) == False):
        file_not_present = True
    count += 1

  height, _ = util.load_from_file(input_path)
  util.save_as_png(height, output_path)