$ErrorActionPreference = 'Stop'

$pythonw = 'C:\Users\USER\Desktop\1\OpenJarvis\.venv\Scripts\pythonw.exe'
$script  = 'C:\Users\USER\Desktop\1\launcher\openjarvis.pyw'
$icon    = 'C:\Users\USER\Desktop\1\OpenJarvis\frontend\src-tauri\icons\icon.ico'

foreach ($dir in @("$env:USERPROFILE\Desktop", "$env:APPDATA\Microsoft\Windows\Start Menu\Programs")) {
    $path = Join-Path $dir 'OpenJarvis.lnk'
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($path)
    $lnk.TargetPath = $pythonw
    $lnk.Arguments = '"' + $script + '"'
    $lnk.WorkingDirectory = 'C:\Users\USER\Desktop\1\launcher'
    $lnk.IconLocation = $icon + ',0'
    $lnk.Description = 'OpenJarvis - local AI assistant'
    $lnk.WindowStyle = 7
    $lnk.Save()
    Write-Output "created: $path"
}
