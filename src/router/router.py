from agents import faq_agent
from agents import order_agent

class LLMRouter:

    def __init__(self, faq_agent: faq_agent, order_agent: order_agent, llm_function):
        self.faq_agent = faq_agent
        self.order_agent = order_agent
        self.llm_function = llm_function


    def route(self, query: str) -> str:
        # classification first
        classification_prompt = f"""You are a routing system for a veterinary clinic customer service bot.

Classify this customer query into ONLY ONE category:
- FAQ: General questions about hours, services, pricing, appointments, location, or policies
- ORDER_STATUS: Questions about prescription orders, lab results, test results, or supply orders

Query: {query}

Respond with ONLY one word: FAQ or ORDER_STATUS"""

        intent = self.llm_function(classification_prompt).strip().upper()

        # Routing
        if "FAQ" in intent:
            return self.faq_agent.handle(query, self.llm_function)
        else:
            return self.order_agent.handle(query, self.llm_function)

