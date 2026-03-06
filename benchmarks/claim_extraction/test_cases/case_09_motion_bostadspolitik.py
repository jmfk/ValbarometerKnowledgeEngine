TEST_CASE = {
    "id": "case_09",
    "name": "Motion om bostadspolitik",
    "description": "Motion om bostadsbyggande och hyresreglering",
    "purpose": "Tests extraction of two claims where one supports reform and the other opposes existing regulation, requiring correct stance differentiation.",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:1789 av Annie Lööf m.fl. (C)\n\n"
        "Förslag till riksdagsbeslut\n\n"
        "Riksdagen ställer sig bakom det som anförs i motionen om reformer "
        "för ökat bostadsbyggande och tillkännager detta för regeringen.\n\n"
        "Motivering\n\n"
        "Bostadsbristen är ett av Sveriges mest akuta samhällsproblem. "
        "Centerpartiet föreslår en genomgripande reformering av plan- och "
        "byggprocessen för att korta handläggningstiderna. Kommunernas "
        "planmonopol bör luckras upp och det statliga överklagningsmaskineriet "
        "förenklas. Vi vill införa fri hyressättning i nyproduktion för att "
        "stimulera byggande av fler hyresrätter. Rörligheten på bostadsmarknaden "
        "måste öka genom sänkt reavinstskatt och reformerade "
        "ränteavdrag. Strandskyddet bör reformeras i grunden för att "
        "möjliggöra mer byggande i attraktiva lägen utanför storstäderna."
    ),
    "expected_claims": [
        {
            "subject": "Centerpartiet",
            "topic": "bostadspolitik",
            "stance": "support",
            "evidence": "genomgripande reformering av plan- och byggprocessen för att korta handläggningstiderna",
            "confidence_min": 0.8,
        },
        {
            "subject": "Centerpartiet",
            "topic": "hyresreglering",
            "stance": "oppose",
            "evidence": "fri hyressättning i nyproduktion för att stimulera byggande",
            "confidence_min": 0.7,
        },
    ],
}
