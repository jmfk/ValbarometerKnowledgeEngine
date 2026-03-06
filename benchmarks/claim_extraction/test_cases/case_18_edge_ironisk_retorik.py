TEST_CASE = {
    "id": "case_18",
    "name": "Ironisk retorik",
    "description": "Text med sarkasm och retoriska frågor som kan vilseleda modellen",
    "document_type": "anförande",
    "text": (
        "Anf. 89 Jonas Sjöstedt (V):\n\n"
        "Herr talman! Vilken fantastisk idé av regeringen att sänka skatten "
        "för de rikaste med 15 miljarder kronor. Det är ju precis vad Sverige "
        "behöver när vårdköerna växer och skolorna saknar lärare. Och visst, "
        "låt oss privatisera ännu mer – det har ju fungerat så strålande "
        "hittills. Caremaskandalen var kanske bara en tillfällighet. "
        "Nej, herr talman, Vänsterpartiet har en annan vision. Vi vill "
        "investera i människor, inte i skattesänkningar till de som redan "
        "har mest. Vi vill ha en välfärd som fungerar för alla, inte bara "
        "för de som har råd att köpa sig förbi kön."
    ),
    "expected_claims": [
        {
            "subject": "Vänsterpartiet",
            "topic": "skattesänkningar",
            "stance": "oppose",
            "evidence": "investera i människor, inte i skattesänkningar till de som redan har mest",
            "confidence_min": 0.8,
        },
        {
            "subject": "Vänsterpartiet",
            "topic": "privatisering",
            "stance": "oppose",
            "evidence": "låt oss privatisera ännu mer – det har ju fungerat så strålande hittills",
            "confidence_min": 0.7,
        },
    ],
}
