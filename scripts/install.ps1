$ErrorActionPreference = "Stop"

$Repo       = "wtfenzo/ezfetch"
$BinName    = "ezfetch.exe"
$Artifact   = "ezfetch-windows-amd64.exe"
if ($env:EZFETCH_INSTALL_DIR) { $InstallDir = $env:EZFETCH_INSTALL_DIR } else { $InstallDir = "$HOME\.ezfetch\bin" }

function Info($msg)  { Write-Host "[info]  $msg" -ForegroundColor Cyan }
function Ok($msg)    { Write-Host "[ok]    $msg" -ForegroundColor Green }
function Err($msg)   { Write-Host "[error] $msg" -ForegroundColor Red; exit 1 }


function Get-LatestTag {
    if ($env:EZFETCH_VERSION) { return $env:EZFETCH_VERSION }

    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
        return $release.tag_name
    } catch {
        Err "Could not determine latest release. Set `$env:EZFETCH_VERSION manually."
    }
}



function Download-Binary($tag) {
    $url = "https://github.com/$Repo/releases/download/$tag/$Artifact"
    $tmpBase = [System.IO.Path]::GetTempFileName()
    Remove-Item $tmpBase -ErrorAction SilentlyContinue
    $tmp = $tmpBase + ".exe"

    Info "Downloading $Artifact ($tag) ..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
    } catch {
        Err "Download failed. Check the release exists: $url"
    }

    return $tmp
}



function Install-Binary($tmpFile) {
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }

    $dest = Join-Path $InstallDir $BinName
    Move-Item -Path $tmpFile -Destination $dest -Force
    
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$InstallDir*") {
        Info "Adding $InstallDir to user PATH ..."
        [Environment]::SetEnvironmentVariable("PATH", "$userPath;$InstallDir", "User")
        $env:PATH = "$env:PATH;$InstallDir"
    }

    return $dest
}

Info "ezfetch installer for Windows"

$tag  = Get-LatestTag
Info "Latest release: $tag"

$tmp  = Download-Binary $tag
$dest = Install-Binary $tmp

Ok "Installed to $dest"
Info "Restart your terminal, then run 'ezfetch'."
