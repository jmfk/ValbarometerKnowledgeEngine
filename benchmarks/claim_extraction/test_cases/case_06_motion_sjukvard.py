TEST_CASE = {
    "id": "case_06",
    "name": "Motion om sjukvård",
    "description": "Motion om vårdköer och förstatligande av sjukvården",
    "purpose": "Tests extraction of two claims with opposing stances from the same subject — one supporting nationalization and one opposing privatization.",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:3201 av Nooshi Dadgostar m.fl. (V)\n\n"
        "Förslag till riksdagsbeslut\n\n"
        "Riksdagen ställer sig bakom det som anförs i motionen om att utreda "
        "ett förstatligande av sjukvården och tillkännager detta för "
        "regeringen.\n\n"
        "Motivering\n\n"
        "De svenska vårdköerna är oacceptabelt långa. Regionerna har misslyckats "
        "med att säkerställa en jämlik vård i hela landet. Vänsterpartiet "
        "föreslår att staten tar över ansvaret för sjukvården från regionerna "
        "för att garantera likvärdig vård oavsett var man bor. Privata "
        "vårdföretag som drivs med vinstintresse måste fasas ut ur den "
        "offentligt finansierade vården. Istället bör resurser satsas på "
        "att anställa fler sjuksköterskor och läkare med bättre villkor. "
        "Vårdvalet i sin nuvarande form bör avskaffas eftersom det leder "
        "till att resurser koncentreras till välbeställda områden."
    ),
    "expected_claims": [
        {
            "subject": "Vänsterpartiet",
            "topic": "sjukvård",
            "stance": "support",
            "evidence": "staten tar över ansvaret för sjukvården från regionerna för att garantera likvärdig vård",
            "confidence_min": 0.8,
        },
        {
            "subject": "Vänsterpartiet",
            "topic": "privatisering",
            "stance": "oppose",
            "evidence": "Privata vårdföretag som drivs med vinstintresse måste fasas ut",
            "confidence_min": 0.8,
        },
    ],
}
