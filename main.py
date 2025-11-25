from mock_data.faq_data import FAQ_DATA
from mock_data.order_data import ORDER_DATA
from router.call_LLM import call_gemini, call_openai
from router.router import LLMRouter
from tests import test_queries

def main():

    faq_agent = faq_agent(FAQ_DATA)
    order_agent = order_agent(ORDER_DATA)

    # change it to call different LLM
    llm_function = call_gemini
    router = LLMRouter(faq_agent, order_agent, llm_function)

    # Test queries
    test = test_queries

    print("=======Testing LLM router=========")
    for query in test_queries:
        print(f"Customer: {query}")
        answer = router.route(query)
        print(f"Bot: {answer}\n")

if __name__ == "__main__":
    main()
