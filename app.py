from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import cv2
import numpy as np
import os
import tempfile
import shutil
import base64


from src.preprocessing import preprocessing_image
from src.feature_extraction import extracted_feature
from src.classification import classification

app = FastAPI(title="Crack Detection API")

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
        # Note: preprocessing_image now returns 6 items
        img_original, img_resized, gray, blur, canny, binary_img = preprocessing_image(temp_path)

        # Step B: Feature Extraction
        features, contours = extracted_feature(binary_img)
        area = features["total_area"]

        # Step C: Classification
        prediction = classification(area)

        # Helper to encode to base64
        def encode_img(img):
            _, buffer = cv2.imencode('.jpg', img)
            return base64.b64encode(buffer).decode('utf-8')

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
                "binary": encode_img(binary_img)
            }
        }


    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

