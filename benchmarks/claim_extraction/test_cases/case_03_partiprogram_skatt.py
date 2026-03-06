TEST_CASE = {
    "id": "case_03",
    "name": "Partiprogram om skattepolitik",
    "description": "Utdrag ur partiprogram med tydlig skattepolitisk position",
    "purpose": "Tests extraction of two distinct claims from the same subject, where a single text covers both tax policy and green tax shift as separate topics.",
    "document_type": "partiprogram",
    "text": (
        "Ur Centerpartiets partiprogram, antaget vid partistämman 2023\n\n"
        "Kapitel 7: En ekonomi som växer\n\n"
        "Centerpartiet vill sänka skatten på arbete för att det alltid ska löna "
        "sig att jobba. Marginalskatterna i Sverige är bland de högsta i världen "
        "och hämmar tillväxt och företagande. Vi vill avskaffa den statliga "
        "inkomstskatten så att ingen betalar mer än kommunalskatt på sin lön. "
        "Skatten på företagande måste sänkas för att stärka Sveriges "
        "konkurrenskraft. Samtidigt vill vi se en grön skatteväxling där "
        "miljöskadlig verksamhet beskattas hårdare medan skatten på arbete "
        "och företagande sänks."
    ),
    "expected_claims": [
        {
            "subject": "Centerpartiet",
            "topic": "skatt",
            "stance": "oppose",
            "evidence": "vill sänka skatten på arbete för att det alltid ska löna sig att jobba",
            "confidence_min": 0.8,
        },
        {
            "subject": "Centerpartiet",
            "topic": "miljö",
            "stance": "support",
            "evidence": "grön skatteväxling där miljöskadlig verksamhet beskattas hårdare",
            "confidence_min": 0.7,
        },
    ],
}
