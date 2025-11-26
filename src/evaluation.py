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
    3. Robustness - Does LLM output valid intents, instead of "BOTH"or "NULL" or "ERROR"
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


    # Calculate metrics
    accuracy = (correct / total) * 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p50_latency = sorted(latencies)[len(latencies)//2] if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0
    robustness = ((total - len(invalid_outputs)) / total) * 100

    results = {
        "model": model_name,
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        #worse case scenario
        "p95_latency": p95_latency,
        "robustness": robustness,
        "invalid_count": len(invalid_outputs),
        "errors": errors,
        "invalid_outputs": invalid_outputs
    }

    print(f"\n {model_name} Results:")
    print(f"Accuracy:   {accuracy:.1f}% ({correct}/{total})")
    print(f"Latency:    avg={avg_latency*1000:.0f}ms, p50={p50_latency*1000:.0f}ms, p95={p95_latency*1000:.0f}ms")
    print(f"Robustness: {robustness:.1f}% ({total - len(invalid_outputs)}/{total} valid outputs)")

    return results

def run_evaluation():
    """Run evaluation on all available models"""

    models_to_test = [
        ("GPT-4o-mini", call_openai),
        ("Gemini 2.0 Flash", call_gemini),
    ]

    all_results = []

    print("LLM Router Evaluation")
    print(f"Testing {len(models_to_test)} models on {len(TEST_CASES)} test cases")

    for model_name, llm_function in models_to_test:
        try:
            results = evaluate_model(model_name, llm_function, TEST_CASES)
            all_results.append(results)
            time.sleep(1)
        except Exception as e:
            print(f"Failed to evaluate {model_name}: {str(e)}")

    # Print comparison table
    print("\n" + "="*100)
    print("MODEL COMPARISON - THREE KEY METRICS")
    print("="*100)
    print(f"{'Model':<25} {'Accuracy':<12} {'Avg Latency':<15} {'P95 Latency':<15} {'Robustness':<12}")
    print("-"*100)

    for result in sorted(all_results, key=lambda x: x['accuracy'], reverse=True):
        print(
            f"{result['model']:<25} "
            f"{result['accuracy']:>6.1f}%{'':<5} "
            f"{result['avg_latency']*1000:>6.0f}ms{'':<8} "
            f"{result['p95_latency']*1000:>6.0f}ms{'':<8} "
            f"{result['robustness']:>6.1f}%"
        )