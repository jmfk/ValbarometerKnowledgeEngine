TEST_CASE = {
    "id": "case_17",
    "name": "Flera aktörer i samma text",
    "description": "Text som beskriver flera partiers ståndpunkter samtidigt",
    "document_type": "anförande",
    "text": (
        "Anf. 156 Talmannen:\n\n"
        "Under dagens debatt om EU:s migrationspakt framkom tydliga "
        "skiljelinjer. Socialdemokraterna meddelade genom sin talesperson "
        "att de stödjer pakten i sin helhet och ser den som ett nödvändigt "
        "steg mot en gemensam europeisk migrationspolitik. "
        "Sverigedemokraterna å sin sida avvisade pakten kategoriskt och "
        "menade att den inte går tillräckligt långt och att Sverige bör "
        "ha full nationell kontroll över sin migrationspolitik. "
        "Vänsterpartiet kritiserade pakten från motsatt håll – de anser "
        "att den är för restriktiv och kränker asylrätten. Moderaterna "
        "uttryckte ett villkorat stöd och betonade att implementeringen "
        "måste ske på ett sätt som respekterar svensk suveränitet."
    ),
    "expected_claims": [
        {
            "subject": "Socialdemokraterna",
            "topic": "EU:s migrationspakt",
            "stance": "support",
            "evidence": "stödjer pakten i sin helhet",
            "confidence_min": 0.8,
        },
        {
            "subject": "Sverigedemokraterna",
            "topic": "EU:s migrationspakt",
            "stance": "oppose",
            "evidence": "avvisade pakten kategoriskt",
            "confidence_min": 0.85,
        },
        {
            "subject": "Vänsterpartiet",
            "topic": "EU:s migrationspakt",
            "stance": "oppose",
            "evidence": "den är för restriktiv och kränker asylrätten",
            "confidence_min": 0.8,
        },
        {
            "subject": "Moderaterna",
            "topic": "EU:s migrationspakt",
            "stance": "mixed",
            "evidence": "villkorat stöd och betonade att implementeringen måste ske på ett sätt som respekterar svensk suveränitet",
            "confidence_min": 0.7,
        },
    ],
}
