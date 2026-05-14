# Backgammon AI Server — Deployment

This server runs **gnubg** (via [bgweb-api](https://github.com/foochu/bgweb-api))
to provide expert-level move analysis for the iOS app's training mode.

## Architecture

```
iOS app (training mode)
    ↓ HTTPS
Fly.io edge → Caddy (CORS) → bgweb-api (gnubg engine)
```

- **Caddy**: handles CORS headers and HTTPS termination
- **bgweb-api**: Go reimplementation of gnubg, exposes `/api/v1/getmoves`
- **Fly.io**: hosting (free tier covers low-traffic apps)

## Deploy to Fly.io (free tier)

### 1. Install Fly CLI

```bash
# macOS
brew install flyctl

# or via curl
curl -L https://fly.io/install.sh | sh
```

### 2. Sign up and authenticate

```bash
fly auth signup   # if you don't have an account
fly auth login
```

### 3. Launch the app

```bash
cd backgammon-game/server

# First time: pick a unique app name (the default in fly.toml is 'backgammon-ai'
# but it may already be taken — fly will prompt you for a new name)
fly launch --copy-config --no-deploy
# When prompted:
#  - "Choose a unique app name": pick something like 'yourname-bg-ai'
#  - "Select a region": pick closest to your users (default 'iad' = Virginia)
#  - "Would you like to deploy now?": NO
#  - "Set up Postgres/Redis": NO

# This updates fly.toml with your app name. Now deploy:
fly deploy
```

The first deploy takes 3-5 minutes (downloads bgweb-api Docker image, builds Caddy layer).

### 4. Get your app URL

```bash
fly status
# Hostname will be: https://<your-app-name>.fly.dev
```

Test it:
```bash
curl -X POST https://<your-app-name>.fly.dev/api/v1/getmoves \
  -H "Content-Type: application/json" \
  -d '{"board":{"x":{"6":5,"8":3,"13":5,"24":2},"o":{"6":5,"8":3,"13":5,"24":2}},
       "dice":[3,1],"player":"x","max-moves":3,"score-moves":true}'
```

You should get back a JSON array of analyzed moves with equity values.

### 5. Add the URL to the iOS app

Open `www/index.html` and find the line:
```js
const ANALYSIS_SERVER_URL='';
```

Replace with your Fly.io URL:
```js
const ANALYSIS_SERVER_URL='https://<your-app-name>.fly.dev';
```

Then sync to iOS:
```bash
cd .. && npx cap sync ios
```

## Cost expectations

- **Free tier**: 3 shared VMs at 256MB each — plenty for testing/launch
- The `auto_stop_machines = true` setting in fly.toml pauses the VM when idle (saves money)
- Once you grow past the free tier, expect $5-15/month at modest usage
- Each request takes ~200-800ms of CPU time

## Local testing (optional)

If you have Docker installed:
```bash
cd server
docker build -t bg-ai .
docker run -p 8080:8080 bg-ai
# Test: curl http://localhost:8080/health
```

If you don't have Docker, just deploy to Fly.io directly — it builds remotely.

## Monitoring

```bash
fly logs            # tail server logs
fly status          # health and metrics
fly machine list    # see running VMs
fly scale count 1   # always-on (no auto-stop)
fly scale count 0   # turn off (saves money in dev)
```

## Troubleshooting

**App fails to start**: Check `fly logs` for errors. Common issues:
- Port mismatch (must be 8080)
- Memory too low (bump `memory_mb` in fly.toml to 1024)

**CORS errors in browser**: Caddy should handle this. If you see CORS errors:
- Check that requests go to your Fly.io URL (not http)
- Check that the `Access-Control-Allow-Origin` header is in the response

**iOS app can't reach server**: Check that:
- The URL in `ANALYSIS_SERVER_URL` is correct (with `https://`, no trailing slash)
- The app is running (`fly status`)
- iOS has internet access

## Updating the server

Just `fly deploy` again from the `server/` folder. Zero downtime.

## License notes

- bgweb-api code: MIT
- Embedded gnubg data files (neural net weights, bearoff DB, MET): GPL-3.0
- This server uses GPL software internally — that's allowed under GPL because
  GPL applies to *distribution*, not network use ("ASP loophole")
- Your iOS app does NOT bundle any GPL code, only makes HTTPS calls to your server
- You don't need to open-source anything to use this setup
- Standard practice — same as how Google/AWS/etc. use Linux/MySQL/etc. on servers
