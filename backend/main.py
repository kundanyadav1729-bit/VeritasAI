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
    allow_origins=["*"],  # In production, change this to your Vercel/GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our RAG Engine
engine = Verifier()

# Define what a standard text request looks like
class ClaimRequest(BaseModel):
    text: str

@app.post("/api/verify")
async def verify_text_claim(request: ClaimRequest):
    """Handles standard text claims from the input box."""
    try:
        # Send the text to the RAG AI engine
        result = await engine.analyze(request.text)
        return result
    except Exception as e:
        print(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze claim.")

@app.post("/api/verify-image")
async def verify_image_claim(file: UploadFile = File(...)):
    """Handles screenshot uploads, runs OCR, then runs RAG AI."""
    try:
        # Read the uploaded image file directly into memory (zero disk writing = faster for i3)
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run Tesseract OCR to extract the text
        extracted_text = pytesseract.image_to_string(image).strip()
        
        # If the image was blurry or had no text, reject it
        if not extracted_text or len(extracted_text) < 5:
            raise HTTPException(status_code=400, detail="Could not read any clear text from this image. Please upload a clearer screenshot.")
        
        # Send the extracted text to our AI engine
        result = await engine.analyze(extracted_text)
        
        # Attach the text we read to the result so the user can see what the AI saw
        result["extracted_text"] = extracted_text
        
        return result

    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))