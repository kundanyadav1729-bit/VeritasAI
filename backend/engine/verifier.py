import os
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

class Verifier:
    def __init__(self):
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.trusted_sources = [
    # Global Heavyweights
    "reuters.com", "apnews.com", "bbc.com", "npr.org", "aljazeera.com",
    # Dedicated Fact Checkers
    "politifact.com", "snopes.com", "factcheck.org", "leadstories.com",
    # Indian & Regional Fact Checkers
    "thehindu.com", "altnews.in", "boomlive.in", "pib.gov.in", "smhoaxdetective.com", "vishvasnews.com"
]

    def fetch_evidence(self, query):
        evidence = []
        search_query = f"{query} fact check"
        
        for url in search(search_query, num_results=5):
            if any(source in url for source in self.trusted_sources):
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = soup.find_all('p')
                    text = ' '.join([p.text for p in paragraphs[:3]]) 
                    evidence.append({"url": url, "text": text})
                except Exception:
                    continue
        return evidence

    async def analyze(self, claim):
        evidence_data = self.fetch_evidence(claim)
        
        prompt = f"""
        Analyze this claim: "{claim}"
        Here is evidence from trusted sources: {evidence_data}
        Determine if the claim is Real, Fake, or Misleading. 
        Provide a confidence score (0-100) and a 2-sentence explanation.
        Format the output strictly as JSON with keys: verdict, confidence, explanation.
        """

        chat_completion = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            response_format={"type": "json_object"}
        )
        
        result = json.loads(chat_completion.choices[0].message.content)
        result["sources"] = [e["url"] for e in evidence_data]
        return result