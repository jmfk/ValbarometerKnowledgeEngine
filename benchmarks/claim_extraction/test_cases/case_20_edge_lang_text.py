TEST_CASE = {
    "id": "case_20",
    "name": "Lång text med utspädd information",
    "description": "Lång text där den relevanta claim-informationen är utspridd bland bakgrundstext",
    "document_type": "motion",
    "text": (
        "Motion 2023/24:5678 av Elisabeth Svantesson m.fl. (M)\n\n"
        "Förslag till riksdagsbeslut\n\n"
        "Riksdagen ställer sig bakom det som anförs i motionen om ekonomisk "
        "politik och tillkännager detta för regeringen.\n\n"
        "Motivering\n\n"
        "Den svenska ekonomin har genomgått betydande förändringar under de "
        "senaste decennierna. Från den djupa krisen på 1990-talet, genom "
        "IT-bubblan och den globala finanskrisen 2008, till pandemins "
        "ekonomiska konsekvenser – varje epok har ställt nya krav på den "
        "ekonomiska politiken. Sverige har historiskt haft en stark "
        "tradition av sunda statsfinanser, och det ramverket har tjänat "
        "oss väl.\n\n"
        "Under 2023 steg inflationen till nivåer vi inte sett sedan "
        "1990-talet. Riksbanken tvingades höja styrräntan i snabb takt, "
        "vilket drabbade hushåll med rörliga bolån hårt. Samtidigt har "
        "produktivitetstillväxten stagnerat sedan 2015, vilket oroar. "
        "OECD har i flera rapporter pekat på behovet av strukturreformer "
        "i Sverige, särskilt på arbetsmarknaden och bostadsmarknaden.\n\n"
        "I detta läge anser Moderaterna att det krävs en ansvarsfull "
        "ekonomisk politik som prioriterar tillväxt. Skatterna på arbete "
        "och företagande måste sänkas för att stärka incitamenten att "
        "arbeta och investera i Sverige. Jobbskatteavdraget bör utökas "
        "ytterligare och företagens administrativa börda minskas.\n\n"
        "Samtidigt måste offentliga utgifter prioriteras hårdare. Varje "
        "skattekrona ska användas så effektivt som möjligt. Överflödiga "
        "myndigheter bör avvecklas och byråkratin minskas. Statsbudgeten "
        "ska balanseras över en konjunkturcykel i enlighet med det "
        "finanspolitiska ramverket.\n\n"
        "Den gröna omställningen skapar också nya ekonomiska möjligheter. "
        "Sverige har unika förutsättningar inom fossilfri stålproduktion, "
        "batteriproduktion och vindkraft. Dessa industrier behöver "
        "stabila och förutsägbara villkor, inte ständigt ändrade regler "
        "och skatter. Investeringsklimatets förbättring är avgörande för "
        "att Sverige ska kunna konkurrera internationellt om de gröna "
        "investeringarna.\n\n"
        "Vi noterar att internationella bedömare, inklusive IMF och "
        "EU-kommissionen, har rekommenderat Sverige att genomföra "
        "strukturreformer för att höja den potentiella tillväxten. "
        "Moderaterna delar denna analys och anser att reformtakten "
        "måste öka."
    ),
    "expected_claims": [
        {
            "subject": "Moderaterna",
            "topic": "skatt",
            "stance": "oppose",
            "evidence": "Skatterna på arbete och företagande måste sänkas för att stärka incitamenten",
            "confidence_min": 0.8,
        },
        {
            "subject": "Moderaterna",
            "topic": "offentliga utgifter",
            "stance": "oppose",
            "evidence": "Överflödiga myndigheter bör avvecklas och byråkratin minskas",
            "confidence_min": 0.7,
        },
    ],
}
