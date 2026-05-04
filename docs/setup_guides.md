# Setup Guides — Sermilik Fjord Sea Ice Project

Two options for running the notebooks:

- **Option A — Google Colab** (browser-based, no local installation needed — recommended for beginners)
- **Option B — Local setup on Windows** (full local environment, same as the Linux workflow)

---

## Option A: Google Colab

Google Colab runs Jupyter notebooks entirely in your browser. No Python installation required. You only need a Google account.

> **Important:** Colab does not clone the full repository automatically when you open a notebook from GitHub. Because the notebooks import code from the `src/` folder, you must clone the repo manually inside Colab at the start of each session. This takes about 30 seconds and is explained in Step 3 below.

---

### A1 — Prerequisites

- A Google account (gmail.com)
- A Google Earth Engine account with access to the project `sea-ice-sermilik-fjord`

If you do not have a GEE account yet:
1. Go to https://earthengine.google.com and click **Get Started**
2. Sign in with your Google account and request access (academic use)
3. Once approved, go to https://code.earthengine.google.com/register and register the project `sea-ice-sermilik-fjord` — ask your collaborator to invite you to the Google Cloud project first

---

### A2 — Open Google Colab

1. Go to https://colab.research.google.com
2. Sign in with your Google account
3. In the welcome dialog, click the **GitHub** tab
4. Paste the repository URL:
   ```
   https://github.com/j-breitler/Sermilik-Fjord-Ice-Detection-using-Google-Earth-Engine
   ```
5. Press Enter — a list of notebooks appears
6. Click on `notebooks/01_data_acquisition.ipynb` to open it

---

### A3 — Set up the environment (run once per session)

Every time you open a new Colab session, you must run a setup cell before anything else. Add a new cell at the very top of the notebook (click `+ Code` at the top left) and paste this:

```python
# ── Colab setup — run this first, every session ──────────────────────────────
import subprocess, os

# 1. Clone the repository so that src/ imports work
subprocess.run([
    "git", "clone",
    "https://github.com/j-breitler/Sermilik-Fjord-Ice-Detection-using-Google-Earth-Engine.git",
    "/content/sermilik"
], check=True)

# 2. Change into the repo directory
os.chdir("/content/sermilik")

# 3. Install dependencies
subprocess.run(["pip", "install", "-q", "-r", "requirements.txt"], check=True)

# 4. Set the GEE project ID (replaces the .env file)
os.environ["GEE_PROJECT_ID"] = "sea-ice-sermilik-fjord"

print("Setup complete. You can now run the notebook cells below.")
```

Run this cell with **Shift+Enter** and wait for it to finish (takes ~60 seconds).

---

### A4 — Authenticate with Google Earth Engine

After the setup cell, run the normal notebook cells. The first time `ee.Initialize()` is called, Colab will ask you to authenticate:

1. A browser popup appears — sign in with your Google account
2. Grant the requested permissions
3. You are redirected back to Colab automatically

This happens once per session. The credentials are stored in Colab's temporary environment and are lost when the session ends, so you will need to authenticate again next time you open Colab.

---

### A5 — Run the notebooks

After the setup cell and authentication, run all other cells normally with **Shift+Enter**. Work through the notebooks in order:

```
01_data_acquisition.ipynb  →  02_preprocessing.ipynb  →  03_classification.ipynb  → ...
```

When you open a new notebook, repeat the setup cell (A3) at the top before running anything else.

---

### A6 — Saving your outputs

Outputs (CSV files, figures) are saved to `/content/sermilik/outputs/` inside Colab's temporary storage. This storage is deleted when the session ends.

To keep your outputs permanently, export them to Google Drive. Add this cell after any export step:

```python
from google.colab import drive
drive.mount('/content/drive')

import shutil
shutil.copytree(
    '/content/sermilik/outputs',
    '/content/drive/MyDrive/sermilik_outputs',
    dirs_exist_ok=True
)
print("Outputs copied to Google Drive.")
```

---

### A7 — Saving changes to notebooks

If you edit a notebook and want to keep your changes:

1. In Colab: **File → Save a copy in GitHub**
2. Sign in to GitHub when prompted
3. Select the repository and the correct notebook path
4. Add a short commit message and click **OK**

This commits your changes directly back to the shared repository.

---

---

## Option B: Local Setup on Windows

This gives you a full local environment. You run Jupyter in your browser but everything is stored and executed on your own computer.

---

### B1 — Install Git

1. Go to https://git-scm.com/download/win and download the installer
2. Run the installer — accept all defaults
3. After installation, open **Git Bash** (search for it in the Start menu) — use this instead of the regular Windows Command Prompt for all commands below

---

### B2 — Install Python

1. Go to https://www.python.org/downloads/ and download the latest Python 3.12 installer
2. Run the installer
3. **Important:** on the first screen, check the box **"Add Python to PATH"** before clicking Install
4. Verify the installation by opening Git Bash and running:
   ```bash
   python --version
   ```
   You should see something like `Python 3.12.x`

---

### B3 — Clone the repository

In Git Bash, run:

```bash
cd ~/Documents
git clone https://github.com/j-breitler/Sermilik-Fjord-Ice-Detection-using-Google-Earth-Engine.git
cd Sermilik-Fjord-Ice-Detection-using-Google-Earth-Engine
```

This downloads the full repository to `Documents\Sermilik-Fjord-Ice-Detection-using-Google-Earth-Engine\` on your computer.

---

### B4 — Create a virtual environment

In Git Bash, inside the repository folder:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Your prompt will change to show `(.venv)` at the start. This means the virtual environment is active.

> Every time you open a new Git Bash window to work on this project, run `source .venv/Scripts/activate` again before doing anything else.

---

### B5 — Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

This installs all required packages. It will take 2–5 minutes.

---

### B6 — Set up the environment file

```bash
cp .env.example .env
```

Open the `.env` file in Notepad (or any text editor):

```bash
notepad .env
```

Change this line:
```
GEE_PROJECT_ID=your-gee-project-id
```
to:
```
GEE_PROJECT_ID=sea-ice-sermilik-fjord
```

Save and close the file.

---

### B7 — Authenticate with Google Earth Engine

With the virtual environment active, open Python:

```bash
python
```

Then run:

```python
import ee
ee.Authenticate()
ee.Initialize(project='sea-ice-sermilik-fjord')
print(ee.String("GEE connected!").getInfo())
```

`ee.Authenticate()` opens a browser window. Sign in with your Google account and grant access. If it prints `GEE connected!`, everything is working. Exit Python with `exit()`.

> If `ee.Initialize()` fails with a 403 error, make sure the GEE API is enabled for the project:
> go to https://console.developers.google.com/apis/api/earthengine.googleapis.com/overview?project=sea-ice-sermilik-fjord
> and click **Enable**, then wait 2 minutes and try again.

---

### B8 — Register the Jupyter kernel

This makes the notebooks use the correct Python environment:

```bash
pip install ipykernel
python -m ipykernel install --user --name sermilik --display-name "Sermilik Sea Ice"
```

---

### B9 — Open the notebooks

```bash
jupyter notebook
```

This opens Jupyter in your browser. Navigate to the `notebooks/` folder and click `01_data_acquisition.ipynb`.

**Important:** In the top-right corner of the notebook, check that the kernel shows **"Sermilik Sea Ice"**. If it shows something else (e.g. Python 3), click it and select **Sermilik Sea Ice** from the list.

Run cells one at a time with **Shift+Enter**. Work through the notebooks in order.

---

### B10 — Daily workflow

Each time you start working:

1. Open Git Bash
2. Navigate to the repo: `cd ~/Documents/Sermilik-Fjord-Ice-Detection-using-Google-Earth-Engine`
3. Activate the venv: `source .venv/Scripts/activate`
4. Pull the latest changes from GitHub: `git pull`
5. Start Jupyter: `jupyter notebook`

After making changes, save your work to GitHub:

```bash
git add .
git commit -m "short description of what you did"
git push
```
