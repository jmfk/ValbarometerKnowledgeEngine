TEST_CASE = {
    "id": "case_16",
    "name": "Implicit stance",
    "description": "Position som aldrig uttrycks explicit men framgår av kontexten",
    "purpose": "Tests extraction of claims where the stance is never stated directly but must be inferred from rhetorical context and implied criticism.",
    "document_type": "anförande",
    "text": (
        "Anf. 45 Magdalena Andersson (S):\n\n"
        "Herr talman! Jag vill tala om vad som händer i kommunerna runt om "
        "i Sverige. I Malmö har man tvingats lägga ned tre fritidsgårdar. "
        "I Norrköping saknas det skolkuratorer. I Gävle har äldreomsorgen "
        "skurits ned till farliga nivåer. Det här är konsekvensen av "
        "regeringens skattesänkningar. Varje krona som ges i skattesänkning "
        "till höginkomsttagare är en krona som tas från välfärden. "
        "Barnen i Rosengård behöver den kronan mer. De äldre i Gävle "
        "behöver den kronan mer. Jag frågar statsministern: var det "
        "verkligen värt det?"
    ),
    "expected_claims": [
        {
            "subject": "Socialdemokraterna",
            "topic": "skattesänkningar",
            "stance": "oppose",
            "evidence": "Varje krona som ges i skattesänkning till höginkomsttagare är en krona som tas från välfärden",
            "confidence_min": 0.7,
        },
        {
            "subject": "Socialdemokraterna",
            "topic": "välfärd",
            "stance": "support",
            "evidence": "Barnen i Rosengård behöver den kronan mer. De äldre i Gävle behöver den kronan mer",
            "confidence_min": 0.7,
        },
    ],
}
