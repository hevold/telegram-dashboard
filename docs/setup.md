# Oppsettsveiledning – Telegram Dashboard

Denne veiledningen dekker alt du trenger for å sette opp og kjøre Telegram Dashboard lokalt.

---

## Forutsetninger

| Verktøy | Minimum versjon | Sjekk |
|---------|----------------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.x | `git --version` |

---

## 1. Hent kildekoden

```bash
git clone https://github.com/hevold/telegram-dashboard.git
cd telegram-dashboard
```

---

## 2. Backend-oppsett

### 2.1 Opprett virtuelt miljø og installer avhengigheter

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2.2 Last ned spaCy-språkmodeller

Applikasjonen bruker to spaCy-modeller for navngitt entitetsgjenkjenning (NER):

```bash
python -m spacy download en_core_web_sm   # Engelsk NER
python -m spacy download xx_ent_wiki_sm   # Flerspråklig NER
```

### 2.3 Konfigurer miljøvariabler

```bash
cp .env.example .env
```

Åpne `.env` og fyll inn verdiene:

```dotenv
# Database – SQLite er standard for lokal utvikling, ingen ekstra oppsett nødvendig
DATABASE_URL=sqlite+aiosqlite:///./dashboard.db

# Telegram API-legitimasjon (se avsnitt 4 nedenfor)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=din_api_hash_her
TELEGRAM_PHONE=+4712345678

# Hvor ofte GDELT-hendelser hentes (minutter)
GDELT_FETCH_INTERVAL_MINUTES=15
```

> **Merk:** `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` og `TELEGRAM_PHONE` er bare påkrevd hvis du vil bruke Telegram-integrasjonen. Appen starter fint uten disse – GDELT-funksjonen og manuell hendelsesregistrering vil fungere normalt.

### 2.4 Start backend-serveren

```bash
uvicorn app.main:app --reload
```

API-et er tilgjengelig på **http://localhost:8000**.  
Interaktiv dokumentasjon: **http://localhost:8000/docs**

---

## 3. Frontend-oppsett

Åpne et nytt terminalvindu:

```bash
cd frontend
npm install
npm run dev
```

Dashbordet åpnes på **http://localhost:5173**.

Vite er konfigurert til å videresende `/api`-forespørsler til `http://localhost:8000`, så backend og frontend trenger ikke noen ekstra CORS-konfigurasjon under utvikling.

---

## 4. Skaff Telegram API-legitimasjon

For å overvåke Telegram-kanaler trenger du egne API-nøkler:

1. Gå til **https://my.telegram.org** og logg inn med telefonnummeret ditt.
2. Velg **API development tools**.
3. Fyll ut skjemaet (appnavn og plattform kan være hva som helst, f.eks. «Dashboard» / «Desktop»).
4. Kopier **App api_id** og **App api_hash** til `.env`-filen.
5. Sett `TELEGRAM_PHONE` til telefonnummeret ditt i internasjonalt format (f.eks. `+4712345678`).

Første gang du starter backend med gyldige Telegram-nøkler vil Telethon be deg om å bekrefte påloggingen via en kode sendt til Telegram-appen din.

---

## 5. Bruk

### Legge til en Telegram-kanal

1. Åpne **Kanaladministrasjon** i dashbordet.
2. Skriv inn kanalens brukernavn (f.eks. `@eksempelkanal` eller bare `eksempelkanal`).
3. Klikk **Legg til**. Kanalen blir lagt til og historikken hentes automatisk.

### GDELT-hendelser

- Hendelser fra [GDELT 2.0](https://www.gdeltproject.org/) hentes automatisk hvert `GDELT_FETCH_INTERVAL_MINUTES` minutt.
- Du kan også utløse en manuell henting via **Oppdater GDELT**-knappen i dashbordet.

### Manuell hendelsesregistrering

Klikk **+ Ny hendelse** og fyll inn tittel, innhold og koordinater (eller la systemet geokode stedsnavnet automatisk).

---

## 6. Feilsøking

| Problem | Mulig årsak | Løsning |
|---------|-------------|---------|
| `ModuleNotFoundError` ved oppstart | Avhengigheter ikke installert | Kjør `pip install -r requirements.txt` i aktivert virtuelt miljø |
| spaCy-feil: modell ikke funnet | spaCy-modeller mangler | Kjør `python -m spacy download en_core_web_sm` og `python -m spacy download xx_ent_wiki_sm` |
| Telegram-tilkobling feiler | Manglende eller feil API-nøkler | Sjekk `.env`-verdiene og se avsnitt 4 |
| Frontend kan ikke nå API | Backend kjører ikke | Start `uvicorn app.main:app --reload` fra `backend/`-mappen |
| CORS-feil i nettleseren | Feil backend-URL | Sjekk at Vite-proxy peker på `http://localhost:8000` i `vite.config.js` |
| `OSError: [Errno 98] Address already in use` | Port 8000 allerede i bruk | Finn prosessen med `lsof -i :8000` og avslutt den, eller start uvicorn på en annen port med `--port 8001` |
