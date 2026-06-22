# One-shot script to initialize this folder as a git repo and push to GitHub.
# Run from PowerShell inside the FinancialRag folder:
#   cd 'C:\Users\mohak\Documents\Codex\rag_regulatory_merged\FinancialRag'
#   .\push_to_github.ps1

$ErrorActionPreference = 'Stop'

Set-Location -Path $PSScriptRoot

Write-Host "==> git init" -ForegroundColor Cyan
git init -b main | Out-Null

Write-Host "==> Setting local git identity (you can change these in .git/config later)"
git config user.name  "Mohak212"
git config user.email "parameshwaran.natarajan@gmail.com"
git config core.autocrlf false
git config core.longpaths true

Write-Host "==> git add ."
git add .

Write-Host "==> git commit"
git commit -m "Initial commit: FinancialRag - RBI/SEBI regulatory RAG system"

Write-Host "==> git remote add origin"
# If a remote already exists this will fail - ignore.
try { git remote remove origin 2>$null } catch {}
git remote add origin "https://github.com/Mohak212/FinancialRag.git"

Write-Host "==> git push -u origin main" -ForegroundColor Cyan
Write-Host "    (You may be prompted for GitHub credentials.)"
git push -u origin main

Write-Host "`nDone! Open https://github.com/Mohak212/FinancialRag" -ForegroundColor Green
