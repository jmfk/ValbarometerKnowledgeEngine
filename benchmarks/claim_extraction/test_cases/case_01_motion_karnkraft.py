TEST_CASE = {
    "id": "case_01",
    "name": "Motion om kärnkraft",
    "description": "Tydlig motion som förespråkar kärnkraftsutbyggnad",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:1456 av Lars Eriksson m.fl. (M)\n\n"
        "Förslag till riksdagsbeslut\n\n"
        "Riksdagen ställer sig bakom det som anförs i motionen om behovet av "
        "ny kärnkraft och tillkännager detta för regeringen.\n\n"
        "Motivering\n\n"
        "Sverige står inför en historisk elförsörjningsutmaning. Den kraftigt "
        "ökande elektrifieringen av industri och transporter kräver en fördubbling "
        "av elproduktionen till 2045. Kärnkraften är den enda storskaliga, "
        "planerbara och fossilfria energikällan som kan leverera den baslast "
        "som krävs. Vi anser att regeringen bör vidta åtgärder för att möjliggöra "
        "uppförandet av minst två nya kärnkraftsreaktorer före 2035. De senaste "
        "årens energikris har visat att intermittenta energikällor som vind- och "
        "solkraft inte ensamma kan garantera leveranssäkerhet. Kärnkraften måste "
        "vara en central del av Sveriges framtida energimix."
    ),
    "expected_claims": [
        {
            "subject": "Moderaterna",
            "topic": "kärnkraft",
            "stance": "support",
            "evidence": "Vi anser att regeringen bör vidta åtgärder för att möjliggöra uppförandet av minst två nya kärnkraftsreaktorer före 2035",
            "confidence_min": 0.8,
        }
    ],
}
