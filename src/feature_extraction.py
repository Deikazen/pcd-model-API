import cv2
import numpy as np


def extracted_feature(binary_image):

    # Gunakan RETR_EXTERNAL agar tidak menghitung kontur di dalam garis retakan tebal
    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    total_area = 0
    total_perimeter = 0
    crack_count = 0

    valid_contours = []

    for cnt in contours:

        area = cv2.contourArea(cnt)

        # Filter noise kecil. Karena sudah didilasi, ukurannya pasti membesar, pakai batas yang sedikit lebih tinggi
        if area > 80:

            perimeter = cv2.arcLength(cnt, True)

            if perimeter > 0:
                circularity = (4 * np.pi * area) / (perimeter * perimeter)

                # Longgarkan syarat circularity agar retakan tebal atau pendek tetap terdeteksi.
                # Retakan umumnya memanjang, sehingga circularity jauh dari 1 (bulat sempurna).
                # Kita gunakan batas < 0.6 untuk membedakannya dengan noise yang benar-benar bulat.
                if circularity < 0.6:

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
