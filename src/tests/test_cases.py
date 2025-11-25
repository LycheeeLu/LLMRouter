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
