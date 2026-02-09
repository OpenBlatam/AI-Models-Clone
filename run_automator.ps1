param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
  Write-Error 'pip not found. Ensure Python is installed and added to PATH.'
}

pip install -r requirements-automator.txt | Out-Null

python -3 cursor_automator.py @Args


