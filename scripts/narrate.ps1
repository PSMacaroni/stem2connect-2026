# Speak the SSML files that scripts/narrate.py wrote, one WAV per shot plus one continuous track.
#
# Usage (Windows PowerShell, from the repo root):
#     powershell -ExecutionPolicy Bypass -File scripts\narrate.ps1
#     powershell -ExecutionPolicy Bypass -File scripts\narrate.ps1 -Voice "Microsoft Zira Desktop"
#
# The default voice is the one Prakhar chose on 2026-11-09 after hearing both (Zira is the other one installed).
#
# Run scripts/narrate.py first. This script only reads dist\narration\shot-*.ssml and writes .wav beside them;
# it never touches the script or the repo. Windows-only: it uses the speech synthesiser built into Windows.
#
# Rate 0 is the voice's own default, which measured 142-146 words a minute, the pace docs/video.md budgets for.
# Every duration printed is read back out of the WAV it just wrote, so the timing report is measured, not assumed.

param(
    [string]$Voice = 'Microsoft David Desktop',
    [int]$Rate = 0,
    [string]$Dir = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech

if ($Dir -eq '') {
    $Dir = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) 'dist\narration'
}
if (-not (Test-Path $Dir)) {
    throw "No $Dir - run: uv run python scripts/narrate.py"
}

$ssml = Get-ChildItem -Path $Dir -Filter 'shot-*.ssml' | Sort-Object { [int]($_.BaseName -replace '\D', '') }
if ($ssml.Count -eq 0) { throw "No shot-*.ssml in $Dir - run: uv run python scripts/narrate.py" }

function Get-WavSeconds($path) {
    $b = [System.IO.File]::ReadAllBytes($path)
    $byteRate = [BitConverter]::ToInt32($b, 28)
    return ($b.Length - 44) / $byteRate
}

"voice: $Voice   rate: $Rate"
""

# One file per shot: the recorder clicks, plays a shot, clicks on.
$total = 0.0
foreach ($f in $ssml) {
    $wav = Join-Path $Dir ($f.BaseName + '.wav')
    $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $s.SelectVoice($Voice)
    $s.Rate = $Rate
    $s.SetOutputToWaveFile($wav)
    $s.SpeakSsml((Get-Content -Raw -Encoding UTF8 $f.FullName))
    $s.Dispose()
    $sec = Get-WavSeconds $wav
    $total += $sec
    "{0,-14} {1,6:N1} s" -f $f.BaseName, $sec
}

# One continuous track, same synthesiser settings, for checking the total against the 6:00 limit.
$all = Join-Path $Dir 'narration-full.wav'
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SelectVoice($Voice)
$s.Rate = $Rate
$s.SetOutputToWaveFile($all)
foreach ($f in $ssml) { $s.SpeakSsml((Get-Content -Raw -Encoding UTF8 $f.FullName)) }
$s.Dispose()
$fullSec = Get-WavSeconds $all

""
"{0,-14} {1,6:N1} s   ({2:N0}:{3:00})" -f 'shots added up', $total, [math]::Floor($total / 60), ($total % 60)
"{0,-14} {1,6:N1} s   ({2:N0}:{3:00})  <- narration-full.wav" -f 'one track', $fullSec, [math]::Floor($fullSec / 60), ($fullSec % 60)
""
$left = 360 - $fullSec
if ($left -lt 0) {
    "OVER the 6:00 limit by {0:N0} s of speech alone. Cut sentences from docs/video.md, do not speed the voice up." -f (-$left)
} else {
    "{0:N0} s under the 6:00 limit, and that is before any gap you leave between shots." -f $left
}
