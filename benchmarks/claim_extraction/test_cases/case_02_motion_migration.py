TEST_CASE = {
    "id": "case_02",
    "name": "Motion om migration",
    "description": "Motion som argumenterar för striktare migrationspolitik",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:2891 av Jimmie Åkesson m.fl. (SD)\n\n"
        "Förslag till riksdagsbeslut\n\n"
        "Riksdagen ställer sig bakom det som anförs i motionen om en grundläggande "
        "reformering av Sveriges migrationspolitik och tillkännager detta för "
        "regeringen.\n\n"
        "Motivering\n\n"
        "Sveriges migrationspolitik har under decennier varit alltför generös, "
        "vilket har lett till omfattande integrationsproblem, ökad segregation "
        "och betydande kostnader för välfärdssystemet. Sverigedemokraterna föreslår "
        "att asylinvandringen ska begränsas till ett absolut minimum och att "
        "fokus istället ska läggas på återvandringsprogram. Uppehållstillstånd "
        "bör som huvudregel vara tillfälliga. Anhöriginvandringen måste "
        "villkoras med krav på självförsörjning och kunskaper i svenska språket. "
        "Kommunernas möjlighet att säga nej till ytterligare mottagning bör "
        "stärkas genom lag."
    ),
    "expected_claims": [
        {
            "subject": "Sverigedemokraterna",
            "topic": "migration",
            "stance": "oppose",
            "evidence": "asylinvandringen ska begränsas till ett absolut minimum och att fokus istället ska läggas på återvandringsprogram",
            "confidence_min": 0.85,
        }
    ],
}
