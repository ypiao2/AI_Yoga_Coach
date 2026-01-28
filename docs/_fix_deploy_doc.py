# One-off script to fix DEPLOY_AI_BUILDERS.md Important paragraph and 2.1 block
path = '/Users/ellen/Desktop/AI/AI Personal Yoga Coach/docs/DEPLOY_AI_BUILDERS.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Unicode curly quotes as in file
replacement_important = (
    'The script defaults to **`https://ai-yoga-coach.ai-builders.space`** '
    'as the deployment API base. Override `DEPLOY_BASE_URL` only if your '
    'instructor or dashboard gives you a different API host.'
)
old_important = (
    '**Important:** The URL **`https://ai-builders.space/backend/v1/deployments`** '
    'returns a 404 \u201cpage not found\u201d (that host serves Superlinear Academy, '
    'not the deploy API). You **must** get the **exact deployment API base URL** '
    'from your instructor or from the \u201cDashboard & API\u201d / deployment dashboard. '
    'Then set `DEPLOY_BASE_URL` to that host (e.g. `https://api.example.com`) '
    'so the script POSTs to `$DEPLOY_BASE_URL/backend/v1/deployments`.'
)
if old_important in content:
    content = content.replace(old_important, replacement_important)
    print('Replaced Important paragraph')
else:
    print('Important paragraph not found')
    # show what we have
    for i, line in enumerate(content.split('\n')):
        if 'Important' in line and '404' in line:
            print('Line', i+1, ':', repr(line[:150]))
            break

# 2.1 block replacement
old_21 = """Run from Cursor or any terminal. **You must set DEPLOY_BASE_URL to the exact API host from your instructor** — `https://ai-builders.space/backend/v1/deployments` returns 404 (Superlinear Academy 404 page).

```bash
export DEPLOY_BASE_URL="https://YOUR-DEPLOYMENT-API-HOST"   # from instructor/dashboard
export AI_BUILDER_TOKEN="YOUR_DEPLOYMENT_API_KEY"
curl -X POST "${DEPLOY_BASE_URL}/backend/v1/deployments" \\
  -H "Authorization: Bearer $AI_BUILDER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"repo_url":"https://github.com/ypiao2/AI_Yoga_Coach","service_name":"ai-yoga-coach","branch":"main","port":8000}'
```

**Or run the script (requires DEPLOY_BASE_URL from your instructor):**

```bash
export DEPLOY_BASE_URL="https://YOUR-DEPLOYMENT-API-HOST"
export AI_BUILDER_TOKEN="your-deployment-api-key"
chmod +x scripts/deploy_ai_builders.sh
./scripts/deploy_ai_builders.sh
```

**If you see \u201c301 Moved Permanently\u201d and deploy still fails:** The script now follows redirects and keeps POST. If it still doesn't work, get the **exact** deployment API base URL from your instructor or the deployment dashboard. If you see 404 or "page not found" HTML, the URL you used is wrong (it may use `www`, a different path, or another host).

### 2.2 One-shot curl (generic placeholders)

```bash
export DEPLOY_BASE_URL="https://YOUR-DEPLOYMENT-API-HOST"   # from instructor
export AI_BUILDER_TOKEN="your-key"
curl -X POST "${DEPLOY_BASE_URL}/backend/v1/deployments" \\
  -H "Authorization: Bearer $AI_BUILDER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"repo_url":"https://github.com/ypiao2/AI_Yoga_Coach","service_name":"ai-yoga-coach","branch":"main","port":8000}'
```

Replace `YOUR-DEPLOYMENT-API-HOST` with the exact host from your instructor or dashboard. Do not use `ai-builders.space` — that returns 404 for this path.

If the base URL is different, use the exact URL from your \u201cDashboard & API instructions\u201d.

### 2.2 Using an env var for the key (safer)"""

new_21 = """**Run the script (default base URL = ai-yoga-coach):**

```bash
export AI_BUILDER_TOKEN="your-deployment-api-key"
chmod +x scripts/deploy_ai_builders.sh
./scripts/deploy_ai_builders.sh
```

The script uses `https://ai-yoga-coach.ai-builders.space` by default. To use a different API host: `export DEPLOY_BASE_URL="https://that-host"` before running.

**One-shot curl (same default base URL):**

```bash
export AI_BUILDER_TOKEN="YOUR_DEPLOYMENT_API_KEY"
curl -X POST "https://ai-yoga-coach.ai-builders.space/backend/v1/deployments" \\
  -H "Authorization: Bearer $AI_BUILDER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"repo_url":"https://github.com/ypiao2/AI_Yoga_Coach","service_name":"ai-yoga-coach","branch":"main","port":8000}'
```

**If you see "301 Moved Permanently" or 404:** The script follows redirects. If it still fails, confirm the API base URL with your instructor (override with `DEPLOY_BASE_URL` if they give you a different host).

### 2.2 Overriding the base URL

If your instructor or dashboard gives you a different deployment API host:

```bash
export DEPLOY_BASE_URL="https://that-host"
export AI_BUILDER_TOKEN="your-key"
./scripts/deploy_ai_builders.sh
```

### 2.3 Using an env var for the key (safer)"""

if old_21 in content:
    content = content.replace(old_21, new_21)
    print('Replaced 2.1 block')
else:
    print('2.1 block not found')
    idx = content.find('Run from Cursor or any terminal')
    if idx >= 0:
        snippet = content[idx:idx+400]
        print('Snippet:', repr(snippet))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done.')
