TEST_CASE = {
    "id": "case_10",
    "name": "Motion om arbetsmarknad",
    "description": "Motion om arbetsrätt och fackliga rättigheter",
    "purpose": "Tests extraction of a single claim from a motion with multiple policy proposals that all fall under the same overarching labor rights topic.",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:2456 av Teresa Carvalho m.fl. (S)\n\n"
        "Förslag till riksdagsbeslut\n\n"
        "Riksdagen ställer sig bakom det som anförs i motionen om stärkt "
        "arbetsrätt och tillkännager detta för regeringen.\n\n"
        "Motivering\n\n"
        "Socialdemokraterna ser med oro på den ökande otryggheten på "
        "arbetsmarknaden. Andelen osäkra anställningar – visstid, gig-jobb "
        "och inhyrd arbetskraft – har ökat kraftigt. Arbetsrätten måste "
        "stärkas så att tillsvidareanställning förblir normen på svensk "
        "arbetsmarknad. Vi föreslår att hyvling – där arbetsgivare ensidigt "
        "sänker anställdas arbetstid – förbjuds. Strejkrätten ska värnas "
        "och fackförbundens möjligheter att teckna kollektivavtal stärkas. "
        "Lönedumpning genom utstationerad arbetskraft måste motverkas genom "
        "skärpta regler och effektivare kontroller. En stark arbetsrätt är "
        "grunden för den svenska modellen."
    ),
    "expected_claims": [
        {
            "subject": "Socialdemokraterna",
            "topic": "arbetsrätt",
            "stance": "support",
            "evidence": "Arbetsrätten måste stärkas så att tillsvidareanställning förblir normen",
            "confidence_min": 0.85,
        },
    ],
}
