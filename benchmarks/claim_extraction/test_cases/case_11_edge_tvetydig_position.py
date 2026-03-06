TEST_CASE = {
    "id": "case_11",
    "name": "Tvetydig position",
    "description": "Text där partiets position är genuint oklar eller ambivalent",
    "document_type": "anförande",
    "text": (
        "Anf. 78 Johan Pehrson (L):\n\n"
        "Herr talman! Frågan om cannabis-avkriminalisering är komplex. "
        "Liberalerna har traditionellt värnat individens frihet, och det finns "
        "argument för att nuvarande narkotikapolitik inte har levererat de "
        "resultat vi hoppats på. Samtidigt ser vi oroande signaler från länder "
        "som legaliserat – ökat bruk bland unga och trafiksäkerhetsproblem. "
        "Vi behöver mer evidens innan vi kan ta ställning. En statlig utredning "
        "bör tillsättas för att grundligt analysera effekterna av alternativa "
        "narkotikapolitiska modeller. Det vore oansvarigt att fatta ett så "
        "stort beslut utan ordentligt underlag."
    ),
    "expected_claims": [
        {
            "subject": "Liberalerna",
            "topic": "narkotikapolitik",
            "stance": "unclear",
            "evidence": "Vi behöver mer evidens innan vi kan ta ställning",
            "confidence_min": 0.6,
        }
    ],
}
