import cv2
import numpy as np


def preprocessing_image(image_path):

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ganti jadinya pake Bilateral yang kata AI sangat pintar, lets try.
    blur = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # Canny otsu method

    ht, _ = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lt = 0.5 * ht
    canny = cv2.Canny(blur, ht, lt)

    kernel = np.ones((3, 3), dtype=np.uint8)

    close = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)

    return img, gray, blur, canny, close
