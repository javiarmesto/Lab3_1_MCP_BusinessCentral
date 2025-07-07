# PowerShell script para crear un ZIP limpio para Azure App Service
# Excluye carpetas y archivos innecesarios (como .venv, bc_server_bkp, copilot-studio-connector, etc.)

$zipName = "deploy.zip"
$exclude = @( ".venv", "bc_server_bkp", "copilot-studio-connector", $zipName )

# Elimina el ZIP anterior si existe
if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}

# Obtiene todos los archivos y carpetas excepto los excluidos
$items = Get-ChildItem -Recurse -File | Where-Object {
    $path = $_.FullName.Replace($PWD.Path + "\", "")
    foreach ($ex in $exclude) {
        if ($path -like "$ex*" -or $path -like "*$ex*" -or $path -match "\\$ex\\") { return $false }
    }
    return $true
}


# Crea el ZIP manteniendo la estructura de carpetas
Compress-Archive -Path $items.FullName -DestinationPath $zipName

Write-Host "ZIP creado: $zipName (excluyendo: $($exclude -join ', '))"
