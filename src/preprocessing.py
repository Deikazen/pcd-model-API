import cv2
import numpy as np


def preprocessing_image(image_path):

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")

    resized_img = cv2.resize(img, (224, 224))

    gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

    # Blur sedikit lebih besar untuk mengurangi noise halus
    blur = cv2.GaussianBlur(gray, (5, 5), 0.0)

    # Canny otsu method
    ht, _ = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lt = 0.5 * ht
    
    # Canny edge detection (pastikan urutan lt dan ht benar)
    canny = cv2.Canny(blur, int(lt), int(ht))

    # Gunakan kernel 5x5 dan Dilation untuk menebalkan garis retakan
    # Ini membuat retakan terdeteksi lebih luas dan persentase lebih realistis
    kernel = np.ones((5, 5), dtype=np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=1)

    # Tutup celah-celah kecil di dalam area retakan
    close = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    return img, resized_img, gray, blur, canny, close
