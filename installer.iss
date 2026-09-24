; Inno Setup script for System Audio Recorder.
; Build the onedir PyInstaller output first (see CLAUDE.md), then compile
; this with ISCC.exe (or open it in the Inno Setup Compiler GUI).

#define MyAppName "System Audio Recorder"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "psymore"
#define MyAppExeName "AudioRecorder.exe"

[Setup]
AppId={{B6E1C6C2-6B9B-4A9E-9C2E-6E7C1D8A2F3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Per-user install under %LOCALAPPDATA%\Programs — no admin/UAC required,
; and matches where the app already keeps its data (%LOCALAPPDATA%\AudioRecorder).
DefaultDirName={localappdata}\Programs\{#MyAppName}
PrivilegesRequired=lowest
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=dist_installer
OutputBaseFilename=AudioRecorder-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\AudioRecorder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
