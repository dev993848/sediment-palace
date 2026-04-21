param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ArgsList
)

$scriptPath = Join-Path $PSScriptRoot "init_memory.py"
python $scriptPath @ArgsList
