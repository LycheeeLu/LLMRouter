import re

from ..agents import faq_agent
from ..agents import order_agent

class LLMRouter:

    def __init__(self, faq_agent: faq_agent, order_agent: order_agent, llm_function):
        self.faq_agent = faq_agent
        self.order_agent = order_agent
        self.llm_function = llm_function


    def route(self, query: str) -> str:
        # classification first, same as the ones in evaluation.py
        classification_prompt = f"""You are a routing system for a veterinary clinic customer service bot.

Classify this customer query into ONLY ONE category:
- FAQ: General questions about hours, services, pricing, appointments, location, or policies
- ORDER: Questions about prescription orders, lab results, test results, or supply orders

Query: {query}

Respond with ONLY one word: FAQ or ORDER"""


        intent_raw = self.llm_function(classification_prompt).strip().upper()
        print(intent_raw)
        if intent_raw.startswith("ERROR CALLING"):
            intent = self._fallback_intent(query)
        else:
            intent = intent_raw

        # Routing needs to fix here no if else.
        if "FAQ" in intent:
            return self.faq_agent.handle(query)
        else:
            return self.order_agent.handle(query)


# simple fallback when LLM API fails
    def _fallback_intent(self, query: str) -> str:

        query_lower = query.lower()
        if re.search(r"ord\d+", query_lower) or any(
            keyword in query_lower for keyword in ("order", "tracking", "shipment", "status", "lab")
        ):
            return "ORDER"
        return "FAQ"
