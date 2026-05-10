from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import google.generativeai as genai
import PIL.Image
import os
import json

app = FastAPI()

# Mount the 'static' folder so your CSS/JS works
# Ensure you have a folder named 'static' in your directory
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. Configure Gemini
# NOTE: Avoid hardcoding keys in public repos! Use os.getenv('GEMINI_KEY') for production.
genai.configure(api_key="AIzaSyDXfDUdY0pYNLGjwqAC2CWSci5q3D_GRCQ")
model = genai.GenerativeModel('gemini-2.5-flash')

# --- TEMPLATE LOADER HELPER ---
def render_html(file_name: str):
    path = os.path.join("templates", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# --- PAGE ROUTES ---

@app.get("/", response_class=HTMLResponse)
def index():
    return render_html("index.html")

@app.get("/impact", response_class=HTMLResponse)
def impact():
    return render_html("impact.html")

@app.get("/marketplace", response_class=HTMLResponse)
def marketplace():
    return render_html("marketplace.html")

# --- API LOGIC ---

@app.post("/api/classify")
async def classify_api(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_path = "temp_image.png"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    img = PIL.Image.open(temp_path)
    
    prompt = """
    Analyze this image for waste management. 
    Return strictly a JSON object with these keys:
    'item': Name of the object.
    'craft_ideas': A list of 5 creative upcycling ideas.
    """
    
    response = model.generate_content([prompt, img])
    
    # Clean and parse JSON
    text = response.text.replace('```json', '').replace('```', '').strip()
    try:
        data = json.loads(text)
        return data
    except:
        return {"error": "Failed to parse Gemini response", "raw": text}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI on Netlify!"}

handler = Mangum(app)