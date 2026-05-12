import cv2
import numpy as np

from preprocessing import preprocessing_image
from feature_extraction import extracted_feature
from classification import classification

image_path = r"dataset\positive\00055.jpg"

img, gray, blur, canny, close = preprocessing_image(image_path)

features, valid_contours = extracted_feature(close)

total_area = features['total_area']

status = classification(total_area)
total_crack = features['crack_count']

print(status)
print(total_crack)
print(total_area)

cv2.imshow('image', img)
cv2.imshow('grayscale', gray)
cv2.imshow('blur', blur)
cv2.imshow('canny', canny)
cv2.imshow('close', close)

cv2.waitKey(0)
cv2.destroyAllWindows()
