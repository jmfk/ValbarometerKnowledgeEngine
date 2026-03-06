TEST_CASE = {
    "id": "case_12",
    "name": "Flera ämnen i samma text",
    "description": "Text som täcker minst tre helt olika politikområden",
    "purpose": "Tests extraction of three separate claims across entirely different policy areas (family, healthcare, defense) from a single text.",
    "document_type": "partiprogram",
    "text": (
        "Ur Kristdemokraternas valmanifest 2022\n\n"
        "Familjen är samhällets grundsten. Kristdemokraterna vill höja "
        "vårdnadsbidraget och ge familjer större valfrihet i barnomsorgen. "
        "Föräldrar – inte politiker – ska avgöra vad som är bäst för deras "
        "barn.\n\n"
        "Sjukvården behöver en nationell vårdgaranti som innebär att ingen "
        "ska behöva vänta mer än 30 dagar på specialistvård. Vi vill öka "
        "patientens makt genom ett förstärkt vårdval.\n\n"
        "Sverige behöver en starkare försvarsmakt. Anslagen till försvaret "
        "bör uppgå till minst 2 procent av BNP. Det civila försvaret "
        "måste återuppbyggas med moderna beredskapslager."
    ),
    "expected_claims": [
        {
            "subject": "Kristdemokraterna",
            "topic": "familjepolitik",
            "stance": "support",
            "evidence": "höja vårdnadsbidraget och ge familjer större valfrihet i barnomsorgen",
            "confidence_min": 0.8,
        },
        {
            "subject": "Kristdemokraterna",
            "topic": "sjukvård",
            "stance": "support",
            "evidence": "nationell vårdgaranti som innebär att ingen ska behöva vänta mer än 30 dagar",
            "confidence_min": 0.8,
        },
        {
            "subject": "Kristdemokraterna",
            "topic": "försvar",
            "stance": "support",
            "evidence": "Anslagen till försvaret bör uppgå till minst 2 procent av BNP",
            "confidence_min": 0.8,
        },
    ],
}
