#define MyAppName "LaunchDock"
#define MyAppPublisher "Dylanliiiii"
#define MyAppURL "https://github.com/Dylanliiiii/LaunchDock"

#ifndef AppVersion
#define AppVersion "1.0.0"
#endif

#ifndef SourceDir
#define SourceDir "..\dist\LaunchDock"
#endif

#ifndef OutputDir
#define OutputDir "..\dist"
#endif

#ifndef IconPath
#define IconPath "..\build\launchdock.ico"
#endif

[Setup]
AppId={{8B536EE7-4F0E-4F13-8A24-469AB5F29D88}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=LaunchDock-v{#AppVersion}-windows-setup
SetupIconFile={#IconPath}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\LaunchDock.exe

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\LaunchDock.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\LaunchDock.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LaunchDock.exe"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
