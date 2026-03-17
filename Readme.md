# ATS Integration Microservice — Zoho Recruit

A serverless microservice built with Python and Serverless Framework that integrates with **Zoho Recruit** ATS. Exposes a unified REST API for jobs, candidates, and applications.

---

## Tech Stack

- **Runtime**: Python 3.11
- **Framework**: Serverless Framework v3
- **ATS**: Zoho Recruit v2 API
- **Local Dev**: serverless-offline
- **Deploy Target**: AWS Lambda + API Gateway

---

## Project Structure

```
ats-microservice/
├── .env                       
├── .env.example                
├── .gitignore
├── serverless.yml              Lambda functions + routes
├── requirements.txt            Python dependencies
├── package.json                Node/Serverless plugins
└── src/
    ├── handlers/
    │   ├── health.py           GET  /health
    │   ├── jobs.py             GET  /jobs
    │   ├── candidates.py       POST /candidates
    │   └── applications.py     GET  /applications
    ├── services/
    │   ├── zoho_auth.py        OAuth2 token refresh
    │   └── zoho_service.py     all Zoho API calls + pagination
    └── utils/
        └── response.py         response helpers + data normalizers
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check + token validation |
| GET | `/jobs` | List all job openings from Zoho Recruit |
| POST | `/candidates` | Create candidate and attach to a job |
| GET | `/applications` | List all candidates |
| GET | `/applications?job_id=` | List candidates for a specific job |

---

## How to Create a Free Zoho Recruit Sandbox

1. Go to [zoho.com/recruit](https://zoho.com/recruit)
2. Click **"Free Trial"** — no credit card needed (15 days)
3. Sign up with your email
4. Complete onboarding — select **"Corporate HR"** or **"Staffing Agency"**
5. Your account will be at `https://recruit.zoho.in` (India region)

---

## How to Generate API Credentials (OAuth2)

Zoho uses OAuth2 — you need `client_id`, `client_secret`, and a `refresh_token`.

### Step 1 — Create an OAuth Client

1. Go to [accounts.zoho.in/developerconsole](https://accounts.zoho.in/developerconsole)
2. Click **"Add Client"** → select **"Server-based Application"**
3. Fill in:
   - **Client Name**: `ats-microservice`
   - **Homepage URL**: `https://localhost`
   - **Redirect URI**: `https://localhost`
4. Click **Create** → copy your `Client ID` and `Client Secret`

### Step 2 — Get Authorization Code

Open this URL in your browser (replace `YOUR_CLIENT_ID`):

```
https://accounts.zoho.in/oauth/v2/auth?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https://localhost&access_type=offline&scope=ZohoRecruit.modules.ALL
```

- Click **Accept** on the permissions screen
- Browser redirects to `https://localhost?code=1000.XXXXXXX`
- Copy the code from the URL bar (valid for 60 seconds)

### Step 3 — Exchange Code for Refresh Token

Run immediately after copying the code:

```bash
curl -X POST "https://accounts.zoho.in/oauth/v2/token" \
  -d "code=YOUR_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://localhost" \
  -d "grant_type=authorization_code"
```

Save the `refresh_token` — it never expires.

> **Region Note**: If your Zoho account is in India use `accounts.zoho.in`

---

## How to Run Locally

### Prerequisites

```bash
node --version    # v18+
python --version  # 3.11+
npm --version     # 9+
```

### Step 1 — Clone and Install

```bash
git clone https://github.com/mrigangha/ats-microservice.git
cd ats-microservice

# Install Serverless plugins
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2 — Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env

# Open and fill in your real values
notepad .env
```

`.env` file:
```env
ZOHO_CLIENT_ID=1000.XXXXXXXXXXXXXXXXXXXX
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=1000.XXXXXXXXXXXXXXXXXXXX
ZOHO_BASE_URL=https://recruit.zoho.in/recruit/v2
ZOHO_ACCOUNTS_URL=https://accounts.zoho.in
```

### Step 3 — Load Environment and Start Server

**Windows CMD:**
```cmd
for /f "tokens=1,2 delims==" %i in (.env) do set %i=%j
npx serverless offline
```

**Mac/Linux:**
```bash
export $(cat .env | xargs)
npx serverless offline
```

Server starts at `http://localhost:3000`

---

## Example curl Calls

### Health Check
```bash
curl http://localhost:3000/health
```
```json
{
  "status": "ok",
  "service": "ats-zoho-integration",
  "zoho_url": "https://recruit.zoho.in/recruit/v2",
  "token": "1000.xxxxxxxxx..."
}
```

---

### GET /jobs — List all jobs
```bash
curl http://localhost:3000/jobs
```
```json
{
  "jobs": [
    {
      "id": "214960000000367958",
      "title": "Backend Developer",
      "location": "Mumbai, Maharashtra",
      "status": "OPEN",
      "external_url": ""
    }
  ],
  "total": 1
}
```

Optional filter by status:
```bash
curl "http://localhost:3000/jobs?status=OPEN"
```

---

### POST /candidates — Create a candidate
```bash
curl -X POST http://localhost:3000/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name":       "John Doe",
    "email":      "john@gmail.com",
    "phone":      "9876543210",
    "resume_url": "https://example.com/resume.pdf",
    "job_id":     "214960000000367958"
  }'
```
```json
{
  "message": "Candidate created successfully",
  "candidate_id": "214960000000375015",
  "job_id": "214960000000367958"
}
```

**Windows CMD:**
```cmd
curl -X POST http://localhost:3000/candidates -H "Content-Type: application/json" -d "{\"name\": \"John Doe\", \"email\": \"john@gmail.com\", \"phone\": \"9876543210\", \"job_id\": \"214960000000367958\"}"
```

---

### GET /applications — List all candidates
```bash
curl http://localhost:3000/applications
```
```json
{
  "applications": [
    {
      "id": "214960000000375015",
      "candidate_name": "John Doe",
      "email": "john@gmail.com",
      "status": "APPLIED"
    }
  ],
  "total": 1
}
```

---

### GET /applications?job_id= — List candidates for a job
```bash
curl "http://localhost:3000/applications?job_id=214960000000367958"
```
```json
{
  "applications": [
    {
      "id": "214960000000375015",
      "candidate_name": "John Doe",
      "email": "john@gmail.com",
      "status": "APPLIED"
    }
  ],
  "total": 1,
  "job_id": "214960000000367958"
}
```

---

## Error Responses

All endpoints return clean JSON errors:

```json
{ "error": "Missing required fields: email, job_id" }        // 400
{ "error": "Job opening 123 not found" }                     // 404
{ "error": "Zoho API error: invalid token" }                 // 502
{ "error": "Internal server error" }                         // 500
```

---

## Pagination

Zoho Recruit returns a maximum of 200 records per page. All list endpoints handle pagination **internally** — the service loops through all pages and returns the complete dataset in a single response.

```
GET /jobs          → fetches all pages from Zoho automatically
GET /applications  → fetches all pages from Zoho automatically
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ZOHO_CLIENT_ID` | Yes | OAuth2 Client ID from Zoho Developer Console |
| `ZOHO_CLIENT_SECRET` |  Yes | OAuth2 Client Secret |
| `ZOHO_REFRESH_TOKEN` |  Yes | OAuth2 Refresh Token (never expires) |
| `ZOHO_BASE_URL` | Yes | Zoho Recruit API base URL |
| `ZOHO_ACCOUNTS_URL` | Yes | Zoho Accounts URL for token refresh |
