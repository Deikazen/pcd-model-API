import cv2
import numpy as np


def extracted_feature(binary_image):

    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    total_area = 0
    total_perimeter = 0
    crack_count = 0

    valid_contours = []

    for cnt in contours:

        area = cv2.contourArea(cnt)

        # filter noise kecil
        if area > 30:

            perimeter = cv2.arcLength(cnt, True)

            if perimeter > 0:
                # Circularity = (4 * pi * area) / (perimeter^2)
                # Retak biasanya memiliki circularity yang sangat rendah (mendekati 0)
                # karena bentuknya yang memanjang dan tidak beraturan.
                circularity = (4 * np.pi * area) / (perimeter * perimeter)

                # Filter ganda: Sangat ketat untuk area kecil, lebih longgar untuk area besar
                # Ini membantu menghilangkan noise kecil di Negative sambil menangkap retakan besar di Positive
                if (circularity < 0.01) or (area > 200 and circularity < 0.1):

                    total_area += area
                    total_perimeter += perimeter
                    crack_count += 1

                    valid_contours.append(cnt)

    features = {
        "total_area": total_area,
        "total_perimeter": total_perimeter,
        "crack_count": crack_count
    }

    return features, valid_contours
