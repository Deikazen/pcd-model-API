from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import cv2
import os
import tempfile
import shutil
import base64

from src.preprocessing import preprocessing_image
from src.feature_extraction import extracted_feature
from src.classification import classification


app = FastAPI(title="Crack Detection API")

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# ini revisian reguler, menambah tanda pada kerusakan tembok
def create_marked_damage_image(image, contours, binary_img):
    marked_image = image.copy()

    # Bikin overlay merah dari hasil binary
    red_overlay = marked_image.copy()
    red_overlay[binary_img > 0] = (0, 0, 255)

    # Gabungkan gambar asli dengan overlay merah
    marked_image = cv2.addWeighted(marked_image, 0.75, red_overlay, 0.25, 0)

    # Tetap tambahkan kotak kuning dari contour
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 30:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(marked_image, (x, y), (x + w, y + h), (0, 255, 255), 2)

    return marked_image

#ini revisi praktikum, menambah perbandingan kerusakan tembok
def create_comparison_images(image, contours):
    h, w = image.shape[:2]

    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 30:
            valid_contours.append(contour)

    # Kalau tidak ada retakan, pakai gambar original sebagai fallback
    if len(valid_contours) == 0:
        return image.copy(), image.copy()

    # Ambil contour terbesar sebagai area rusak utama
    largest_contour = max(valid_contours, key=cv2.contourArea)
    x, y, cw, ch = cv2.boundingRect(largest_contour)

    # Tambahin padding biar crop area rusak tidak terlalu mepet
    padding = 25
    x1 = max(x - padding, 0)
    y1 = max(y - padding, 0)
    x2 = min(x + cw + padding, w)
    y2 = min(y + ch + padding, h)

    damaged_crop = image[y1:y2, x1:x2].copy()

    # Area halus diambil dari bagian gambar yang jauh dari area retakan
    crop_w = x2 - x1
    crop_h = y2 - y1

    # Default ambil pojok kanan atas sebagai area halus
    sx1 = max(w - crop_w - 10, 0)
    sy1 = 10
    sx2 = min(sx1 + crop_w, w)
    sy2 = min(sy1 + crop_h, h)

    # Kalau area halus terlalu dekat dengan retakan, pindah ke pojok kiri bawah
    overlap_x = not (sx2 < x1 or sx1 > x2)
    overlap_y = not (sy2 < y1 or sy1 > y2)

    if overlap_x and overlap_y:
        sx1 = 10
        sy1 = max(h - crop_h - 10, 0)
        sx2 = min(sx1 + crop_w, w)
        sy2 = min(sy1 + crop_h, h)

    smooth_crop = image[sy1:sy2, sx1:sx2].copy()

    return damaged_crop, smooth_crop


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        # Save uploaded file to a temporary location
        suffix = os.path.splitext(image.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            await image.seek(0)
            shutil.copyfileobj(image.file, temp)
            temp_path = temp.name

        # Step A: Preprocessing
        img_original, img_resized, gray, blur, canny, binary_img = preprocessing_image(temp_path)

        # Step B: Feature Extraction
        features, contours = extracted_feature(binary_img)
        area = features["total_area"]

        # Step tambahan: kasih tanda kerusakan pada gambar 
        marked_img = create_marked_damage_image(img_resized, contours, binary_img)

        #ini revisi praktikum, membandingkan kerusakan tembok dengan area halus
        damaged_crop, smooth_crop = create_comparison_images(img_resized, contours)

        # Step C: Classification
        prediction = classification(area)

        # Helper to encode to base64
        def encode_img(img):
            _, buffer = cv2.imencode(".jpg", img)
            return base64.b64encode(buffer).decode("utf-8")

        # Clean up temporary file
        os.remove(temp_path)

        return {
            "status": "success",
            "prediction": prediction,
            "details": {
                "total_area": float(area),
                "total_perimeter": float(features["total_perimeter"]),
                "crack_count": int(features["crack_count"])
            },
            "steps": {
                "original": encode_img(img_original),
                "resized": encode_img(img_resized),
                "grayscale": encode_img(gray),
                "blurred": encode_img(blur),
                "canny": encode_img(canny),
                "binary": encode_img(binary_img),
                "marked": encode_img(marked_img) ,
                "damaged_crop": encode_img(damaged_crop),
                "smooth_crop": encode_img(smooth_crop)
            }
        }

    except Exception as e:
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)