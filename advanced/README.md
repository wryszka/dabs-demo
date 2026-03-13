# Advanced DABs Demo — Insurance Claims Risk Scoring Pipeline

A production-grade Databricks Asset Bundle demonstrating a multi-task ML pipeline
with Unity Catalog, environment overrides, permissions, and CI/CD-ready configuration.

## Use Case

A daily pipeline for an insurance company that:

1. **Ingests** raw claims data from a landing zone into Unity Catalog (`raw_claims`)
2. **Scores** each claim with an ML-based risk model, writing results to `scored_claims`

Claims are categorized as **HIGH**, **MEDIUM**, or **LOW** risk based on amount,
type, claimant demographics, and prior history.

---

## Project Structure

```
advanced/
├── databricks.yml                 # Bundle config: name, variables, dev/prod targets
├── resources/
│   └── insurance_job.yml          # Multi-task workflow with cluster overrides + permissions
├── src/
│   ├── ingest.py                  # Claims ingestion (mock data → Unity Catalog)
│   └── scoring.py                 # Risk scoring model (rule-based mock ML)
└── README.md                      # This file — demo script + talk track
```

---

## Bundle Configuration Highlights

| Feature | How It's Implemented |
|---------|---------------------|
| **Two targets** | `dev` (single-node, development mode) and `prod` (autoscaling, production mode) |
| **Environment overrides** | Dev: `Standard_DS3_v2`, 0 workers. Prod: `Standard_DS4_v2`, 2–10 autoscaling workers |
| **Unity Catalog variables** | `${var.catalog}` and `${var.schema}` resolve per target (e.g., `dev_insurance_catalog`) |
| **Task dependencies** | `score_risk` depends on `ingest_claims` — enforced in the workflow DAG |
| **Permissions** | `claims_auditors` group gets `CAN_VIEW` on the job |
| **Schedule** | Daily at 6 AM UTC via cron (paused automatically in dev mode) |
| **Queue** | Job queuing enabled for concurrent run management |

---

## Prerequisites

- Databricks CLI v0.200+ authenticated (`databricks auth profiles`)
- Python 3.10+
- Access to a Databricks workspace with Unity Catalog enabled

### Setup

```bash
git clone https://github.com/wryszka/dabs-demo.git
cd dabs-demo/advanced
```

Update `databricks.yml` if needed:
- `workspace.host` — your workspace URL
- `workspace.profile` — your CLI profile name
- `variables.catalog` / `variables.schema` — your Unity Catalog names

---

## Demo Script

### Step 1 — Validate (Dev)

**Command:**
```bash
databricks bundle validate -t dev
```

**Action:** Validates bundle syntax, authentication, variable resolution, resource
references, and cluster configurations for the dev target.

**Observation:** JSON summary showing resolved variables (`dev_insurance_catalog.claims`),
single-node cluster config, and "Validation OK!" message.

**Talk Track:** *"Before anything touches the workspace, `validate` catches
misconfigurations locally. This is your first gate in CI/CD — every PR runs this."*

---

### Step 2 — Validate (Prod)

**Command:**
```bash
databricks bundle validate -t prod
```

**Action:** Same validation but resolves prod variables and autoscaling cluster config.

**Observation:** Variables resolve to `prod_insurance_catalog`, clusters show 2–10 workers.

**Talk Track:** *"Same bundle, different target. The config is identical in Git —
environment differences are declared, not ad-hoc. This is how you get environment
consistency for regulatory compliance."*

---

### Step 3 — Deploy to Dev

**Command:**
```bash
databricks bundle deploy -t dev
```

**Action:** Uploads `src/ingest.py` and `src/scoring.py`, creates the multi-task job
`[dev <username>] insurance_claims_risk_scoring` with schedule paused.

**Observation:** Terminal logs show file uploads and job creation.

**UI Verification:** **Workflows > Jobs** — click the job to see the two-task DAG
(ingest_claims → score_risk).

**Talk Track:** *"In dev mode, DABs automatically prefixes your name and pauses
schedules — no risk of dev jobs running against production data."*

---

### Step 4 — Run in Dev

**Command:**
```bash
databricks bundle run -t dev insurance_claims_job
```

**Action:** Triggers an immediate run. The ingest task writes 6 mock claims to
`dev_insurance_catalog.claims.raw_claims`, then the scoring task reads them and
writes risk scores to `dev_insurance_catalog.claims.scored_claims`.

**Observation:** Terminal streams the run URL. Job output shows:
- Ingestion: 6 claims written
- Scoring: risk distribution summary (HIGH / MEDIUM / LOW counts)

**UI Verification:** **Workflows > Job Runs** — click into the run to see both
task outputs and the DAG execution.

**Talk Track:** *"One command triggers the full pipeline. The dependency graph
ensures scoring never runs before ingestion completes. In Unity Catalog, you can
trace the lineage from landing zone to scored output — that's your audit trail."*

---

### Step 5 — Deploy to Prod

**Command:**
```bash
databricks bundle deploy -t prod
```

**Action:** Creates the production job `insurance_claims_risk_scoring` with:
- Autoscaling clusters (2–10 workers)
- Daily 6 AM UTC schedule (active)
- `claims_auditors` group permissions

**Observation:** Terminal shows prod deployment with autoscaling config.

**UI Verification:** **Workflows > Jobs** — job has the daily schedule active and
permissions set.

**Talk Track:** *"Deploying to prod uses the exact same code from Git — no manual
configuration, no drift. The autoscaling cluster handles variable claim volumes,
and the auditor group has view-only access for compliance reviews."*

---

### Step 6 — Triggered Run (Prod)

**Command:**
```bash
databricks bundle run -t prod insurance_claims_job
```

**Action:** Triggers an ad-hoc production run (in addition to the daily schedule).

**UI Verification:** Job runs against `prod_insurance_catalog` with production clusters.

---

### Step 7 — Cleanup

```bash
# Destroy dev resources
databricks bundle destroy -t dev --auto-approve

# Destroy prod resources (when done demoing)
databricks bundle destroy -t prod --auto-approve
```

**UI Verification:** Both jobs removed from **Workflows > Jobs**.

---

## Quick Reference

| Step | Action | Command | What to Show |
|------|--------|---------|--------------|
| 1 | Validate dev | `databricks bundle validate -t dev` | Variable resolution, single-node config |
| 2 | Validate prod | `databricks bundle validate -t prod` | Autoscaling config, prod catalog |
| 3 | Deploy dev | `databricks bundle deploy -t dev` | Job in Workflows with `[dev]` prefix |
| 4 | Run dev | `databricks bundle run -t dev insurance_claims_job` | Two-task DAG, risk scores in output |
| 5 | Deploy prod | `databricks bundle deploy -t prod` | Schedule active, permissions set |
| 6 | Run prod | `databricks bundle run -t prod insurance_claims_job` | Production clusters, prod catalog |
| 7 | Cleanup | `databricks bundle destroy -t dev --auto-approve` | Jobs removed |

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
> `databricks bundle deploy -t prod` against a new workspace and you're back in
> business — same job, same schedule, same permissions. No screenshots of UI
> configurations, no tribal knowledge. The bundle IS the disaster recovery plan.
> Combined with Unity Catalog's cross-workspace metastore, your data catalog
> and lineage survive too."*
