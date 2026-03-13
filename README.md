# DABs Demo — Databricks Asset Bundles

A minimal live demo showing the full DABs lifecycle: validate, deploy, run, destroy.

---

## Prerequisites

### 1. Install the Databricks CLI

```bash
# macOS (Homebrew)
brew tap databricks/tap && brew install databricks

# Linux / WSL
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Verify installation (requires v0.200+)
databricks --version
```

### 2. Configure authentication

```bash
databricks configure
```

When prompted, enter:
- **Databricks Host**: your workspace URL (e.g. `https://myworkspace.cloud.databricks.com`)
- **Personal Access Token**: generate one at **Settings > Developer > Access tokens** in the Databricks UI

Verify it works:

```bash
databricks auth profiles    # should show your profile with Valid = YES
databricks current-user me  # should print your username
```

### 3. Python 3.10+

```bash
python3 --version
```

---

## Getting Started

```bash
git clone https://github.com/wryszka/dabs-demo.git
cd dabs-demo
```

### Connect to your workspace

Edit `databricks.yml` — replace the workspace host:

```yaml
workspace:
  host: https://YOUR-WORKSPACE.cloud.databricks.com   # <-- your URL here
  # profile: DEFAULT                                    # <-- uncomment if you have multiple profiles
```

If you have multiple CLI profiles, uncomment the `profile` line and set it to the profile
name shown by `databricks auth profiles`.

---

## Project Structure

```
dabs-demo/
├── databricks.yml            # Bundle config (name, target, workspace)
├── resources/
│   └── dabs_demo_job.yml     # Job definition — single Python task
├── src/
│   └── hello.py              # print("DABs Demo Successful")
└── README.md
```

---

## Demo Script

### Step 1 — Validate

```bash
databricks bundle validate -t dev
```

**What it does:** Checks YAML syntax, verifies CLI authentication, and confirms all
resource references resolve correctly — all without touching the workspace.

**Expected output:** Bundle summary ending with `Validation OK!`

---

### Step 2 — Deploy

```bash
databricks bundle deploy -t dev
```

**What it does:** Uploads `src/hello.py` to the workspace and creates the job.

**Where to see it in Databricks UI:**

1. Open your workspace in a browser
2. Click **Workflows** in the left sidebar
3. Click the **Jobs** tab
4. Look for **`[dev <your_username>] dabs_demo_job`**
5. Click it to see the job definition — you'll see one task: `hello_task`

The uploaded files are at:
**Workspace > Users > `<you>` > `.bundle/dabs_demo/dev/files/src/hello.py`**

---

### Step 3 — Run

```bash
databricks bundle run -t dev dabs_demo_job
```

**What it does:** Triggers the job immediately and prints a run URL.

**Where to see it in Databricks UI:**

1. Click the **run URL** printed in your terminal, OR:
2. Go to **Workflows > Jobs > `[dev] dabs_demo_job`**
3. Click the **Runs** tab
4. Click the latest run to see task output
5. Click **`hello_task`** to see the output: `DABs Demo Successful`

---

### Step 4 — Cleanup (single command)

```bash
databricks bundle destroy -t dev --auto-approve
```

**What it does:** Deletes all deployed resources — the job and all uploaded files.

**Verify cleanup in Databricks UI:**

1. Go to **Workflows > Jobs**
2. The job `[dev] dabs_demo_job` should no longer appear
3. Go to **Workspace > Users > `<you>`** — the `.bundle/dabs_demo` folder should be gone

---

## Quick Reference

| Step | Command | Where to Verify in UI |
|------|---------|-----------------------|
| Validate | `databricks bundle validate -t dev` | Terminal shows `Validation OK!` |
| Deploy | `databricks bundle deploy -t dev` | **Workflows > Jobs > `[dev] dabs_demo_job`** |
| Run | `databricks bundle run -t dev dabs_demo_job` | **Workflows > Jobs > Runs tab > latest run > hello_task output** |
| Cleanup | `databricks bundle destroy -t dev --auto-approve` | Job gone from **Workflows > Jobs** |

---

## Sharing This Demo

Anyone with a Databricks workspace can run this demo:

1. Clone the repo
2. Replace the `workspace.host` in `databricks.yml` with their workspace URL
3. Run the 4 commands above

No additional dependencies, packages, or catalog setup required.
