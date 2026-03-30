---
description: How to release a new version of dados-publicos-api to Azure. No CI/CD — manual deploy required for both the function app and the git repo.
applyTo: "**"
---

# Release Process

This project has **no CI/CD pipeline**. The Azure Function App is not connected to git. Every release requires two independent actions: deploying code to Azure and committing to git.

---

## Pre-release checklist

- [ ] All changes tested locally with `func start` or via `downloader_http` endpoint
- [ ] New indicators registered in `Constants/Indices.py`
- [ ] New modules registered in `downloader_http/__init__.py` (`DOWNLOADER_MAP`)
- [ ] `requirements.txt` updated if new packages were added
- [ ] `README.md` updated with new indicators, endpoints, or env vars

---

## Step 1 — Deploy to Azure

```bash
cd /home/pedro/DEV/dados-publicos-api/AzureFunctions
func azure functionapp publish func-dados-publicos-api --python
```

Verify the output lists all expected functions:
- `api_indices` — [httpTrigger]
- `downloader_http` — [httpTrigger]
- `downloader_fgv` — [timerTrigger]
- `downloader_ibge` — [timerTrigger]
- `downloader_bacen` — [timerTrigger]
- `downloader_anp` — [timerTrigger]
- `downloader_b3` — [timerTrigger]

**If new env vars were added**, set them in Azure before or immediately after deploy:

```bash
az functionapp config appsettings set \
  --name func-dados-publicos-api \
  --resource-group rg-dados-publicos-api \
  --settings DADPUBAPI_NEW_VAR="value"
```

**Smoke test** after deploy:
```bash
# Force-run a downloader and verify success
curl "https://func-dados-publicos-api.azurewebsites.net/api/downloader_http?downloader=bacen&date=$(date +%Y-%m-%d)"

# Check the stored data
curl "https://func-dados-publicos-api.azurewebsites.net/api/indices?nome=cdi"
```

---

## Step 2 — Commit to git

After confirming the Azure deploy is healthy:

```bash
cd /home/pedro/DEV/dados-publicos-api
git add -p                          # stage changes selectively
git status                          # confirm staged files
git commit -m "[type]: description"
git push origin main
```

Commit type convention:
- `[feat]` — new indicator, new endpoint, new downloader
- `[fix]` — bug fix in feeder or downloader
- `[refactor]` — internal restructuring, no behavior change
- `[docs]` — README or instructions only

---

## Azure resources reference

| Resource | Name | Region |
|---|---|---|
| Resource Group | `rg-dados-publicos-api` | Brazil South |
| Function App | `func-dados-publicos-api` | Flex Consumption, Python 3.11 |
| Storage Account | `stdadospublicosapi` | Standard_LRS |
| Table | `IndicesPublicos` | via Table Storage |

```bash
# Login check
az account show

# List current app settings
az functionapp config appsettings list \
  --name func-dados-publicos-api \
  --resource-group rg-dados-publicos-api \
  --output table

# View recent function invocations (last 20)
az monitor app-insights query \
  --app func-dados-publicos-api \
  --resource-group rg-dados-publicos-api \
  --analytics-query "traces | order by timestamp desc | take 20" \
  --output table
```

---

## Rollback

Azure Flex Consumption does not support deployment slots. To rollback:

1. Identify the last working git commit: `git log --oneline -10`
2. Checkout that commit locally: `git checkout <hash> -- AzureFunctions/`
3. Re-deploy: `func azure functionapp publish func-dados-publicos-api --python`
4. Revert the git commit: `git revert HEAD`
