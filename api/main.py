from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI on Netlify!"}

# This is the entry point for Netlify Functions
handler = Mangum(app)