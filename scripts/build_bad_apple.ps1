param(
  [Parameter(Mandatory = $true)][string]$InputVideo,
  [string]$OutputGif = "assets/bad-apple-lua.gif",
  [int]$Fps = 10
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
foreach ($Command in @("ffmpeg", "luatex")) {
  if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
    throw "Missing required command: $Command"
  }
}
if (-not (Test-Path $InputVideo -PathType Leaf)) { throw "Input video not found: $InputVideo" }
$OutputPath = Join-Path $Root $OutputGif
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null
$TempPath = [IO.Path]::ChangeExtension($OutputPath, ".tmp.gif")
$ffmpegSource = "ffmpeg -hide_banner -loglevel error -i `"$InputVideo`" -an -vf `"fps=$Fps,scale=76:40:flags=lanczos,format=gray`" -f rawvideo -pix_fmt gray -"
$luaRender = "luatex --luaonly `"$Root/bad_apple.lua`" 76 40 $Fps"
$ffmpegGif = "ffmpeg -hide_banner -loglevel error -f image2pipe -framerate $Fps -vcodec pgm -i - -an -vf format=rgb8 -loop 0 -gifflags +transdiff `"$TempPath`""
cmd /c "$ffmpegSource | $luaRender | $ffmpegGif"
if ($LASTEXITCODE -ne 0) { throw "Animation build failed with exit code $LASTEXITCODE" }
Move-Item -Force $TempPath $OutputPath
$Size = (Get-Item $OutputPath).Length
if ($Size -ge 100MB) { throw "GIF exceeds GitHub's 100 MiB limit. Retry with -Fps 6." }
Write-Host ("Created {0} ({1:N2} MiB)" -f $OutputPath, ($Size / 1MB))
