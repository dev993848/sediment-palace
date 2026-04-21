@echo off
setlocal EnableDelayedExpansion

if not "%~1"=="" goto run_direct

set "agent_codex=1"
set "agent_opencode=0"
set "agent_qwen=0"
set "agent_kimi=0"
set "agent_claude=0"

:menu
cls
echo ============================================
echo   SedimentPalace Memory Init
echo ============================================
echo.
call :print_agent 1 codex    !agent_codex!
call :print_agent 2 opencode !agent_opencode!
call :print_agent 3 qwen     !agent_qwen!
call :print_agent 4 kimi     !agent_kimi!
call :print_agent 5 claude   !agent_claude!
echo.
echo Enter 1-5 to toggle agent.
echo S - start, Q - quit.
set /p "choice=> "

if /I "!choice!"=="Q" goto end
if /I "!choice!"=="S" goto ask_workspace
if "!choice!"=="1" call :toggle agent_codex
if "!choice!"=="2" call :toggle agent_opencode
if "!choice!"=="3" call :toggle agent_qwen
if "!choice!"=="4" call :toggle agent_kimi
if "!choice!"=="5" call :toggle agent_claude
goto menu

:ask_workspace
set "agents="
call :append_agent codex !agent_codex!
call :append_agent opencode !agent_opencode!
call :append_agent qwen !agent_qwen!
call :append_agent kimi !agent_kimi!
call :append_agent claude !agent_claude!

if "!agents!"=="" (
  echo.
  echo No agents selected.
  pause
  goto menu
)

set "workspace=%cd%"
echo.
set /p "workspace_input=Workspace path [%cd%]: "
if not "!workspace_input!"=="" set "workspace=!workspace_input!"

echo.
echo Running: python "%~dp0init_memory.py" --workspace "!workspace!" --agents !agents!
python "%~dp0init_memory.py" --workspace "!workspace!" --agents !agents!
set "rc=%errorlevel%"
echo.
if "!rc!"=="0" (
  echo STATUS: SUCCESS
) else (
  echo STATUS: FAILED ^(exit code !rc!^)
)
pause
goto end

:run_direct
python "%~dp0init_memory.py" %*
set "rc=%errorlevel%"
echo.
if "%rc%"=="0" (
  echo STATUS: SUCCESS
) else (
  echo STATUS: FAILED ^(exit code %rc%^)
)
pause
goto end

:toggle
set "name=%~1"
if "!%name%!"=="1" (
  set "%name%=0"
) else (
  set "%name%=1"
)
exit /b 0

:append_agent
set "name=%~1"
set "enabled=%~2"
if "%enabled%"=="1" (
  if defined agents (
    set "agents=!agents!,%name%"
  ) else (
    set "agents=%name%"
  )
)
exit /b 0

:print_agent
set "idx=%~1"
set "name=%~2"
set "enabled=%~3"
set "mark=[ ]"
if "%enabled%"=="1" set "mark=[x]"
echo %idx%. %mark% %name%
exit /b 0

:end
endlocal

