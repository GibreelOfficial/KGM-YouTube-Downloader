[Setup]
AppId={{A8F93C2F-7B4D-4A2E-BC4E-1D7A4F8B9C3E}
AppName=KGM YouTube Downloader
AppVersion=2.0.0-beta_1
AppPublisher=Kisakye Gibreel
DefaultDirName={autopf}\KGM YouTube Downloader
DefaultGroupName=KGM YouTube Downloader
AllowNoIcons=yes
; Save the installer artifact to your root project distribution folder
OutputDir=X:\CodeX\KGM-YouTube-Downloader\dist
OutputBaseFilename=KGM_YouTube_Downloader_Setup
; Apply your custom branding logo to the installer setup executable framework
SetupIconFile=X:\CodeX\KGM-YouTube-Downloader\dist\KGM YouTube Downloader\_internal\assets\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The main application execution entry point
Source: "X:\CodeX\KGM-YouTube-Downloader\dist\KGM YouTube Downloader\KGM YouTube Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion
; Safely extract and embed all dependency components and _internal sandboxes recursively 
Source: "X:\CodeX\KGM-YouTube-Downloader\dist\KGM YouTube Downloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Exclude copying the main executable twice during recursive grouping extraction
Source: "X:\CodeX\KGM-YouTube-Downloader\dist\KGM YouTube Downloader\*"; Excludes: "KGM YouTube Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\KGM YouTube Downloader"; Filename: "{app}\KGM YouTube Downloader.exe"
Name: "{autodesktop}\KGM YouTube Downloader"; Filename: "{app}\KGM YouTube Downloader.exe"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,KGM YouTube Downloader}"; Flags: nowait postinstall skipifsilent; Filename: "{app}\KGM YouTube Downloader.exe"