[Setup]
AppName=Autonome Job Filler & Gadgets Suite
AppVersion=1.1
DefaultDirName={userdesktop}\JobFiller
DisableDirPage=no
DefaultGroupName=Autonome Job Filler
OutputBaseFilename=JobFiller-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "profile.example.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "profile.example.md"; DestDir: "{app}"; DestName: "profile.md"; Flags: onlyifdoesntexist

[Icons]
Name: "{userdesktop}\Autonome Job Filler"; Filename: "{app}\launcher.bat"; WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 13
Name: "{group}\Autonome Job Filler"; Filename: "{app}\launcher.bat"; WorkingDir: "{app}"

[Run]
Filename: "{app}\launcher.bat"; Description: "Launch Autonome Job Filler Suite now"; Flags: nowait postinstall skipifsilent shellexec
