# SRD - System Requirements & Architecture

Referensdokument: [MVP1.md](../product/MVP1.md)

## 1. Övergripande Arkitektur
Systemet är uppbyggt som en datamotor för politisk analys med fokus på transparens och evidens.

### Komponenter
- **Ingestion Layer**: Python-baserade workers för att hämta data från Riksdagens API och partiers webbplatser.
- **Storage Layer**: PostgreSQL med `pgvector` för strukturerad data och embeddings. S3 för rådokument (PDF/HTML).
- **Processing Pipeline**: NLP-pipeline för textextraktion, chunking, embedding och claim-extraktion.
- **API Layer**: FastAPI för att servera entiteter, claims, voteringar och jämförelser.

## 2. Datamodell (High-Level)
- **Entities**: Partier och politiker.
- **Documents & Chunks**: Källdokument med tillhörande textsegment och vektorer.
- **Topics**: Kategorisering av politiska sakfrågor.
- **Claims & Evidence**: Extraherade ståndpunkter kopplade till specifika textsegment (evidens).
- **Votes**: Faktiska röstningsresultat från Riksdagen.

## 3. Teknisk Stack
- **Språk**: Python 3.11+
- **Databas**: PostgreSQL (Linode, Docker) + pgvector
- **Migrationer**: Alembic (SQLAlchemy)
- **AI/NLP**: OpenAI (text-embedding-3-small, 1536 dim), Gemini 2.5 Flash för extraktion/classification.
- **API**: FastAPI
- **Storage**: Lokal disk / S3-kompatibel (bestäms vid deploy)
- **Observabilitet**: structlog + Prometheus metrics
