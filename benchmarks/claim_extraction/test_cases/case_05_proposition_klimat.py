TEST_CASE = {
    "id": "case_05",
    "name": "Proposition om klimat",
    "description": "Propositionstext om klimatåtgärder med tydlig regeringsposition",
    "document_type": "proposition",
    "text": (
        "Prop. 2023/24:176 Klimatpolitiska handlingsplanen\n\n"
        "Regeringen föreslår att riksdagen godkänner den klimatpolitiska "
        "handlingsplanen för perioden 2024–2027.\n\n"
        "Regeringen bedömer att Sverige ska nå nettonollutsläpp senast 2045. "
        "För att nå dit krävs en kombination av teknikutveckling, "
        "elektrifiering och koldioxidinfångning. Regeringen avser att införa "
        "ett nytt stödsystem för bio-CCS som möjliggör negativa utsläpp. "
        "Utsläppen från transportsektorn ska minska genom fortsatt elektrifiering "
        "och en omställning av reduktionsplikten. Industrin ska ges "
        "förutsättningar att ställa om genom långsiktiga elavtal och "
        "tillståndsprocesser som kortas ned. Klimatpolitiken ska vara "
        "kostnadseffektiv och teknikneutral."
    ),
    "expected_claims": [
        {
            "subject": "Regeringen",
            "topic": "klimat",
            "stance": "support",
            "evidence": "Sverige ska nå nettonollutsläpp senast 2045",
            "confidence_min": 0.85,
        },
    ],
}
