import glob
import cv2

from src.preprocessing import preprocessing_image
from src.feature_extraction import extracted_feature
from src.classification import classification

image_positive = glob.glob(r"dataset/positive/*.jpg")
image_negative = glob.glob(r"dataset/negative/*.jpg")



# print(len(image_positive))
# print(len(image_negative))


img_positive = []
img_negative = []

for i in image_positive:
    img_positive.append(i)

for i in image_negative:
    img_negative.append(i)


for i in img_positive[i]