import requests
import os

# Ganti dengan path gambar yang ada di dataset Anda
image_path = "dataset/positive/Positive_1.jpg"

if not os.path.exists(image_path):
    # Jika path spesifik tidak ada, cari gambar pertama di folder dataset/positive
    import glob
    files = glob.glob("dataset/positive/*.jpg")
    if files:
        image_path = files[0]
    else:
        print("No test image found.")
        exit()

url = "http://127.0.0.1:5000/predict"

with open(image_path, "rb") as img:
    files = {"image": img}
    response = requests.post(url, files=files)

print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())
