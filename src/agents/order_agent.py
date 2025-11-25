# using hardcoded dictionary answers
from typing import Dict, Any
import re

class OrderAgent:
    def __init__ (self, order_data: Dict[str, Dict[str, Any]]):
        self.order_data = order_data

    def respond(self, query: str) -> str:
        # sanitize capital letters
        q = query.lower()

        # ORD### like ORD123
        # try to extract ID through this pattern
        match = re.search(r'ORD\d+', query.upper())
        if match:

            order_id = match.group(0)
            # try to find ID in mockdata
            if order_id in self.order_data:
                order = self.order_data[order_id]
                return f"Order {order_id} for {order['pet']}: {order['item']} - Status: {order['status']}. {order.get('tracking', '')}"

        # fallback response
        return (
             "Could you rephrase your question?"
             "To check your order, please provide your order ID like ORD123 "
        )