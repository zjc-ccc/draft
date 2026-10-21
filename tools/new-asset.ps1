<#
.SYNOPSIS
    Create a new asset folder: assets/<category>/<id>/ with source/, export/ and a README from the template.

.EXAMPLE
    .\tools\new-asset.ps1 -Id slime -Category characters

.EXAMPLE
    .\tools\new-asset.ps1 wooden-door props
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Id,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$Category,

    # Repository root. Defaults to the parent of this script.
    [string]$Root
)

$ErrorActionPreference = 'Stop'
$Kebab = '^[a-z0-9]+(-[a-z0-9]+)*$'

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
$Root = (Resolve-Path $Root).Path

if ($Id -notmatch $Kebab) {
    throw "Invalid -Id '$Id'. Use lowercase kebab-case, e.g. slime or wooden-door."
}
if ($Category -notmatch $Kebab) {
    throw "Invalid -Category '$Category'. Use lowercase kebab-case, e.g. characters."
}

$template = Join-Path $Root 'templates\asset\README.md'
if (-not (Test-Path $template)) { throw "Template not found: $template" }

$target = Join-Path $Root "assets\$Category\$Id"
if (Test-Path $target) { throw "Asset already exists: assets\$Category\$Id" }

New-Item -ItemType Directory -Force -Path (Join-Path $target 'source') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $target 'export') | Out-Null

$text = [System.IO.File]::ReadAllText($template, [System.Text.Encoding]::UTF8)
$text = $text.Replace('{{ID}}', $Id).Replace('{{CATEGORY}}', $Category).Replace('{{DATE}}', (Get-Date -Format 'yyyy-MM-dd'))

$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText((Join-Path $target 'README.md'), $text, $utf8)

Write-Host "已创建 assets/$Category/$Id" -ForegroundColor Green
Write-Host "  source\  <- 放可编辑源文件（.aseprite / .psd / .kra）"
Write-Host "  export\  <- 放导出给 Godot 的 PNG"
Write-Host ""
Write-Host "下一步：画完填好 README.md，运行 .\tools\build-index.ps1 更新索引"
