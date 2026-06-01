$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\..\.."
$SourceFile = Join-Path $PSScriptRoot "src\VirtualThreadScalingBenchmark.java"
$OutDir = Join-Path $PSScriptRoot "out"

if (!(Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

Push-Location $ProjectRoot

javac --release 21 -d $OutDir $SourceFile
java -cp $OutDir VirtualThreadScalingBenchmark

Pop-Location