import time
from typing import List, Dict, Callable
from main import (
    FAQ_DATA, OrderAgent, LLMRouter,
    FAQAgent, ORDER_DATA,
    call_gemini, call_openai
)

# Test cases with expected intents
TEST_CASES = [
    # FAQ queries
    {"query": "What time do you close on Saturday?", "expected": "FAQ"},
    {"query": "How much does a wellness exam cost?", "expected": "FAQ"},
    {"query": "Do you offer emergency services?", "expected": "FAQ"},
    {"query": "Where is your clinic located?", "expected": "FAQ"},
    {"query": "Can I book an appointment online?", "expected": "FAQ"},
    {"query": "What services do you provide?", "expected": "FAQ"},
    {"query": "Are you open on Sunday?", "expected": "FAQ"},
    {"query": "How much is a dental cleaning?", "expected": "FAQ"},
    {"query": "What's your emergency number?", "expected": "FAQ"},
    {"query": "How can I contact you?", "expected": "FAQ"},

    # Order status queries
    {"query": "Where is my order ORD123?", "expected": "ORDER_STATUS"},
    {"query": "Is order ORD456 ready for pickup?", "expected": "ORDER_STATUS"},
    {"query": "Can you check the status of ORD789?", "expected": "ORDER_STATUS"},
    {"query": "When will my prescription ORD321 be ready?", "expected": "ORDER_STATUS"},
    {"query": "Has ORD123 shipped yet?", "expected": "ORDER_STATUS"},
    {"query": "I'm checking on my lab results for order ORD456", "expected": "ORDER_STATUS"},
    {"query": "What's happening with order ORD789?", "expected": "ORDER_STATUS"},
    {"query": "Track my order ORD321", "expected": "ORDER_STATUS"},
    {"query": "Status of ORD123 please", "expected": "ORDER_STATUS"},
    {"query": "Where's ORD456?", "expected": "ORDER_STATUS"},
]


def classify_intent(query: str, llm_function: Callable) -> str:
    # same from router.py
    classification_prompt = f"""You are a routing system for a veterinary clinic customer service bot.

Classify this customer query into ONLY ONE category:
- FAQ: General questions about hours, services, pricing, appointments, location, or policies
- ORDER: Questions about prescription orders, lab results, test results, or supply orders

Query: {query}

Respond with ONLY one word: FAQ or ORDER"""

    response = llm_function(classification_prompt).strip().upper()
    if "FAQ" in response:
        return "FAQ"
    elif "ORDER" in response:
        return "ORDER"
    return response


def evaluate_model(model_name: str, llm_function: Callable, test_cases: List[Dict]) -> Dict:
    """
    Evaluate LLM routing performance on 3 key metrics:
    1. Accuracy - Does LLM predict correct intent?
    2. Latency - How fast is the LLM inference?
    3. Robustness - Does LLM output valid intents?
    """

    print(f"\n{'='*60}")
    print(f"Evaluating: {model_name}")
    print(f"{'='*60}")
    correct = 0
    total = len(test_cases)
    errors = []
    latencies = []
    invalid_outputs = []

    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]

        try:
            # Measure ONLY LLM inference latency (not agent execution)
            start_time = time.time()
            predicted = classify_intent(query, llm_function)
            latency = time.time() - start_time
            latencies.append(latency)
            # Check robustness: is the output valid
            valid_intents = ["FAQ", "ORDER"]
            is_valid = any(intent in predicted for intent in valid_intents)
            # invalid output
            if not is_valid:
                invalid_outputs.append({
                    "query": query,
                    "output": predicted
                })
                is_correct = False
                status = "INVALID"
            # Check accuracy
            else:
                # predicted intent === expected intent
                is_correct = (expected in predicted)
                status = "CORRECT" if is_correct else "WRONG"
            if is_correct:
                correct += 1
            else:
                errors.append({
                    "query": query,
                    "expected": expected,
                    "predicted": predicted,
                    "valid": is_valid
                })

            print(f"{status} [{i:2d}/{total}] '{query[:35]:<35}' Expected: {expected:<12} Got: {predicted:<15} ({latency*1000:.0f}ms)")

        except Exception as e:
            print(f"✗ [{i:2d}/{total}] ERROR: {str(e)}")
            errors.append({
                "query": query,
                "expected": expected,
                "predicted": f"ERROR: {str(e)}",
                "valid": False
            })
            invalid_outputs.append({
                "query": query,
                "output": f"ERROR: {str(e)}"
            })
