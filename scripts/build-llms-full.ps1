#Requires -Version 5.1
# build-llms-full.ps1 - regenerate llms-full.txt from current sources.
# Concatenates README + docs/*.md and appends a generated tool/REST/MCP
# surface section (routes parsed live from the router source, so endpoint
# drift shows up on the next regeneration). ASCII-only (PS 5.1 safe).
# Re-run after any tool, route, prompt, or docs change.

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $RepoRoot 'llms-full.txt'

$sb = New-Object System.Text.StringBuilder
$sb.AppendLine('# davinci-resolve-mcp - full reference (generated)') | Out-Null
$sb.AppendLine('') | Out-Null
$stamp = (Get-Date).ToString('yyyy-MM-dd')
$sb.AppendLine('_Generated: ' + $stamp + ' - do not hand-edit; run scripts/build-llms-full.ps1_') | Out-Null
$sb.AppendLine('') | Out-Null

$sb.AppendLine('## README') | Out-Null
$sb.AppendLine('') | Out-Null
$sb.AppendLine([System.IO.File]::ReadAllText((Join-Path $RepoRoot 'README.md'))) | Out-Null
$sb.AppendLine('') | Out-Null

foreach ($doc in Get-ChildItem (Join-Path $RepoRoot 'docs/*.md') | Sort-Object Name) {
    $sb.AppendLine('## docs/' + $doc.Name) | Out-Null
    $sb.AppendLine('') | Out-Null
    $sb.AppendLine([System.IO.File]::ReadAllText($doc.FullName)) | Out-Null
    $sb.AppendLine('') | Out-Null
}

$sb.AppendLine('## REST surface (parsed from src/davinci_resolve_mcp/api/routes.py)') | Out-Null
$sb.AppendLine('') | Out-Null
$routerPath = Join-Path $RepoRoot 'src/davinci_resolve_mcp/api/routes.py'
$pattern = '@router\.(get|post|patch|delete)\("(.+?)"'
$routes = Select-String -Path $routerPath -Pattern $pattern | ForEach-Object {
    $m = $_.Matches[0].Groups
    $m[1].Value.ToUpper().PadRight(6) + ' /api/v1' + $m[2].Value
}
foreach ($r in $routes) { $sb.AppendLine('- ' + $r) | Out-Null }
$sb.AppendLine('') | Out-Null

$sb.AppendLine('## MCP surface') | Out-Null
$sb.AppendLine('') | Out-Null
$sb.AppendLine('- Tools (portmanteau, default mode): resolve_project, resolve_media, resolve_timeline,') | Out-Null
$sb.AppendLine('  resolve_color, resolve_render, resolve_audio, resolve_fairlight, resolve_subtitle,') | Out-Null
$sb.AppendLine('  resolve_system (READ-ONLY) - plus help, get_status, shutdown (confirm-gated), 3 agentic tools.') | Out-Null
$sb.AppendLine('- Individual mode (RESOLVE_TOOL_MODE=individual): ~38 single-purpose tools.') | Out-Null
$sb.AppendLine('- Prompts: edit_plan, color_recipe, render_checklist.') | Out-Null
$sb.AppendLine('- Resources: skill://davinci-resolve/skills, resolve://status.') | Out-Null
$sb.AppendLine('- All portmanteau tools carry output_schema + ToolAnnotations; params are Annotated+Field.') | Out-Null
$sb.AppendLine('') | Out-Null

[System.IO.File]::WriteAllText($Out, $sb.ToString(), (New-Object System.Text.UTF8Encoding $false))
$count = $routes.Count
Write-Host "Wrote $Out ($count routes)"
