Set-Location "$PSScriptRoot"

$InputDir = Join-Path $PSScriptRoot "./../../src-md"
$OutputDir = Join-Path $PSScriptRoot "./../../dist"
$PythonScript = Join-Path $PSScriptRoot "./mkdocs_setup.py"

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker не установлен или не в PATH. Установите Docker Desktop."
    exit 1
}

if (!(Test-Path $InputDir)) {
    Write-Host "Создание папки входных файлов: $InputDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $InputDir | Out-Null
}

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

if (!(Test-Path $PythonScript)) {
    Write-Error "Файл $PythonScript не найден. Положите его в одну папку с этим скриптом."
    exit 1
}

$InputPath = (Resolve-Path $InputDir).ProviderPath
$OutputPath = (Resolve-Path $OutputDir).ProviderPath
$ScriptPath = (Resolve-Path $PythonScript).ProviderPath

Write-Host "🐳 Запуск Material for MkDocs в Docker..." -ForegroundColor Cyan
docker run --rm -it `
    -v `"${InputPath}`":/data/input:ro `
    -v `"${OutputPath}`":/data/output `
    -v `"${ScriptPath}`":/app/mkdocs_setup.py:ro `
    -w /app `
    --entrypoint /bin/sh `
    squidfunk/mkdocs-material:latest `
    -c "python /app/mkdocs_setup.py && mkdocs build -f /app/mkdocs.yml"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🎉 Успешно! Откройте: $OutputDir\index.html" -ForegroundColor Green
    Write-Host "💡 Для локального просмотра можно запустить: python -m http.server --directory '$OutputDir'" -ForegroundColor DarkYellow
} else {
    Write-Error "`n❌ Ошибка сборки. Проверьте логи выше."
}
