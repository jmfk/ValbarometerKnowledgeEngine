TEST_CASE = {
    "id": "case_13",
    "name": "Historisk referens",
    "description": "Text som refererar till historiska positioner som inte längre gäller",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:892 av Per Bolund m.fl. (MP)\n\n"
        "Motivering\n\n"
        "Miljöpartiet har alltid stått i främsta ledet för kärnkraftens "
        "avveckling. I folkomröstningen 1980 kampanjade vi för linje 3 – "
        "omedelbar avveckling. Under 2010-talet drev vi igenom stängningen "
        "av Ringhals 1 och 2 som en del av energiöverenskommelsen. "
        "Idag ser vi dock att energiläget har förändrats. Den gröna "
        "omställningen kräver enorma mängder el. Miljöpartiet anser att "
        "befintliga kärnkraftverk bör kunna drivas vidare så länge de "
        "uppfyller säkerhetskraven, men vi motsätter oss statliga "
        "subventioner för nybyggnation. Framtidens energisystem ska byggas "
        "på förnybart – sol, vind och lagringsteknologi."
    ),
    "expected_claims": [
        {
            "subject": "Miljöpartiet",
            "topic": "kärnkraft",
            "stance": "mixed",
            "evidence": "befintliga kärnkraftverk bör kunna drivas vidare så länge de uppfyller säkerhetskraven, men vi motsätter oss statliga subventioner för nybyggnation",
            "confidence_min": 0.7,
        },
        {
            "subject": "Miljöpartiet",
            "topic": "förnybar energi",
            "stance": "support",
            "evidence": "Framtidens energisystem ska byggas på förnybart – sol, vind och lagringsteknologi",
            "confidence_min": 0.8,
        },
    ],
}
