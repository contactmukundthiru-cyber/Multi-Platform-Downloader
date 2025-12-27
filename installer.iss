; ============================================================================
; FLARE DOWNLOAD - Inno Setup Installer Script
; Creates a professional Windows installer (.exe)
; ============================================================================
;
; Requirements to build:
;   1. Install Inno Setup from https://jrsoftware.org/isinfo.php
;   2. Run build_installer.bat (or open this file in Inno Setup and click Build)
;
; The installer will:
;   - Install all files to Program Files
;   - Create Start Menu and Desktop shortcuts
;   - Add to Windows "Add/Remove Programs"
;   - Support repair and uninstall
; ============================================================================

#define MyAppName "Flare Download"
#define MyAppVersion "2.6.1"
#define MyAppPublisher "Mukund Thiru"
#define MyAppURL "https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader"
#define MyAppExeName "FlareDownload.exe"

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
; SetupIconFile=icon.ico  ; Uncomment if you have an icon.ico file
Compression=lzma2/ultra64
SolidCompression=yes

; Appearance
WizardStyle=modern
WizardSizePercent=100

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

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (built with PyInstaller)
Source: "dist\Flare Download.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

; If not using PyInstaller, include Python and all dependencies:
; Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "youtube_downloader.py"; DestDir: "{app}"; Flags: ignoreversion
; Source: "version.py"; DestDir: "{app}"; Flags: ignoreversion
; Source: "updater.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

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
