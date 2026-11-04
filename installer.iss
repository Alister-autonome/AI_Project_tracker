[Setup]
AppName=Job Hunter
AppVersion=2.0
DefaultDirName={userdesktop}\JobFiller
DisableDirPage=no
DefaultGroupName=Job Hunter
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
Source: ".streamlit\config.toml"; DestDir: "{app}\.streamlit"; Flags: ignoreversion
Source: "profile.example.md"; DestDir: "{app}"; DestName: "profile.md"; Flags: onlyifdoesntexist

[Icons]
Name: "{userdesktop}\Job Hunter"; Filename: "{app}\launcher.bat"; WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 13
Name: "{group}\Job Hunter"; Filename: "{app}\launcher.bat"; WorkingDir: "{app}"

[Run]
Filename: "{app}\launcher.bat"; Description: "Launch Job Hunter now"; Flags: nowait postinstall skipifsilent shellexec
