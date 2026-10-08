# Setup

Do this once, before starting Phase 00.

## Tooling

| Tool | Purpose | Install |
|---|---|---|
| Burp Suite or Caido | Proxy/repeater (you already have one) | - |
| Bruno | Building/collection-managing API requests, importing OpenAPI specs | https://www.usebruno.com/downloads |
| `jwt_tool` | JWT attack automation (alg confusion, kid injection, etc) | `pip install jwt_tool` or `git clone https://github.com/ticarpi/jwt_tool` |
| `ffuf` or `kiterunner` | Endpoint/route discovery, especially for undocumented API surface | already on Kali / `go install` |
| Docker + Docker Compose | Running the lab targets below | `apt install docker.io docker-compose-plugin` |

(The full course adds a few more tools - `grpcurl`, a GraphQL scanner - with the phases that
need them. The REST track needs only the above.)

## Lab environment

Each vulnerable app is its own project with its own compose file - they're not merged into one
stack. Bring each one up when you reach the phase that uses it (no need to run all of them at
once).

> **`docker compose` vs `docker-compose`:** there are two interchangeable front-ends for
> Compose - the v2 plugin (`docker compose`, a space) and the standalone binary
> (`docker-compose`, a hyphen). Depending on how Docker was installed you may have one or the
> other, not both. The commands below use whichever reads most naturally; if yours errors with
> `'compose' is not a docker command` or `docker-compose: command not found`, just swap to the
> other form - the arguments are identical. (`apt install docker-compose-plugin` adds the
> plugin form; `apt install docker-compose` or `pip install docker-compose` adds the standalone
> form.)

### crAPI (Phase 02 - REST)
```bash
curl -L -o crapi.zip https://github.com/OWASP/crAPI/archive/refs/heads/main.zip
unzip crapi.zip && cd crAPI-main/deploy/docker
docker compose pull
docker compose -f docker-compose.yml --compatibility up -d
```
Web UI on `localhost:8888` by default. It's a full microservice stack (Postgres/Mongo/Kafka) -
give it a couple of minutes to settle after `up -d`.

### vAPI (Phase 02 - supplementary REST)
```bash
git clone https://github.com/roottusk/vapi.git && cd vapi
docker-compose up -d
```
PHP/Laravel + MySQL. Ten modules, each its own OWASP API Top 10 (2019) scenario - good for
isolated single-issue practice alongside crAPI's more realistic combined app.

### VAmPI (Phase 02 - supplementary REST)
```bash
docker run -d -e vulnerable=1 -e tokentimetolive=300 -p 5000:5000 erev0s/vampi:latest
```
Or `docker-compose up -d` from a clone of `erev0s/VAmPI` for two instances side by side (secure
on `:5001`, vulnerable on `:5002`) - useful for diffing scanner output between them. Swagger UI
at `/ui/`.

### DVRA - Damn Vulnerable RESTaurant (Phase 02 - supplementary REST, chain practice)
```bash
git clone https://github.com/theowni/Damn-Vulnerable-RESTaurant-API-Game.git
cd Damn-Vulnerable-RESTaurant-API-Game
./start_app.sh
```
API on `localhost:8091` (`/docs` for Swagger, `/redoc` for Redoc). Single connected
privilege-escalation chain (low-priv user to root) rather than independent per-endpoint bugs -
good stretch practice once the OWASP Top 10 categories feel routine individually. `./stop_app.sh`
to tear down; data persists between stops/starts.

### Other supplementary REST targets (optional)
`payatu/Tiredful-API` and `vulnerable-apps/vulnerable-rest-api` are real but lower-priority
additions - see `setup/EXTERNAL-LABS.md` for what each adds and why they're optional rather
than required.

### api-custom-lab (Phase 02 - the custom REST sections)
```bash
cd custom-labs/api-custom-lab
docker compose up --build      # or: docker-compose up --build
```
Three containers: `main-app` on `localhost:5000` (lab index at `/`, three REST sections -
BOLA, BFLA, unsafe-consumption), `partner-api` on `localhost:5001` (supporting service for the
unsafe-consumption section), and `internal-service` (deliberately not published to the host -
only reachable from inside the compose network). See `custom-labs/api-custom-lab/README.md` for
the exact path per section.

## Access you'll need

Everything (deep-dive reference material, tooling notes, the custom lab) is in this repo
already - no other repo access needed. The public labs above are pulled from their official
sources with the commands shown.
