# Advanced DABs Demo — Insurance Claims Risk Scoring Pipeline

A production-grade Databricks Asset Bundle demonstrating a multi-task ML pipeline
with Unity Catalog, environment overrides, permissions, and CI/CD-ready configuration.

---

## Use Case

A daily pipeline for an insurance company that:

1. **Ingests** raw claims data from a landing zone into Unity Catalog (`raw_claims`)
2. **Scores** each claim with an ML-based risk model, writing results to `scored_claims`

Claims are categorized as **HIGH**, **MEDIUM**, or **LOW** risk based on amount,
type, claimant demographics, and prior history.

---

## Prerequisites

### 1. Install the Databricks CLI

```bash
# macOS (Homebrew)
brew tap databricks/tap && brew install databricks

# Linux / WSL
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Verify (requires v0.200+)
databricks --version
```

### 2. Configure authentication

```bash
databricks configure
```

When prompted, enter:
- **Databricks Host**: your workspace URL (e.g. `https://myworkspace.cloud.databricks.com`)
- **Personal Access Token**: generate one at **Settings > Developer > Access tokens** in the Databricks UI

Verify:

```bash
databricks auth profiles    # should show your profile with Valid = YES
databricks current-user me  # should print your username
```

### 3. Python 3.10+

```bash
python3 --version
```

### 4. Unity Catalog access

This demo writes tables to Unity Catalog. You need:
- A catalog you can write to (or permission to create one)
- The default `claims` schema will be created automatically

If you don't have an existing catalog, create one:

```sql
-- Run in a Databricks SQL editor or notebook
CREATE CATALOG IF NOT EXISTS dev_insurance_catalog;
CREATE SCHEMA IF NOT EXISTS dev_insurance_catalog.claims;
```

---

## Getting Started

```bash
git clone https://github.com/wryszka/dabs-demo.git
cd dabs-demo/advanced
```

### Connect to your workspace

Edit `databricks.yml` — update these values:

```yaml
# 1. Set your workspace URL in BOTH targets (dev and prod):
workspace:
  host: https://YOUR-WORKSPACE.cloud.databricks.com

# 2. If you have multiple CLI profiles, uncomment and set:
  # profile: DEFAULT

# 3. Update catalog names to match your Unity Catalog:
variables:
  catalog: dev_insurance_catalog       # <-- your dev catalog
  schema: claims
```

If you have multiple CLI profiles, uncomment the `profile` line and set it to the
profile name shown by `databricks auth profiles`.

---

## Project Structure

```
advanced/
├── databricks.yml                 # Bundle config: variables, dev/prod targets
├── resources/
│   └── insurance_job.yml          # Multi-task workflow + cluster overrides + permissions
├── src/
│   ├── ingest.py                  # Claims ingestion (mock data → Unity Catalog)
│   └── scoring.py                 # Risk scoring model (rule-based mock ML)
└── README.md                      # This file
```

---

## Bundle Configuration Highlights

| Feature | How It's Implemented |
|---------|---------------------|
| **Two targets** | `dev` (single-node, development mode) / `prod` (autoscaling, production mode) |
| **Environment overrides** | Dev: `Standard_DS3_v2`, 0 workers. Prod: `Standard_DS4_v2`, 2–10 autoscaling |
| **Unity Catalog variables** | `${var.catalog}` and `${var.schema}` resolve per target |
| **Task dependencies** | `score_risk` depends on `ingest_claims` — enforced DAG |
| **Permissions** | `claims_auditors` group gets `CAN_VIEW` on the job |
| **Schedule** | Daily at 6 AM UTC (paused automatically in dev mode) |

---

## Demo Script

### Step 1 — Validate (Dev)

```bash
databricks bundle validate -t dev
```

**What it does:** Validates YAML syntax, CLI authentication, variable resolution,
resource references, and cluster configs — without touching the workspace.

**Expected output:** Bundle summary with resolved variables (`dev_insurance_catalog.claims`),
single-node cluster config, ending with `Validation OK!`

**Talk Track:** *"Before anything touches the workspace, `validate` catches
misconfigurations locally. This is your first gate in CI/CD — every PR runs this."*

---

### Step 2 — Validate (Prod)

```bash
databricks bundle validate -t prod
```

**What it does:** Same validation but resolves prod variables and autoscaling cluster config.

**Expected output:** Variables resolve to `prod_insurance_catalog`, clusters show 2–10 workers.

**Talk Track:** *"Same bundle, different target. The config is identical in Git —
environment differences are declared, not ad-hoc. This is environment consistency
for regulatory compliance."*

---

### Step 3 — Deploy to Dev

```bash
databricks bundle deploy -t dev
```

**What it does:** Uploads `src/ingest.py` and `src/scoring.py`, creates the multi-task
job with schedule paused.

**Where to see it in Databricks UI:**

1. Open your workspace in a browser
2. Click **Workflows** in the left sidebar
3. Click the **Jobs** tab
4. Look for **`[dev <your_username>] insurance_claims_risk_scoring`**
5. Click it — you'll see the **two-task DAG**: `ingest_claims` → `score_risk`
6. Click the **Schedule** section — notice it says "Paused" (dev mode auto-pauses)
7. Click **Permissions** — your user is the owner

The uploaded files are at:
**Workspace > Users > `<you>` > `.bundle/insurance_claims_risk_scoring/dev/files/`**

**Talk Track:** *"In dev mode, DABs automatically prefixes your name and pauses
schedules — no risk of dev jobs running against production data."*

---

### Step 4 — Run in Dev

```bash
databricks bundle run -t dev insurance_claims_job
```

**What it does:** Triggers the pipeline. Ingest writes 6 mock claims to
`dev_insurance_catalog.claims.raw_claims`, then scoring reads and writes risk scores
to `dev_insurance_catalog.claims.scored_claims`.

**Where to see it in Databricks UI:**

1. Click the **run URL** printed in your terminal, OR:
2. Go to **Workflows > Jobs > `[dev] insurance_claims_risk_scoring`**
3. Click the **Runs** tab
4. Click the latest run — you'll see the **DAG execution** with both tasks
5. Click **`ingest_claims`** → **Output** tab → see `[INGEST] Successfully wrote claims`
6. Click **`score_risk`** → **Output** tab → see the risk distribution table:
   ```
   +----------+-----+----------------+---------------+
   |risk_label|count|avg_claim_amount|avg_risk_score |
   +----------+-----+----------------+---------------+
   |HIGH      |  2  |     89500.00   |     65.0      |
   |MEDIUM    |  2  |     15700.00   |     41.0      |
   |LOW       |  2  |      7050.00   |     22.0      |
   +----------+-----+----------------+---------------+
   ```
7. **Bonus — check Unity Catalog**: Go to **Catalog > `dev_insurance_catalog` > `claims`**
   and you'll see the `raw_claims` and `scored_claims` tables with lineage

**Talk Track:** *"One command triggers the full pipeline. The dependency graph ensures
scoring never runs before ingestion completes. In Unity Catalog, you can trace the
lineage from landing zone to scored output — that's your audit trail."*

---

### Step 5 — Deploy to Prod

```bash
databricks bundle deploy -t prod
```

**Where to see it in Databricks UI:**

1. Go to **Workflows > Jobs**
2. Look for **`insurance_claims_risk_scoring`** (no `[dev]` prefix in prod)
3. Click it — the DAG is the same, but:
   - **Clusters** tab: shows `Standard_DS4_v2` with autoscale 2–10 workers
   - **Schedule**: Daily at 6 AM UTC — **active** (not paused)
   - **Permissions**: `claims_auditors` group has `CAN_VIEW`

**Talk Track:** *"Same code from Git, no manual config. Autoscaling handles variable
claim volumes, and the auditor group has view-only access for compliance."*

---

### Step 6 — Triggered Run (Prod)

```bash
databricks bundle run -t prod insurance_claims_job
```

**Where to see it in Databricks UI:**

Same as Step 4, but under the prod job. Tables are written to `prod_insurance_catalog`.

---

### Step 7 — Cleanup (single command per target)

```bash
# Remove ALL dev resources:
databricks bundle destroy -t dev --auto-approve

# Remove ALL prod resources:
databricks bundle destroy -t prod --auto-approve
```

**What gets deleted:** The job, all uploaded files, and the `.bundle` workspace folder.

**Verify cleanup in Databricks UI:**

1. Go to **Workflows > Jobs** — both jobs should be gone
2. Go to **Workspace > Users > `<you>`** — `.bundle/insurance_claims_risk_scoring/` folder removed

> **Note:** The Unity Catalog tables (`raw_claims`, `scored_claims`) are NOT deleted
> by `bundle destroy`. To clean those up manually:
> ```sql
> DROP TABLE IF EXISTS dev_insurance_catalog.claims.raw_claims;
> DROP TABLE IF EXISTS dev_insurance_catalog.claims.scored_claims;
> ```

---

## Quick Reference

| Step | Command | Where to Verify in UI |
|------|---------|-----------------------|
| Validate dev | `databricks bundle validate -t dev` | Terminal: `Validation OK!` |
| Validate prod | `databricks bundle validate -t prod` | Terminal: `Validation OK!` |
| Deploy dev | `databricks bundle deploy -t dev` | **Workflows > Jobs > `[dev] insurance_claims_risk_scoring`** |
| Run dev | `databricks bundle run -t dev insurance_claims_job` | **Workflows > Jobs > Runs tab > click run > task outputs** |
| Deploy prod | `databricks bundle deploy -t prod` | **Workflows > Jobs > `insurance_claims_risk_scoring`** (no prefix) |
| Run prod | `databricks bundle run -t prod insurance_claims_job` | **Workflows > Jobs > Runs tab** |
| Cleanup dev | `databricks bundle destroy -t dev --auto-approve` | Job gone from **Workflows > Jobs** |
| Cleanup prod | `databricks bundle destroy -t prod --auto-approve` | Job gone from **Workflows > Jobs** |

---

## Sharing This Demo

Anyone with a Databricks workspace can run this:

1. **Clone the repo:**
   ```bash
   git clone https://github.com/wryszka/dabs-demo.git
   cd dabs-demo/advanced
   ```

2. **Install & configure CLI** (see Prerequisites above)

3. **Edit `databricks.yml`** — set your workspace URL and catalog names:
   ```yaml
   workspace:
     host: https://YOUR-WORKSPACE.cloud.databricks.com
   variables:
     catalog: your_catalog_name
   ```

4. **Create the Unity Catalog schema** (if it doesn't exist):
   ```sql
   CREATE CATALOG IF NOT EXISTS your_catalog_name;
   CREATE SCHEMA IF NOT EXISTS your_catalog_name.claims;
   ```

5. **Run the demo:**
   ```bash
   databricks bundle validate -t dev
   databricks bundle deploy -t dev
   databricks bundle run -t dev insurance_claims_job
   databricks bundle destroy -t dev --auto-approve
   ```

No additional Python packages, wheels, or pip installs required.

---

## Demo Talk Track — Insurance Compliance Value

### Auditability

> *"Every resource — jobs, clusters, schedules, permissions — is defined in version-controlled
> YAML. Git history shows exactly who changed what, when, and why. When a regulator asks
> 'show me how this risk model was deployed,' you open the Git log. When they ask 'who had
> access to run this job,' you show the permissions block. Unity Catalog adds data lineage
> on top — you can trace a scored claim back through the ingestion pipeline to the raw
> landing zone file."*

### Environment Consistency

> *"Dev and prod are the same bundle with different variable values. There's no 'it worked
> in dev' problem because the code path is identical — only the cluster size, catalog, and
> permissions change. This is declared in YAML, not configured manually in the UI. For
> insurance compliance, this means your validation environment is a faithful replica of
> production, and you can prove it."*

### Disaster Recovery

> *"If the workspace goes down, the entire pipeline definition lives in Git. Run
> `databricks bundle deploy -t prod` against a new workspace and you're back in business —
> same job, same schedule, same permissions. No screenshots of UI configurations, no tribal
> knowledge. The bundle IS the disaster recovery plan. Combined with Unity Catalog's
> cross-workspace metastore, your data catalog and lineage survive too."*
