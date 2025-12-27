; ============================================================================
; FLARE DOWNLOAD - Inno Setup Installer Script
; Creates a professional Windows installer (.exe)
; ============================================================================
;
; Requirements to build:
;   1. Run create_icon.py first to generate icon.ico
;   2. Install Inno Setup from https://jrsoftware.org/isinfo.php
;   3. Run build_installer.bat (or open this file in Inno Setup and click Build)
;
; The installer will:
;   - Install all files to Program Files
;   - Create Start Menu and Desktop shortcuts with icon
;   - Add to Windows "Add/Remove Programs"
;   - Support repair and uninstall
; ============================================================================

#define MyAppName "Flare Download"
#define MyAppVersion "2.6.1"
#define MyAppPublisher "Mukund Thiru"
#define MyAppURL "https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader"
#define MyAppExeName "Flare Download.exe"
#define MyAppDescription "Download videos from YouTube, TikTok, Instagram & 1000+ sites"

[Setup]
; App identity
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases

; Install location
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Output
OutputDir=installer_output
OutputBaseFilename=FlareDownload_Setup_{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes

; Appearance - Modern dark themed installer
WizardStyle=modern
WizardSizePercent=100
WizardImageFile=compiler:WizModernImage.bmp
WizardSmallImageFile=compiler:WizModernSmallImage.bmp

; Privileges (don't require admin)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
Uninstallable=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Misc
AllowNoIcons=yes
DisableProgramGroupPage=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=

; Version info embedded in installer
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
Name: "startmenuicon"; Description: "Create a Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked

[Files]
; Main executable (built with PyInstaller)
Source: "dist\Flare Download.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

; Icon file for shortcuts
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts with icon and description
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Comment: "{#MyAppDescription}"; Tasks: startmenuicon
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"

; Desktop shortcut with icon and description
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Comment: "{#MyAppDescription}"; Tasks: desktopicon

; Taskbar/Quick Launch (for older Windows)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Register file associations (optional - for URL protocols)
Root: HKCU; Subkey: "Software\Classes\{#MyAppName}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyAppName}"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyAppName}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyAppName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

; App registration for better Start Menu appearance
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletekey

[Code]
// Custom code for cleanup and initialization

procedure CleanupOldVersions();
var
  OldPaths: array[0..5] of String;
  DesktopPath: String;
  i: Integer;
begin
  // Old installation directories to clean
  OldPaths[0] := ExpandConstant('{localappdata}\NeonTube');
  OldPaths[1] := ExpandConstant('{localappdata}\FlareDownload');
  OldPaths[2] := ExpandConstant('{localappdata}\YouTubeDownloader');
  OldPaths[3] := ExpandConstant('{userappdata}\NeonTube');
  OldPaths[4] := ExpandConstant('{userappdata}\FlareDownload');
  OldPaths[5] := ExpandConstant('{userappdata}\YouTubeDownloader');

  for i := 0 to 5 do
  begin
    if DirExists(OldPaths[i]) then
    begin
      DelTree(OldPaths[i], True, True, True);
    end;
  end;

  // Clean old desktop shortcuts
  DesktopPath := ExpandConstant('{autodesktop}');
  DeleteFile(DesktopPath + '\NeonTube.lnk');
  DeleteFile(DesktopPath + '\FlareDownload.lnk');
  DeleteFile(DesktopPath + '\YouTube Downloader.lnk');

  // Clean old start menu entries
  DelTree(ExpandConstant('{group}\..\NeonTube'), True, True, True);
  DelTree(ExpandConstant('{group}\..\FlareDownload'), True, True, True);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Cleanup runs before installation
  CleanupOldVersions();
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-install: ensure old versions are cleaned
    CleanupOldVersions();
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Clean app data on uninstall
    AppDataPath := ExpandConstant('{localappdata}\Flare Download');
    if DirExists(AppDataPath) then
      DelTree(AppDataPath, True, True, True);
  end;
end;
