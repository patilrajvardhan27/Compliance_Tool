# TUNBEEC Windows Installer

Turns `python_tunbeec/` into a single `TUNBEEC-Setup.exe` — double-click, click Next a few
times, get a desktop icon. No terminal, no Python, no `pip install`, nothing to configure.
That's the file you hand to your professor.

**Important:** this has to be *built* on a real Windows machine (or Windows CI) — PyInstaller
does not cross-compile from macOS to Windows. You have two options:

## Option A — build it in the cloud (recommended, no Windows machine needed)

This repo has a GitHub Actions workflow (`.github/workflows/build-windows-installer.yml`) that
does the whole build on a Windows runner and hands you back the finished installer.

1. Push this repo to GitHub (it already has the `origin` remote configured).
2. On GitHub, go to **Actions → Build Windows Installer → Run workflow**.
3. Wait a few minutes for it to finish, then open the run and download the **TUNBEEC-Setup**
   artifact — that zip contains `TUNBEEC-Setup.exe`.
4. Send `TUNBEEC-Setup.exe` to your professor (email, USB drive, Drive link — it's one file).

Tip: pushing a tag like `v1.0.0` (`git tag v1.0.0 && git push origin v1.0.0`) also attaches the
installer to a GitHub Release automatically, so you get a permanent download link.

## Option B — build it yourself on a Windows PC/VM

1. Install [Python 3.10+](https://python.org/downloads) (check "Add python.exe to PATH") and
   [Inno Setup 6](https://jrsoftware.org/isdl.php) — both are one-click Windows installers.
2. Copy this whole repo (or at least `python_tunbeec/` and `windows_exe/`, keeping them as
   siblings) onto the Windows machine.
3. Double-click `windows_exe\build.bat`. It creates its own build environment, installs
   PySide6 + PyInstaller, builds the app, then packages it with Inno Setup.
4. The finished installer lands at `windows_exe\installer_output\TUNBEEC-Setup.exe`.

## What the professor experiences

1. Double-click `TUNBEEC-Setup.exe`.
2. Click Next → Next → Install → Finish (no admin password prompt — it installs to their own
   user profile, not Program Files).
3. A **TUNBEEC** icon appears on the Desktop and in the Start Menu. That's it — PySide6 and
   every other dependency are already inside the install folder.
4. Uninstalling later works the normal Windows way: Settings → Apps → TUNBEEC → Uninstall.

Sample projects (`PROJECT/test1.tct` … `test5.tct`) are bundled in, so **Ouvrir** works out of
the box for a first look. The DOE-2.2 "Approche Performencielle" step also works immediately —
`RUN22.exe` is a Windows binary and is bundled with the installer.

## How it fits together

| File | Purpose |
|---|---|
| `tunbeec.spec` | PyInstaller spec — bundles `main.py`, `tunbeec/`, `resources/`, and sample `PROJECT/` files into a windowed `TUNBEEC.exe` (no console flash) with the app icon. |
| `installer.iss` | Inno Setup script — wraps the PyInstaller output into `TUNBEEC-Setup.exe` with Start Menu/Desktop shortcuts and a normal uninstaller. Installs per-user, no admin rights needed. |
| `build.bat` | One-shot build script for a real Windows machine: sets up a build venv, runs PyInstaller, then Inno Setup. |
| `../.github/workflows/build-windows-installer.yml` | Runs the same steps on a GitHub-hosted Windows runner, for when you don't have a Windows machine at all. |

Bump `MyAppVersion` in `installer.iss` when you cut a new release — everything else stays the
same.

### Note on `RUN22.exe`

`resources/doe22/RUN22.exe` (bundled from `python_tunbeec/resources/doe22/`) is an old 32-bit
console binary. If Windows complains about a missing runtime DLL when running a simulation, the
professor needs the [Microsoft Visual C++ Redistributable
(x86)](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist) — a second one-click
installer, unrelated to TUNBEEC itself. Worth testing on a clean Windows machine before handing
this off, since the machine you build on may already have it installed.
