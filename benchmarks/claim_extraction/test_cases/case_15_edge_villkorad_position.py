TEST_CASE = {
    "id": "case_15",
    "name": "Villkorad position",
    "description": "Stöd som är villkorat med 'om' och 'under förutsättning att'",
    "purpose": "Tests whether the model identifies a conditional, 'mixed' stance when support is explicitly contingent on prerequisites being met.",
    "document_type": "anförande",
    "text": (
        "Anf. 203 Ebba Busch (KD):\n\n"
        "Herr talman! Kristdemokraterna är öppna för en höjning av pensionsåldern, "
        "men enbart under förutsättning att det sker i kombination med "
        "förbättrade villkor för de som har tunga yrken. En undersköterska "
        "som slitit i 40 år kan inte förväntas arbeta lika länge som en "
        "tjänsteman. Om garantipensionen höjs till en rimlig nivå och om "
        "det införs en rätt till omställning för de över 60, då kan vi "
        "diskutera en gradvis höjning. Men utan dessa reformer säger vi nej. "
        "Vi stödjer principen men inte utan villkor."
    ),
    "expected_claims": [
        {
            "subject": "Kristdemokraterna",
            "topic": "pension",
            "stance": "mixed",
            "evidence": "öppna för en höjning av pensionsåldern, men enbart under förutsättning att det sker i kombination med förbättrade villkor",
            "confidence_min": 0.7,
        },
    ],
}
