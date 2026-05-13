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
        # CHANGED: We removed the " fact check" keyword so it can find breaking news too!
        search_query = query 
        
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

    # CHANGED: Removed 'async' and renamed to 'verify_claim' to match your main.py perfectly!
    def verify_claim(self, claim):
        evidence_data = self.fetch_evidence(claim)
        
        # CHANGED: The Hybrid System Prompt to fix the Fact-Checker Paradox
        system_prompt = f"""
        You are VeritasAI, an expert, razor-sharp fact-checker. 
        Analyze this claim: "{claim}"
        Here is the evidence scraped from trusted websites: {evidence_data}

        Follow these strict rules:
        1. If the scraped evidence contains relevant information, use it to prove or debunk the claim.
        2. If the scraped evidence is EMPTY, but the claim involves well-established public facts (like political leaders, history, or science), you MUST use your internal knowledge to explicitly correct the user.
        3. NEVER be vague. If a claim is wrong, state the actual truth immediately.
        4. Format the output strictly as JSON with keys: 'verdict' (Real, Fake, or Unclear), 'confidence' (0-100), and 'explanation' (2-3 direct sentences). Do not say "The provided evidence is empty." Just state the facts.
        """

        chat_completion = self.groq_client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}],
            model="llama-3.1-8b-instant", 
            response_format={"type": "json_object"}
        )
        
        result = json.loads(chat_completion.choices[0].message.content)
        result["sources"] = [e["url"] for e in evidence_data]
        return result