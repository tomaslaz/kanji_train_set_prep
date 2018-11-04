import imageio
import random
import os
import pylab
import uuid
import PIL
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage, misc
import numpy as np

_const_font_dir = "fonts"
_number_of_img = 100
_font_size = 80
_image_size = 80

def read_in_fonts():
  """
  Get the paths for the font files

  """

  fonts = []

  font_files = os.listdir(_const_font_dir)

  for font_file in font_files:
    fonts.append(os.path.join(_const_font_dir, font_file))

  return fonts

def kanji_to_array(kanji, kanji_font_file, font_size, image_size):
  """


  """

  kanji_font = ImageFont.truetype(kanji_font_file, font_size, encoding = "unic")

  kanji_image = Image.new('LA', (image_size, image_size), (0, ))
  
  draw = ImageDraw.Draw(kanji_image)
  
  text_width, text_height = draw.textsize(kanji, font = kanji_font)
  
  draw.text(((image_size - text_width) / 2, (image_size - text_height) / 2), kanji, "white", font = kanji_font)
  
  del draw
  
  # TODO: change it to IO stream?
  temp_file = "%s.png" % (str(uuid.uuid4()))
  kanji_image.save(temp_file, "PNG")
  
  im = imageio.imread(temp_file, "PNG-PIL", pilmode="L")
  
  os.remove(temp_file)
  
  return im

def distort_image(image_arr, angle = 15.0, shift = 5.0, blur_radius = 3, factor = 2):
  """
  A method to randomly rotate and shift

  """
  
  new_image_arr = image_arr.astype(np.uint8)

  # rotoate and shift
  new_image_arr = misc.imresize(ndimage.shift(ndimage.rotate(new_image_arr, random.gauss(0, angle)), 
                       random.gauss(0, shift)), image_arr.shape)

  # blur and saturate
  new_image_arr = ndimage.gaussian_filter(new_image_arr, random.gauss(0, blur_radius))

  # clip values
  new_image_arr = np.clip(new_image_arr * factor, 0, 255)

  return new_image_arr

def prep_dist_images(image_arr, n_images, angle = 15.0, shift = 5.0, blur_radius = 3, factor = 2):
  """
  Prepares a list of a number of distorted images for a particular kanji

  """

  list_image_arr = np.zeros((n_images, image_arr.shape[0], image_arr.shape[1]), dtype = np.uint8)

  for i in range(n_images):
    new_image_arr = distort_image(image_arr, angle = angle, shift = shift, 
      blur_radius = blur_radius, factor = factor)

    list_image_arr[i, :] = new_image_arr[:,:]

  return list_image_arr

def kanji_list_diff_fonts(test_kanji_unicode, fonts_list, font_size, image_size):
  """


  """

  font_cnt = len(fonts_list)
  total_cnt = _number_of_img * font_cnt

  list_image_arr = np.zeros((total_cnt, image_size, image_size), dtype = np.uint8)

  font_i = 0
  for font in fonts_list:
    kanji_image_array = kanji_to_array(test_kanji_unicode, font, font_size, image_size)

    kanji_array_font_list = prep_dist_images(kanji_image_array, _number_of_img)
  
    list_image_arr[font_i*_number_of_img:(font_i+1)*_number_of_img, :] =  kanji_array_font_list[ : :]

    font_i += 1

  return list_image_arr

def prep_tain_list(kanji_list, kanji_labels, fonts_list, font_size, image_size):
  """

  """

  tot_kanji_samples = len(fonts_list) * _number_of_img
  tot_samples = len(kanji_list) * tot_kanji_samples

  kanji_train_data = np.zeros((tot_samples, image_size, image_size), dtype = np.uint8)
  kanji_train_labels = np.zeros(tot_samples, dtype = np.uint8)

  kanji_i = 0
  for kanji in kanji_list:
    kanji_samples = kanji_list_diff_fonts(kanji, fonts_list, _font_size, _image_size)

    kanji_train_data[kanji_i*tot_kanji_samples:(kanji_i+1)*tot_kanji_samples,:] = kanji_samples[::]

    kanji_train_labels[kanji_i*tot_kanji_samples:(kanji_i+1)*tot_kanji_samples] = np.repeat(kanji_labels[kanji_i], tot_kanji_samples)

    kanji_i += 1

  return kanji_train_data, kanji_train_labels

def main():
  """


  """

  # 0. Read in different fonts for training
  fonts_list = read_in_fonts()

  # 1. select kanji
  kanji_list = [u'\u4E86']
  kanji_labels = [1]

  # kanji with different fonts
  prep_tain_list(kanji_list, kanji_labels, fonts_list, _font_size, _image_size)

  # pylab.winter()
  # pylab.imshow(kanji_samples[199, :])
  # pylab.show()

  return

if __name__ == "__main__":

  main()

  print("Finished.")