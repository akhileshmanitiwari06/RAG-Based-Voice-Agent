from app.rag.retriever import search


queries = [
    "check BGP",
    "show subscribers",
    "check active alarms",
]


for query in queries:

    print("\nQUERY:", query)

    results = search(
        query,
        top_k=1,
    )

    for result in results:

        print(
            "MATCH:",
            result["template_id"]
        )

        print(
            "SCORE:",
            result["score"]
        )

        print(
            "SOURCE:",
            result["source"]
        )