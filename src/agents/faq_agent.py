# using hardcoded dictionary answers
from typing import Dict, Any

class FAQAgent:
    def __init__ (self, faq_data: Dict[str, str]):
        self.faq_data = faq_data

    def handle(self, query: str) -> str:
        # sanitize capital letters
        q = query.lower()

        # keyword matching
        if "hour" in q or "open" in q or "close" in q or "closing" in q or "time" in q:
            return self.faq_data["hours"]

        if "emergency" in q or "urgent" in q or "after hours" in q:
            return self.faq_data["emergency"]

        if "service" in q or "offer" in q or "provide" in q or "do you do" in q or "what do you" in q:
            return self.faq_data["services"]

        if "where" in q or "locat" in q or "address" in q or "find you" in q:
            return self.faq_data["location"]

        if "contact" in q or "phone" in q or "call" in q or "email" in q or "reach" in q:
            return self.faq_data["contact"]

        if "appointment" in q or "book" in q or "schedule" in q or "reservation" in q:
            return self.faq_data["appointment"]

        if "cost" in q or "price" in q or "pricing" in q or "how much" in q or "fee" in q:
            return self.faq_data["pricing"]

        # fallback response
        return (
             "Could you rephrase your question?"
        )
