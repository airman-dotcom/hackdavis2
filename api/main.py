import os
import json
import shutil
import PIL.Image
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

app = FastAPI()
gemini_api = os.getenv("GEMINI_API")
# 1. Setup Gemini
# Using your key - Ensure no spaces around it
genai.configure(api_key=gemini_api)

# FORCE JSON output mode to prevent markdown errors
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

# 2. Helper to load HTML
def render_html(file_name: str):
    try:
        path = os.path.join("templates", file_name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>Error: {file_name} not found in templates/ folder</h1>"

# 3. Routes for Pages
@app.get("/", response_class=HTMLResponse)
def index():
    return render_html("index.html")

@app.get("/classify", response_class=HTMLResponse)
def classify_page():
    return render_html("classify.html")

@app.get("/marketplace", response_class=HTMLResponse)
def marketplace():
    return render_html("marketplace.html")

@app.get("/impact", response_class=HTMLResponse)
def impact():
    return render_html("impact.html")

# 4. The API Logic (Fixed and Checked)
@app.post("/api/classify")
async def classify_api(file: UploadFile = File(...)):
        # Save the file to disk so PIL can read it
        temp_file = "current_scan.png"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Open with Pillow
        img = PIL.Image.open(temp_file)
        
        # Detailed prompt to ensure Gemini behaves
        prompt = """
        Identify the trash/object in this image. 
        Provide 5 creative upcycling craft ideas.
        Return ONLY a JSON object with:
        {
          "item": "Object Name",
          "craft_ideas": ["Idea 1", "Idea 2", "Idea 3", "Idea 4", "Idea 5"]
        }
        """
        
        # Generate content
        response = model.generate_content([prompt, img])
        
        # Debug print: See what Gemini actually returns in your terminal
        print(f"DEBUG: Gemini Response: {response.text}")
        
        # Parse the JSON string into a Python dict
        result = json.loads(response.text)
        return result


# For Netlify
handler = Mangum(app)