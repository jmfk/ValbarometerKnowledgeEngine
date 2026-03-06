TEST_CASE = {
    "id": "case_14",
    "name": "Negation och dubbel negation",
    "description": "Text med negationer som gör stance svårtolkad",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:4102 av Märta Stenevi m.fl. (MP)\n\n"
        "Motivering\n\n"
        "Miljöpartiet kan inte acceptera att regeringen inte agerar mot de "
        "ökande klyftorna i samhället. Det är inte rimligt att inte "
        "beskatta höga kapitalinkomster när välfärden underfinansieras. "
        "Vi motsätter oss inte skattesänkningar i princip, men vi kan "
        "inte stödja sänkningar som inte kompenseras med andra intäkter. "
        "Att inte höja skatten på finansiella transaktioner vore att inte "
        "ta ansvar för kommande generationer. Vi vill inte se ett samhälle "
        "där de med minst får bära den tyngsta bördan."
    ),
    "expected_claims": [
        {
            "subject": "Miljöpartiet",
            "topic": "skatt",
            "stance": "support",
            "evidence": "inte rimligt att inte beskatta höga kapitalinkomster när välfärden underfinansieras",
            "confidence_min": 0.6,
        },
    ],
}
