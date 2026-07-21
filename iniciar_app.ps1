# Inicializador do Valuation Ciano.
#
# Sobe o app (Streamlit) sem janela preta e abre o navegador quando ele estiver
# pronto — em vez de abrir na hora e mostrar erro de conexao enquanto carrega.
# Se o app ja estiver rodando, so abre o navegador (nao duplica processo).
#
# Chamado pelo atalho "Valuation Ciano" da Area de Trabalho.

$ErrorActionPreference = "SilentlyContinue"
$projeto = Split-Path -Parent $MyInvocation.MyCommand.Path
$porta = 8501
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
    Start-Process -WindowStyle Hidden -FilePath "py" -ArgumentList @(
        "-m", "streamlit", "run", "app.py",
        "--server.headless", "true", "--server.port", "$porta"
    )
    # Espera o app responder (ate ~40s) antes de abrir o navegador
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Seconds 1
        if (AppNoAr) { break }
    }
}

if (AppNoAr) {
    Start-Process $url
} else {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "O Valuation Ciano nao subiu a tempo.`n`nAbra o Prompt na pasta do projeto e rode:`n  py -m streamlit run app.py",
        "Valuation Ciano", "OK", "Warning") | Out-Null
}
