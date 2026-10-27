; Instalador de TECLA para Windows (Inno Setup 6).
; Se compila desde la raíz del repositorio, después de generar dist\TECLA:
;   ISCC packaging\windows\TECLA.iss

#define AppName "TECLA"
#define AppVersion "2.1.1"
#define AppUrl "https://isabel-mm.github.io/TECLA/"

[Setup]
; No cambiar el AppId: identifica la aplicación en las actualizaciones
AppId={{6F3B1C52-8A4E-4D7B-9C21-5E0A7D2F4B19}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=TECLA
AppPublisherURL={#AppUrl}
AppSupportURL={#AppUrl}
; Instalación por usuario: no pide permisos de administrador
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#AppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SourceDir=..\..
OutputDir=dist
; Sin versión en el nombre: la web enlaza a releases/latest/download/
OutputBaseFilename=TECLA-instalador-windows-setup
SetupIconFile=gui\assets\tecla.ico
UninstallDisplayIcon={app}\TECLA.exe
LicenseFile=LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\TECLA\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\TECLA.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\TECLA.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TECLA.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
