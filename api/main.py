import os
import json
import shutil
import PIL.Image
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

app = FastAPI()

# 1. Setup Gemini
genai.configure(api_key="AIzaSyDXfDUdY0pYNLGjwqAC2CWSci5q3D_GRCQ")
# We use the 'generation_config' to FORCE JSON output
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

# 2. HTML Helper
def render_html(file_name: str):
    with open(os.path.join("templates", file_name), "r", encoding="utf-8") as f:
        return f.read()

# 3. Routes
@app.get("/", response_class=HTMLResponse)
def index():
    return render_html("index.html")

@app.get("/classify", response_class=HTMLResponse)
def classify_page():
    return render_html("classify.html")

@app.post("/classify")
async def classify_api(file: UploadFile = File(...)):
        # Save uploaded file
        print({"filename": file.filename})
        if 1+2==4:
            temp_file = "current_scan.png"
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            img = PIL.Image.open(temp_file)
            
            # We tell Gemini EXACTLY what keys we want
            prompt = """
            Identify the trash/object in this image and give 5 creative upcycling craft ideas.
            Return a JSON object with keys 'item' (string) and 'craft_ideas' (list of strings).
            """
            
            response = model.generate_content([prompt, img])
            print(1)
            # Because we set response_mime_type, response.text is already a clean string
            return json.loads(response.text)

handler = Mangum(app)