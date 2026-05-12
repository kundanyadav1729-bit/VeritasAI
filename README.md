# VeritasAI 🛡️

VeritasAI is a multimodal, AI-powered misinformation detector built to combat the rapid spread of fake news, specifically targeting WhatsApp forwards and social media screenshots in the Indian context. 

Instead of relying on an AI's static memory (which can hallucinate), VeritasAI uses a Live Web-Augmented Generation (WAG) architecture. It actively scrapes real-time data from a whitelist of highly trusted journalistic and government sources to verify claims and provide evidence-backed verdicts.

## Features
* Text & Image Analysis: Type a claim directly or upload a screenshot (like a WhatsApp forward or fake tweet).
* Computer Vision (OCR): Extracts text from compressed images using Tesseract OCR.
* Live Fact-Checking Pipeline: Scrapes verified sources (e.g., AltNews, PIB India) in real-time to gather supporting or debunking evidence.
* Explainable AI: Provides a clear Fake, True, or Unclear verdict alongside a confidence score, logical reasoning, and clickable source links.
* Responsive UI: Built with a modern, dark-mode Glassmorphism design.

## Tech Stack
* Frontend: HTML5, JavaScript, Tailwind CSS (Hosted on GitHub Pages)
* Backend: Python, FastAPI (Containerized with Docker, Hosted on Render)
* AI Engine: Groq API (High-speed LLM inference)
* Web Scraping: BeautifulSoup4, Requests
* OCR Engine: Tesseract, Pillow

## How It Works
1. The user submits a text claim or uploads an image via the frontend.
2. If an image is uploaded, the FastAPI backend uses Tesseract OCR to extract the raw text.
3. The backend searches a hardcoded whitelist of trusted fact-checking websites for keywords related to the claim.
4. The scraped context and the original claim are fed into the Groq LLM.
5. The AI analyzes the evidence, determines a verdict, and sends the results (with source URLs) back to the user interface.

## Local Setup
If you want to run this project locally on your machine:

1. Clone the repository
2. Install the system requirements (Tesseract OCR must be installed on your OS)
3. Create a virtual environment and run: `pip install -r requirements.txt`
4. Create a `.env` file in the backend folder and add your API key: `GROQ_API_KEY=your_key_here`
5. Start the backend server: `cd backend && uvicorn main:app --reload`
6. Open `frontend/index.html` in your browser.