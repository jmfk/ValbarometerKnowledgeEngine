TEST_CASE = {
    "id": "case_07",
    "name": "Partiprogram om utbildning",
    "description": "Utdrag ur partiprogram om skolpolitik och betyg",
    "purpose": "Tests extraction of two claims from a party manifesto covering education policy and profit restrictions in schools.",
    "document_type": "partiprogram",
    "text": (
        "Ur Socialdemokraternas valmanifest 2022\n\n"
        "En skola för alla\n\n"
        "Socialdemokraterna vill att alla barn ska ha rätt till en bra skola "
        "oavsett bakgrund. Vinstjakten i skolan måste stoppas – skattepengar "
        "avsedda för barns utbildning ska inte bli vinst i riskkapitalbolags "
        "fickor. Vi vill stärka den kommunala skolan genom ökade statsbidrag "
        "riktade till skolor i utsatta områden. Läraryrkets attraktivitet "
        "måste höjas genom bättre löner och arbetsvillkor. Vi vill också "
        "reformera betygssystemet genom att införa ämnesbetyg istället för "
        "kursbetyg i gymnasiet, så att elever ges möjlighet att utvecklas "
        "under hela sin utbildning utan att tidiga misslyckanden permanentas."
    ),
    "expected_claims": [
        {
            "subject": "Socialdemokraterna",
            "topic": "utbildning",
            "stance": "support",
            "evidence": "alla barn ska ha rätt till en bra skola oavsett bakgrund",
            "confidence_min": 0.8,
        },
        {
            "subject": "Socialdemokraterna",
            "topic": "vinster i välfärden",
            "stance": "oppose",
            "evidence": "Vinstjakten i skolan måste stoppas",
            "confidence_min": 0.8,
        },
    ],
}
