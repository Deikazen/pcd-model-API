from classification import classification
from feature_extraction import extracted_feature
from preprocessing import preprocessing_image
import cv2
import numpy as np


image_path = r"dataset\negative\01403.jpg "

img, gray, blur, canny, close = preprocessing_image(image_path)

features, valid_contours = extracted_feature(close)

total_area = features['total_area']

status = classification(total_area)
total_crack = features['crack_count']
total_perimeter = features["total_perimeter"]

print(status)
print(f'Total Crack:{total_crack}')
print(f'total perimeter : {total_perimeter}')
print(f"total area {total_area} ")

cv2.imshow('image', img)
cv2.imshow('grayscale', gray)
cv2.imshow('blur', blur)
cv2.imshow('canny', canny)
cv2.imshow('close', close)

cv2.waitKey(0)
cv2.destroyAllWindows()
