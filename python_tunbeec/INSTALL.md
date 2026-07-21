# TUNBEEC Desktop (Python) — Install & Run Guide

Python/PySide6 port of the original TUNBEEC Java desktop app (Tunisian building energy code
compliance tool, ANME). This folder is self-contained — it does not depend on anything outside
`python_tunbeec/`.

## 1. Requirements

- Python 3.10 or newer (3.11–3.13 recommended; 3.14 also works).
- Windows/Mac/Linux — the **Prescriptive** compliance path works identically on all three.
- The **Performance** path (DOE-2.2 simulation) needs `resources/doe22/RUN22.exe`, which is a
  **Windows-only** binary. On macOS/Linux you can still generate the `.inp` simulation file, but
  the actual DOE-2.2 run has to happen on Windows (see §5).

## 2. Install

Open a terminal in this folder (the one containing `main.py`) and run:

**Windows (cmd):**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux (bash):**
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This installs PySide6 (the only dependency) into an isolated virtual environment.

## 3. Run

With the virtual environment activated:
```
python main.py
```
(Windows: you can also just double-click `main.py` once the venv is set up, though running it
from the activated venv terminal is more reliable.)

The main window opens with 4 tabs — Informations Générales, Enveloppe, Espaces, Système CVCA —
plus a button row for New/Open/Save/Save As and the two compliance checks.

## 4. Try it with a sample project

`PROJECT/` ships with 5 pre-built sample projects (`test1.tct` … `test5.tct`). Use **Ouvrir** in
the app and pick one of them, then click **Approche Prescriptive** to run the compliance check.

## 5. Approche Performencielle (DOE-2.2)

Clicking **Approche Performencielle**:
1. Generates the DOE-2.2 `.inp` BDL file next to your saved project (e.g. `PROJECT/myproj.inp`).
2. On Windows, automatically runs `resources/doe22/RUN22.exe` to simulate it and produce
   `myproj.sim`, then shows the Performance Compliance Report.
3. On macOS/Linux, the `.inp` file is still generated, but RUN22.exe can't run — you'll see a
   message telling you to run it via the original Windows installation. If you copy the
   resulting `.sim` file back into the same `PROJECT/` folder and click the button again, the
   report will be generated from that `.sim` automatically (no re-simulation needed).

**Note on Wine:** running `resources/doe22/RUN22.exe` (and the `DOEBDL.EXE`/`DOESIM.EXE` binaries
it calls) under Wine on macOS was tried and does not work — both crash with an illegal-instruction
fault (`VERR`, a legacy protected-mode CPU instruction) under Wine's WOW64 layer on Apple Silicon.
This is a hard compatibility gap in these 1990s/2000s-era binaries, not a configuration problem, so
a real Windows install/VM is required for the simulation step — Wine is not a working substitute.

### 5a. Setting up a Windows machine/VM to run the simulation

If you're on macOS/Linux day-to-day, you still need access to a real Windows environment (a
physical PC, Boot Camp, or a VM such as Parallels/VMware/VirtualBox running Windows 10/11) to
produce `.sim` files. Two ways to use it:

**Option A — run the full TUNBEEC app on Windows**

Copy (or clone) this entire `python_tunbeec/` folder onto the Windows machine, then follow §2/§3
above using the Windows commands:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Open the same project (or copy the `.tct` file over), click **Approche Performencielle** — it
generates the `.inp` and runs `RUN22.exe` automatically, all in one place. Copy the resulting
`myproj.tct`/`.sim` back to your Mac/Linux machine to keep working there.

**Option B — only run the DOE-2.2 step on Windows**

If you'd rather not set up Python on the Windows machine, just copy the `resources/doe22/` folder
over (it's self-contained: `RUN22.exe`, `exent/`, `weather/`) along with the `.inp` file generated
on Mac/Linux, then from a Windows `cmd` prompt inside that copied `doe22` folder run:
```
RUN22.exe  <folder containing myproj.inp>  myproj  <path to doe22>\weather  <LOCATION>  <path to doe22>\exent
```
- `<folder containing myproj.inp>` — the directory holding the `.inp` file (no trailing filename).
- `myproj` — the file name **without** the `.inp` extension.
- `<LOCATION>` — the weather file name without `.bin`, e.g. `TUNIS`, `SFAX` (see
  `resources/doe22/weather/` for the full list of Tunisian cities).

This produces `myproj.sim` in that same folder — copy it back into your project's `PROJECT/`
folder on Mac/Linux and re-click **Approche Performencielle** to get the report.

**Troubleshooting on Windows:** `RUN22.exe`/`DOEBDL.EXE`/`DOESIM.EXE` are old 32-bit console
binaries. If Windows reports a missing runtime DLL, install the
[Microsoft Visual C++ Redistributable](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist)
(x86). On Windows on ARM, they run through Windows' built-in x86 emulation the same as any other
32-bit Windows app.

## 6. Project files

- Saved projects are plain SQLite `.tct` files in `PROJECT/` — the same format the original Java
  app used, so files are interchangeable both ways.
- `resources/lib1/DefaultDB.tct` is the reference library (materials, constructions, glass types,
  building types, locations, HVAC systems). Don't rename or move it — `tunbeec/app_paths.py`
  expects it at that exact path.
- A log file (`applog.txt`) is written next to `main.py` on each run — useful to attach if
  something breaks.

## 7. Project layout

```
python_tunbeec/
  main.py                  entry point
  requirements.txt
  tunbeec/
    calc/                   compliance-check math (prescriptive + performance/DOE-2.2 + reports)
    data/                   reference-DB loader + .tct project load/save
    ui/                     PySide6 windows/dialogs
  resources/                bundled reference DB, DOE-2.2 binaries, images, config
  PROJECT/                  saved projects (test1-5 are samples)
```
