@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "GODOT="

for %%G in (
  Godot_v4.7.2-stable_win64_console.exe
  Godot_v4.7.2-stable_win64.exe
  godot4.exe
  godot.exe
) do (
  if exist "%%G" if not defined GODOT set "GODOT=%%G"
)

if not defined GODOT where godot4.exe >nul 2>nul && set "GODOT=godot4.exe"
if not defined GODOT where godot.exe >nul 2>nul && set "GODOT=godot.exe"

rem Common Godot ZIP extraction layout under Downloads (console preferred).
if not defined GODOT for /f "delims=" %%G in ('dir /b /s "%USERPROFILE%\Downloads\Godot*_console.exe" 2^>nul') do if not defined GODOT set "GODOT=%%G"
if not defined GODOT for /f "delims=" %%G in ('dir /b /s "%USERPROFILE%\Downloads\Godot*.exe" 2^>nul') do if not defined GODOT set "GODOT=%%G"

if not defined GODOT (
  echo [NG] Godot 4 executable was not found.
  echo Put Godot 4.7.2 in this folder, on PATH, or under Downloads, then run this file again.
  exit /b 10
)

echo [INFO] Godot: %GODOT%
echo [1/2] Godot parser/editor startup check...
"%GODOT%" --headless --editor --quit --path "%CD%"
if errorlevel 1 (
  echo [NG] Godot parser/editor startup failed.
  exit /b %errorlevel%
)

echo [2/2] SHINOBI non-destructive regression...
"%GODOT%" --headless --path "%CD%" -- --shinobi-regression
if errorlevel 1 (
  echo [NG] Regression failed.
  exit /b %errorlevel%
)

echo [PASS] Godot preflight completed.
exit /b 0
