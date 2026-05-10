const express = require('express');
const serverless = require('serverless-http');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
const upload = multer(); // Handles files in memory

// 1. Setup Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API);
const model = genAI.getGenerativeModel({ 
    model: "gemini-flash-latest",
    generationConfig: { responseMimeType: "application/json" }
});

// 2. Helper to load HTML (Looks up one level to find /templates)
const renderHtml = (fileName, res) => {
    const filePath = path.join(__dirname, '..', 'templates', fileName);
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            res.status(404).send(`<h1>Error: ${fileName} not found</h1>`);
        } else {
            res.send(data);
        }
    });
};

// 3. Routes for Pages
app.get('/', (req, res) => renderHtml('index.html', res));
app.get('/classify', (req, res) => renderHtml('classify.html', res));
app.get('/marketplace', (req, res) => renderHtml('marketplace.html', res));
app.get('/impact', (req, res) => renderHtml('impact.html', res));

// 4. The API Logic
app.post('/class', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No image uploaded" });
        }

        // Convert buffer to Google Generative AI format
        const imagePart = {
            inlineData: {
                data: req.file.buffer.toString("base64"),
                mimeType: req.file.mimetype,
            },
        };

        const prompt = `
            Identify the trash/object in this image. 
            Provide 5 creative upcycling craft ideas.
            Return ONLY a JSON object with:
            {
              "item": "Object Name",
              "craft_ideas": ["Idea 1", "Idea 2", "Idea 3", "Idea 4", "Idea 5"]
            }
        `;

        const result = await model.generateContent([prompt, imagePart]);
        const response = await result.response;
        const text = response.text();

        // Parse and return
        res.json(JSON.parse(text));
    } catch (error) {
        console.error("DEBUG ERROR:", error);
        res.status(500).json({ error: error.message });
    }
});

// For Netlify
module.exports.handler = serverless(app);