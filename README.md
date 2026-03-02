# Telegram Dashboard

Overvåkningsdashbord for Telegram-kanaler og GDELT-hendelser med interaktivt kart.

## Funksjoner
- Kart (OpenStreetMap) med hendelser fra Telegram og GDELT
- Automatisk geokoding via NLP (spaCy + Nominatim)
- Manuell registrering av hendelser med koordinater
- Administrasjon av Telegram-kanaler
- Periodisk GDELT-oppdatering

## Lokal utvikling

Se `docs/setup.md` for full oppsettsinstruks.

### Hurtigstart

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm
cp .env.example .env   # fyll inn verdier
uvicorn app.main:app --reload

# Frontend (nytt terminalvindu)
cd frontend
npm install
npm run dev
```

Åpne http://localhost:5173
