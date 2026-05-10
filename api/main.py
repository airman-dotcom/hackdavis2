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
    # ... (save file logic remains the same) ...
    
    img = PIL.Image.open(temp_path)
    
    # IMPROVED PROMPT: Strict formatting instructions
    prompt = """Analyze this image. Identify the object and give 5 upcycling craft ideas.
    Return ONLY a raw JSON object. Do not include markdown code blocks.
    Structure:
    {"item": "name", "craft_ideas": ["idea1", "idea2", "idea3", "idea4", "idea5"]}"""
    
    response = model.generate_content([prompt, img])
    
    # ROBUST PARSING: Remove markdown backticks if Gemini adds them anyway
    text = response.text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "", 1).replace("```", "", 1).strip()
    elif text.startswith("```"):
        text = text.replace("```", "", 1).replace("```", "", 1).strip()

    try:
        data = json.loads(text)
        return data # Returns: {"item": "...", "craft_ideas": [...]}
    except Exception as e:
        print(f"JSON Error: {text}") # Check your terminal to see what Gemini actually sent
        return {"item": "Unknown Object", "craft_ideas": ["Could not generate ideas. Try again."]}
@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI on Netlify!"}

handler = Mangum(app)