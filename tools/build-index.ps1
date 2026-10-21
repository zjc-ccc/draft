<#
.SYNOPSIS
    Rebuild INDEX.md from every asset README, and warn about naming / metadata problems.

.EXAMPLE
    .\tools\build-index.ps1
#>
[CmdletBinding()]
param(
    # Repository root. Defaults to the parent of this script.
    [string]$Root
)

$ErrorActionPreference = 'Stop'
$Kebab = '^[a-z0-9]+(-[a-z0-9]+)*$'
$Utf8 = [System.Text.UTF8Encoding]::new($false)

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
$Root = (Resolve-Path $Root).Path

$assetsRoot = Join-Path $Root 'assets'
$templatePath = Join-Path $Root 'templates\index.md'
$indexPath = Join-Path $Root 'INDEX.md'

if (-not (Test-Path $templatePath)) { throw "Template not found: $templatePath" }

function Get-FrontMatter {
    param([string]$Path)

    $meta = [ordered]@{}
    if (-not (Test-Path $Path)) { return $meta }

    $inBlock = $false
    foreach ($line in [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)) {
        if ($line.Trim() -eq '---') {
            if ($inBlock) { break } else { $inBlock = $true; continue }
        }
        if ($inBlock -and $line -match '^\s*([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*)$') {
            $meta[$matches[1]] = $matches[2].Trim()
        }
    }
    return $meta
}

function Get-Value {
    param($Meta, [string]$Key, [string]$Default = '-')
    if ($Meta.Contains($Key) -and $Meta[$Key]) { return $Meta[$Key] }
    return $Default
}

$rows = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$count = 0

if (Test-Path $assetsRoot) {
    foreach ($categoryDir in Get-ChildItem $assetsRoot -Directory | Sort-Object Name) {
        $category = $categoryDir.Name
        if ($category -notmatch $Kebab) {
            $warnings.Add("- category folder is not kebab-case: assets/$category")
        }
        foreach ($assetDir in Get-ChildItem $categoryDir.FullName -Directory | Sort-Object Name) {
            $id = $assetDir.Name
            $rel = "assets/$category/$id"
            $meta = Get-FrontMatter (Join-Path $assetDir.FullName 'README.md')

            if ($id -notmatch $Kebab) {
                $warnings.Add("- folder name is not kebab-case: $rel")
            }
            if ($meta.Count -eq 0) {
                $warnings.Add("- no YAML front matter in README: $rel")
            } else {
                $metaId = Get-Value $meta 'id'
                $metaCategory = Get-Value $meta 'category'
                $status = Get-Value $meta 'status'
                if ($metaId -ne $id) { $warnings.Add("- README id '$metaId' does not match folder name: $rel") }
                if ($metaCategory -ne $category) { $warnings.Add("- README category '$metaCategory' does not match folder: $rel") }
                if ($status -notin @('idea', 'wip', 'review', 'done', 'dropped')) {
                    $warnings.Add("- unknown status '$status' (expected idea/wip/review/done/dropped): $rel")
                }
            }

            $exportDir = Join-Path $assetDir.FullName 'export'
            $exportCount = 0
            if (Test-Path $exportDir) {
                $exportCount = (Get-ChildItem $exportDir -File -Recurse | Measure-Object).Count
            }
            if ($exportCount -eq 0 -and (Get-Value $meta 'status') -eq 'done') {
                $warnings.Add("- status is 'done' but export/ is empty: $rel")
            }

            $count++
            $rows.Add("| [$id]($rel/) | $category | $(Get-Value $meta 'status' '?') | $(Get-Value $meta 'size') | $(Get-Value $meta 'frames') | $(Get-Value $meta 'fps') | $(Get-Value $meta 'license' '?') | $(Get-Value $meta 'created') | $exportCount |")
        }
    }
}

if ($count -eq 0) {
    $summary = '还没有素材。运行 `.\tools\new-asset.ps1 -Id <name> -Category <category>` 创建第一个。'
    $rows.Add('| _（空）_ | | | | | | | | |')
} else {
    $summary = "共 $count 个素材。"
}

if ($warnings.Count -gt 0) {
    $warningText = "## 需要处理`n`n" + ($warnings -join "`n")
} else {
    $warningText = ''
}

$text = [System.IO.File]::ReadAllText($templatePath, [System.Text.Encoding]::UTF8)
$text = $text.Replace('{{SUMMARY}}', $summary).Replace('{{ROWS}}', ($rows -join "`n")).Replace('{{WARNINGS}}', $warningText)

[System.IO.File]::WriteAllText($indexPath, $text, $Utf8)

Write-Host "INDEX.md 已更新：$count 个素材" -ForegroundColor Green
if ($warnings.Count -gt 0) {
    Write-Host "$($warnings.Count) 条警告：" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "  $_" }
}
