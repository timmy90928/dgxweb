@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title 網路磁碟機對應

echo ================================================
echo   AILab 網路磁碟機對應
echo ================================================
echo.

rem 清除舊對應
net use * /delete /y >nul 2>&1

rem 預存每台伺服器的唯一憑證（避免 1219）；.247 兩個分享用同一組帳號
cmdkey /delete:140.123.106.219 >nul 2>&1
cmdkey /delete:140.123.106.247 >nul 2>&1
cmdkey /add:140.123.106.219 /user:user     /pass:ailab120 >nul
cmdkey /add:140.123.106.247 /user:dgx_user /pass:w6V2lqW_ >nul

echo.
call :MapDrive "A:" "\\140.123.106.219\ailab"
call :MapDrive "T:" "\\140.123.106.219\temp"
call :MapDrive "X:" "\\140.123.106.247\DGX"
call :MapDrive "W:" "\\140.123.106.247\workspace"

echo.
echo ================================================
echo   目前磁碟機狀態
echo ================================================
net use
echo.
pause
exit /b

:MapDrive
set "_drive=%~1"
set "_unc=%~2"
set "_errfile=%temp%\netuse_err.txt"
net use "%_drive%" "%_unc%" /persistent:yes >nul 2>"%_errfile%"
if !errorlevel! equ 0 (
    echo   [成功]  %_drive%  -^>  %_unc%
) else (
    echo   [失敗]  %_drive%  -^>  %_unc%
    for /f "usebackq delims=" %%E in ("%_errfile%") do echo          %%E
)
del "%_errfile%" >nul 2>&1
exit /b