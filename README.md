# DABs Demo — Databricks Asset Bundles

A minimal live demo showing the full DABs lifecycle: init, validate, deploy, run, destroy.

## Prerequisites

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) v0.200+ installed and authenticated
- Python 3.10+

## Getting Started

```bash
git clone https://github.com/wryszka/dabs-demo.git
cd dabs-demo
```

Before running, update `databricks.yml` if needed:
- Set `workspace.host` to your Databricks workspace URL
- Set `workspace.profile` to match your Databricks CLI profile name (run `databricks auth profiles` to list available profiles)

## Project Structure

```
dabs-demo/
├── databricks.yml            # Bundle configuration (name, targets, workspace)
├── resources/
│   └── dabs_demo_job.yml     # Job definition with a single Python task
├── src/
│   └── hello.py              # print("DABs Demo Successful")
└── README.md                 # This file — the demo script
```

## Bundle Configuration Explained

| Field | Purpose |
|-------|---------|
| `bundle.name` | Unique identifier for the bundle (`dabs_demo`) |
| `targets.dev.mode` | `development` — prefixes resources with `[dev <user>]`, pauses schedules |
| `targets.dev.workspace.host` | The Databricks workspace URL to deploy to |
| `targets.dev.workspace.profile` | The Databricks CLI auth profile to use (from `~/.databrickscfg`) |

---

## Demo Script

### Step 1 — Validate

**Command:**
```bash
databricks bundle validate -t dev
```

**Action:** Checks the bundle configuration for syntax errors, verifies authentication,
and confirms all resource references are valid.

**Observation:** You should see a JSON summary of the bundle with no errors.

---

### Step 2 — Deploy

**Command:**
```bash
databricks bundle deploy -t dev
```

**Action:** Uploads `src/hello.py` to the workspace and creates the job
`[dev <your_username>] dabs_demo_job` in Databricks.

**Observation:** Terminal shows upload and job creation logs.

**UI Verification:** Navigate to **Workflows > Jobs** — you should see
`[dev <your_username>] dabs_demo_job`.

---

### Step 3 — Run

**Command:**
```bash
databricks bundle run -t dev dabs_demo_job
```

**Action:** Triggers the job and streams the run URL to your terminal.

**Observation:** Terminal prints the run URL. Click it to see the run in the UI.

**UI Verification:** Navigate to **Workflows > Job Runs** — the run should show
as succeeded with output: `DABs Demo Successful`.

---

### Step 4 — Cleanup

**Command:**
```bash
databricks bundle destroy -t dev --auto-approve
```

**Action:** Deletes all deployed resources (job + uploaded files) from the workspace.

**Observation:** Terminal confirms each resource is destroyed.

**UI Verification:** Navigate to **Workflows > Jobs** — the job should no longer exist.

---

## Quick Reference

| Step | Action | CLI Command | UI Verification |
|------|--------|-------------|-----------------|
| 1 | Validate | `databricks bundle validate -t dev` | "Success" in terminal |
| 2 | Deploy | `databricks bundle deploy -t dev` | Workflows > Jobs > `[dev] dabs_demo_job` |
| 3 | Run | `databricks bundle run -t dev dabs_demo_job` | Job Runs > Active Runs |
| 4 | Cleanup | `databricks bundle destroy -t dev --auto-approve` | Job deleted from Workflows |
