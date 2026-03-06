TEST_CASE = {
    "id": "case_04",
    "name": "Anförande om försvar",
    "description": "Riksdagsanförande om försvarspolitik och NATO",
    "document_type": "anförande",
    "text": (
        "Anf. 47 Pål Jonson (M):\n\n"
        "Herr talman! Det säkerhetspolitiska läget i Europa har fundamentalt "
        "förändrats sedan Rysslands fullskaliga invasion av Ukraina. Sverige har "
        "tagit ett historiskt steg genom att ansöka om och nu bli medlem i NATO. "
        "Det är Moderaternas fasta övertygelse att Sverige skyndsamt måste nå "
        "försvarsutgifter på minst 2,5 procent av BNP. Vi behöver öka vår "
        "militära förmåga genom fler förband, bättre beväpning och fördjupat "
        "samarbete med våra allierade. Det handlar inte bara om att uppfylla "
        "NATO:s förväntningar utan om att skydda Sveriges territorium och "
        "medborgare. Totalförsvaret måste stärkas genom ökad civil beredskap "
        "och fler värnpliktiga."
    ),
    "expected_claims": [
        {
            "subject": "Moderaterna",
            "topic": "försvar",
            "stance": "support",
            "evidence": "Sverige skyndsamt måste nå försvarsutgifter på minst 2,5 procent av BNP",
            "confidence_min": 0.85,
        },
        {
            "subject": "Moderaterna",
            "topic": "NATO",
            "stance": "support",
            "evidence": "Sverige har tagit ett historiskt steg genom att ansöka om och nu bli medlem i NATO",
            "confidence_min": 0.8,
        },
    ],
}
