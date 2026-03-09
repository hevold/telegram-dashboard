# Telegram Dashboard

Overvåkningsdashbord for Telegram-kanaler og GDELT-hendelser med interaktivt kart.

## Funksjoner
- Kart (OpenStreetMap) med hendelser fra Telegram og GDELT
- Automatisk geokoding via NLP (spaCy + Nominatim)
- Manuell registrering av hendelser med koordinater
- Administrasjon av Telegram-kanaler
- Periodisk GDELT-oppdatering
- IP-basert hviteliste for tilgangskontroll

## Lokal utvikling

### Krav
- Python 3.10 eller nyere
- Node.js 18 eller nyere
- Telegram API-nøkler (hentes fra https://my.telegram.org)

### Oppsett

#### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm
cp .env.example .env              # Rediger .env med dine verdier
uvicorn app.main:app --reload
```

Backend kjører på http://localhost:8000

#### 2. Frontend

```bash
# Åpne et nytt terminalvindu
cd frontend
npm install
npm run dev
```

Frontend kjører på http://localhost:5173 – åpne denne adressen i nettleseren.

### Miljøvariabler (backend/.env)

| Variabel | Beskrivelse | Standardverdi |
|---|---|---|
| `DATABASE_URL` | Databasetilkobling | `sqlite+aiosqlite:///./dashboard.db` |
| `TELEGRAM_API_ID` | Telegram API-ID | – |
| `TELEGRAM_API_HASH` | Telegram API-hash | – |
| `TELEGRAM_PHONE` | Telefonnummer (med landkode) | – |
| `GDELT_FETCH_INTERVAL_MINUTES` | Hentingsintervall for GDELT | `15` |
| `ALLOWED_IPS` | IP-hviteliste (se nedenfor) | *(tom – alle tillatt)* |
| `TRUST_FORWARDED_FOR` | Stol på X-Forwarded-For (se nedenfor) | `false` |

---

## IP-hviteliste

For å begrense tilgang til dashbordet kan du hviteliste bestemte IP-adresser
eller subnett via miljøvariabelen `ALLOWED_IPS` i `backend/.env`.

### Format

`ALLOWED_IPS` er en kommaseparert liste med én eller flere av disse:
- **Enkelt IP-adresse:** `192.168.1.10`
- **CIDR-subnett:** `10.0.0.0/8`, `192.168.1.0/24`
- **Blanding:** `192.168.1.10,10.0.0.0/8,172.16.0.5`

Hvis variabelen er tom (standardverdien), tillates alle IP-adresser.

### Eksempler

```env
# Tillat bare én spesifikk maskin
ALLOWED_IPS=192.168.1.42

# Tillat hele det private nettverket og én ekstern adresse
ALLOWED_IPS=192.168.0.0/16,203.0.113.55

# Tillat localhost (IPv4 og IPv6)
ALLOWED_IPS=127.0.0.1,::1
```

Forespørsler fra IP-adresser som ikke er på hvitelisten avvises med HTTP **403 Forbudt**.

### Bak en omvendt proxy (Nginx, Traefik, o.l.)

Hvis backend kjøres bak en proxy som setter `X-Forwarded-For`-headeren,
kan du aktivere `TRUST_FORWARDED_FOR=true` slik at klient-IP-en leses fra
den headeren. **Aktiver ikke dette uten en proxy** – uten proxy kan en
angriper sette headeren selv og omgå hvitelisten.

Eksempel på Nginx-konfigurasjon:

```nginx
proxy_set_header X-Forwarded-For $remote_addr;
```

