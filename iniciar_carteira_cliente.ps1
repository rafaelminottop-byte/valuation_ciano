# Inicializador da Carteira do Cliente.
#
# Mesmo esquema do iniciar_app.ps1 (Valuation): sobe o app Streamlit sem janela
# preta, espera ele responder e só entao abre o navegador. Se o app ja estiver
# rodando, so abre o navegador (nao duplica processo).
#
# Chamado pelo atalho "Carteira do Cliente" da Area de Trabalho.

$ErrorActionPreference = "SilentlyContinue"
$projeto = Split-Path -Parent $MyInvocation.MyCommand.Path
$porta = 8502
$url = "http://localhost:$porta"

function AppNoAr {
    try {
        $r = Invoke-WebRequest -Uri "$url/_stcore/health" -UseBasicParsing -TimeoutSec 3
        return $r.Content -match "ok"
    } catch { return $false }
}

if (-not (AppNoAr)) {
    Set-Location $projeto
    $env:BROWSER = "none"   # quem abre o navegador somos nos, na hora certa
    # Tema claro fixo: o visual (marfim/marinho/dourado) nao deve herdar o modo escuro do sistema
    Start-Process -WindowStyle Hidden -FilePath "py" -ArgumentList @(
        "-m", "streamlit", "run", "app_cliente.py",
        "--server.headless", "true", "--server.port", "$porta",
        "--theme.base", "light", "--theme.primaryColor", "#0E2266",
        "--theme.backgroundColor", "#FAF8F3", "--theme.secondaryBackgroundColor", "#F3EFE6",
        "--theme.textColor", "#1C2541"
    )
    # Espera o app responder (ate ~60s: na 1a vez ele consulta o Banco Central)
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 1
        if (AppNoAr) { break }
    }
}

if (AppNoAr) {
    Start-Process $url
} else {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "A Carteira do Cliente nao subiu a tempo.`n`nAbra o Prompt na pasta do projeto e rode:`n  py -m streamlit run app_cliente.py --server.port 8502",
        "Carteira do Cliente", "OK", "Warning") | Out-Null
}
