import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.verifier import Verifier
import pytesseract
from PIL import Image
import io

# Initialize the FastAPI Server
app = FastAPI(title="VeritasAI API")

# Allow the frontend to talk to the backend without security blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our RAG Engine
engine = Verifier()

# Define what a standard text request looks like
class ClaimRequest(BaseModel):
    text: str

# CHANGED: Removed 'async' so FastAPI automatically runs this in a background thread
@app.post("/api/verify")
def verify_text_claim(request: ClaimRequest):
    """Handles standard text claims OR pasted URLs."""
    try:
        input_text = request.text.strip()
        extracted_text = None

        # SMART DETECT: If the user pasted a URL, scrape the article first!
        if input_text.startswith("http://") or input_text.startswith("https://"):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(input_text, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            # Extract all the paragraph text from the news article
            paragraphs = soup.find_all('p')
            article_text = " ".join([p.get_text() for p in paragraphs])

            if len(article_text) < 20:
                raise HTTPException(status_code=400, detail="Could not extract readable article text from this URL.")

            # Only take the first 2000 characters so we don't overload the AI
            input_text = article_text[:2000]
            extracted_text = f"🔗 Scraped from URL: {request.text}"

        # Send the text (or scraped article) to the Hybrid AI engine
        result = engine.verify_claim(input_text)

        # If it was a URL, show the user that we read it
        if extracted_text:
            result["extracted_text"] = extracted_text

        return result

    except Exception as e:
        print(f"Error analyzing text/url: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze claim.")

# CHANGED: Removed 'async'
@app.post("/api/verify-image")
def verify_image_claim(file: UploadFile = File(...)):
    """Handles screenshot uploads, runs OCR, then runs RAG AI."""
    try:
        # Read the uploaded image file directly into memory
        image_bytes = file.file.read() # CHANGED: synchronous read
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run Tesseract OCR to extract the text
        extracted_text = pytesseract.image_to_string(image).strip()
        
        # If the image was blurry or had no text, reject it
        if not extracted_text or len(extracted_text) < 5:
            raise HTTPException(status_code=400, detail="Could not read any clear text from this image. Please upload a clearer screenshot.")
        
        # CHANGED: Removed 'await'
        result = engine.verify_claim(extracted_text)
        
        # Attach the text we read to the result so the user can see what the AI saw
        result["extracted_text"] = extracted_text
        
        return result

    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))