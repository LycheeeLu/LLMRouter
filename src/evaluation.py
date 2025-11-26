import time
from typing import List, Dict, Callable
from .main import (
    FAQ_DATA,
    ORDER_DATA,
    FAQAgent,
    OrderAgent,
    LLMRouter,
    call_gemini,
    call_openai,
    call_anthropic,
    call_groq
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
    {"query": "Where is my order ORD123?", "expected": "ORDER"},
    {"query": "Is order ORD456 ready for pickup?", "expected": "ORDER"},
    {"query": "Can you check the status of ORD789?", "expected": "ORDER"},
    {"query": "When will my prescription ORD321 be ready?", "expected": "ORDER"},
    {"query": "Has ORD123 shipped yet?", "expected": "ORDER"},
    {"query": "I'm checking on my lab results for order ORD456", "expected": "ORDER"},
    {"query": "What's happening with order ORD789?", "expected": "ORDER"},
    {"query": "Track my order ORD321", "expected": "ORDER"},
    {"query": "Status of ORD123 please", "expected": "ORDER"},
    {"query": "Where's ORD456?", "expected": "ORDER"},
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
    """

    print(f"\n{'='*60}")
    print(f"Evaluating: {model_name}")
    print(f"{'='*60}")
    correct = 0
    total = len(test_cases)
    errors = []
    latencies = []

    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]

        try:
            # Measure ONLY LLM inference latency (not agent execution)
            start_time = time.time()
            predicted = classify_intent(query, llm_function)
            latency = time.time() - start_time
            latencies.append(latency)
            # Check first is the output valid
            valid_intents = ["FAQ", "ORDER"]
            is_valid = any(intent in predicted for intent in valid_intents)
            # invalid output
            if not is_valid:
                is_correct = False
                status = "WRONG"
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
                })

            print(f"{status} [{i:2d}/{total}] '{query[:35]:<35}' Expected: {expected:<12} Got: {predicted:<15} ({latency*1000:.0f}ms)")

        except Exception as e:
            print(f"✗ [{i:2d}/{total}] ERROR: {str(e)}")
            errors.append({
                "query": query,
                "expected": expected,
                "predicted": f"ERROR: {str(e)}",
            })



    # Calculate metrics
    accuracy = (correct / total) * 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p50_latency = sorted(latencies)[len(latencies)//2] if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0


    results = {
        "model": model_name,
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        #worse case scenario
        "p95_latency": p95_latency,
        "errors": errors,
    }

    print(f"\n {model_name} Results:")
    print(f"Accuracy:   {accuracy:.1f}% ({correct}/{total})")
    print(f"Latency:    avg={avg_latency*1000:.0f}ms, p50={p50_latency*1000:.0f}ms, p95={p95_latency*1000:.0f}ms")

    return results

def run_evaluation():
    """Run evaluation on all available models"""

    models_to_test = [
        ("GPT-4o-mini", call_openai),
        ("Gemini 2.0 Flash", call_gemini),
        ("llama3-70b-8192", call_groq),
        ("claude-sonnet-4", call_anthropic)

    ]

    # ("GPT-4o-mini", call_openai),
    # ("Gemini 2.0 Flash", call_gemini),

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
    print(f"{'Model':<25} {'Accuracy':<12} {'Avg Latency':<15} {'P95 Latency':<15} ")
    print("-"*100)

    for result in sorted(all_results, key=lambda x: x['accuracy'], reverse=True):
        print(
            f"{result['model']:<25} "
            f"{result['accuracy']:>6.1f}%{'':<5} "
            f"{result['avg_latency']*1000:>6.0f}ms{'':<8} "
            f"{result['p95_latency']*1000:>6.0f}ms{'':<8} "
        )

    # determine best model
    if all_results:
        print("RECOMMENDATION BASED ON SCORING")

       # Score each model (accuracy=70%, latency=30%)
        for result in all_results:
            accuracy_score = result['accuracy']
            latency_score = max(0, 100 - (result['avg_latency'] * 100))
            total_score = (accuracy_score * 0.7) + (latency_score * 0.3)
            result['total_score'] = total_score

        best = max(all_results, key=lambda x: x['total_score'])

        print(f"\nBest Overall (Weighted Score): {best['model']}")
        print(f"   Score: {best['total_score']:.1f}/100")


    # Save all results to a text file
    with open("all_results.txt", "w", encoding="utf-8") as f:
        for result in all_results:
            f.write(f"Model: {result['model']}\n")
            f.write(f"Accuracy: {result['accuracy']:.1f}%\n")
            f.write(f"Average Latency: {result['avg_latency']*1000:.0f}ms\n")
            f.write(f"P95 Latency: {result['p95_latency']*1000:.0f}ms\n")
            f.write("Errors:\n")
            for e in result["errors"]:
                f.write(f"  - Query: {e['query']}\n")
                f.write(f"    Expected: {e['expected']}\n")
                f.write(f"    Predicted: {e['predicted']}\n")
            f.write("\n" + "="*80 + "\n\n")


    return all_results


if __name__ == "__main__":
    run_evaluation()