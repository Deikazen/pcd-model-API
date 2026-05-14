import glob
import cv2

from src.preprocessing import preprocessing_image
from src.feature_extraction import extracted_feature
from src.classification import classification

import glob
import cv2
import numpy as np

# Pastikan fungsi-fungsi yang Anda buat sudah terdefinisi atau diimport
# dari src.preprocessing, src.feature_extraction, dll.

# 1. Kumpulkan semua path gambar
image_paths = {
    "Positive": glob.glob(r"dataset/positive/*.jpg"),
    "Negative": glob.glob(r"dataset/negative/*.jpg")
}

print("Memulai Proses Klasifikasi...\n")
print(f"{'Folder':<10} | {'File Name':<20} | {'Area':<10} | {'Result'}")
print("-" * 60)

# 2. Looping utama
for label, paths in image_paths.items():
    for path in paths:
        # Nama file untuk tampilan
        file_name = path.split(
            "\\")[-1] if "\\" in path else path.split("/")[-1]

        try:
            # Step A: Preprocessing
            # Kita ambil hasil 'close' (binary) untuk ekstraksi fitur
            img_original, gray, blur, canny, binary_img = preprocessing_image(
                path)

            # Step B: Feature Extraction
            features, contours = extracted_feature(binary_img)
            area = features["total_area"]

            # Step C: Classification
            prediction = classification(area)

            # Tampilkan Hasil
            print(f"{label:<10} | {file_name:<20} | {area:<10.2f} | {prediction}")

            # (Opsional) Jika ingin menampilkan visualisasi per gambar:
            # cv2.drawContours(img_original, contours, -1, (0, 0, 255), 2)
            # cv2.imshow("Result", img_original)
            # cv2.waitKey(100)

        except Exception as e:
            print(f"Error memproses {file_name}: {e}")

cv2.destroyAllWindows()
print("\nProses Selesai.")
