; Inno Setup script for TUNBEEC Desktop.
; Wraps the PyInstaller "dist\TUNBEEC" onedir build (built by build.bat / CI) into a single
; double-click Setup.exe: no terminal, no "pip install", no admin password needed.
;
; Build with: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
; (build.bat / the GitHub Actions workflow do this automatically.)

#define MyAppName "TUNBEEC"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ANME"
#define MyAppExeName "TUNBEEC.exe"

[Setup]
AppId={{B8F2E1D4-6C3A-4F8E-9A1B-2D5E7C9F0A3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Installs into the current user's own profile -- no admin rights / UAC prompt needed,
; which matters since the person double-clicking this may not have an admin password.
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=TUNBEEC-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\python_tunbeec\resources\image\CU.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\TUNBEEC\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
