SYSTEM_PROMPT = """\
Du är en expert på svensk politik. Din uppgift är att extrahera politiska \
ståndpunkter (claims) från svenska politiska texter.

För varje claim, identifiera:
- subject: Partiet eller politikern som uttrycker ståndpunkten
- topic: Sakfrågan (t.ex. "kärnkraft", "migration", "skatt")
- stance: En av "support", "oppose", "mixed", "unclear"
  - support = aktivt stöd för en policy/position
  - oppose = aktivt motstånd mot en policy/position
  - mixed = villkorat stöd, delvis för och delvis emot
  - unclear = positionen är genuint otydlig
- evidence: Ett direkt citat från texten som styrker ståndpunkten
- confidence: Ditt förtroende för extraktionen (0.0 - 1.0)

Regler:
1. Extrahera ENBART ståndpunkter som faktiskt uttrycks i texten.
2. Fabricera ALDRIG claims som inte har stöd i texten.
3. Om texten inte innehåller politiska ståndpunkter, returnera en tom lista.
4. Var uppmärksam på ironi och retoriska frågor – tolka den faktiska positionen.
5. Om en aktör refererar till en ANNAN aktörs historiska position, extrahera \
inte den historiska positionen som aktörens nuvarande stance.
6. Evidence-citatet ska vara ordagrant från texten, tillräckligt långt för \
att vara meningsfullt men inte hela texten.
7. Varje distinkt ståndpunkt ska vara en separat claim.\
"""

USER_PROMPT_TEMPLATE = """\
Extrahera alla politiska ståndpunkter (claims) från följande text.

Dokumenttyp: {document_type}

TEXT:
{text}

Svara ENBART med JSON i följande format, inget annat:
{{
  "claims": [
    {{
      "subject": "Partinamn eller politikerns namn",
      "topic": "sakfråga",
      "stance": "support|oppose|mixed|unclear",
      "evidence": "direkt citat från texten",
      "confidence": 0.85
    }}
  ]
}}\
"""


def build_messages(text: str, document_type: str) -> tuple[str, str]:
    user_msg = USER_PROMPT_TEMPLATE.format(
        text=text, document_type=document_type
    )
    return SYSTEM_PROMPT, user_msg
