# Step 5: API & Comparison Engine

Referens: [MVP1.md](../MVP1.md) (API & Comparisons)

## Mål
Exponera kunskapsbasen via ett API för att möjliggöra jämförelser och analys.

## Funktionella krav
1. **Search**: Hybrid sökning (text + vektor) efter claims.
2. **Compare**: Sammanställa ståndpunkter vs röstningsbeteende för ett ämne.
3. **Evidence Cards**: Returnera kompletta objekt med påstående, citat och källa.

## Tekniska steg
- Bygga FastAPI-endpoints enligt specifikation i PRD.
- Implementera logik för att aggregera `claims` och `vote_positions`.
- Skapa filter för ämnen (topics) och entiteter (partier/politiker).
