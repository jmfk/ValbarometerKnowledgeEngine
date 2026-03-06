TEST_CASE = {
    "id": "case_08",
    "name": "Anförande om rättspolitik",
    "description": "Anförande om hårdare straff och gängkriminalitet",
    "purpose": "Tests extraction of a single clear claim from a speech with strong language and multiple policy proposals that all belong to the same topic.",
    "document_type": "anförande",
    "text": (
        "Anf. 112 Gunnar Strömmer (M):\n\n"
        "Fru talman! Sverige befinner sig i en allvarlig situation med "
        "gängkriminalitet som saknar motstycke i vår moderna historia. "
        "Skjutningar och sprängningar drabbar oskyldiga människor och "
        "undergräver tryggheten i hela samhället. Moderaterna har konsekvent "
        "drivit linjen att straffen måste skärpas kraftigt. Vi har genomfört "
        "historiska straffskärpningar – dubblerade straff för gängrelaterade "
        "brott, slopad ungdomsrabatt för grova våldsbrott och utökade "
        "möjligheter till hemlig avlyssning. Men mer behövs. Vi vill införa "
        "anonyma vittnen, utöka visitationszoner och ge polisen bättre verktyg "
        "för att bekämpa den organiserade brottsligheten. Den som begår grova "
        "brott ska mötas av kännbara konsekvenser."
    ),
    "expected_claims": [
        {
            "subject": "Moderaterna",
            "topic": "rättspolitik",
            "stance": "support",
            "evidence": "straffen måste skärpas kraftigt",
            "confidence_min": 0.85,
        },
    ],
}
