; Inno Setup Script for FaceFolio
; Save this file as setup.iss in your project's root directory.

#define MyAppName "FaceFolio"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Name"
#define MyAppURL "https://your-website.com"
#define MyAppExeName "FaceFolio.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value for other applications.
AppId={{F03E8A5B-943A-4E1F-B841-2D28B6E321B0}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; The final setup executable file name.
OutputBaseFilename=FaceFolio_Setup_v{#MyAppVersion}
; The installer will be created in an 'installer' sub-folder.
OutputDir=installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Use an icon for the installer itself.
SetupIconFile=icon.ico
; Optional: Add a license file that the user must accept.
; LicenseFile=LICENSE.txt
; Optional: Custom branding for the installer wizard.
; WizardImageFile=WizardImage.bmp
; WizardSmallImageFile=WizardSmallImage.bmp
; Icon for the Add/Remove Programs entry.
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; These lines create checkboxes in the installer wizard.
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; This is the most important line. It tells the installer to find your application
; inside the 'dist' folder relative to this script.
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; These lines create the Start Menu and optional Desktop icons.
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; This line runs your application automatically after the installation is complete.
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
