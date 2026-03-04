@echo off
echo ========================================
echo StressSense Build Script (Using Spec Files)
echo ========================================

:: Check if PyInstaller is installed
pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Clean previous builds
echo Cleaning previous builds...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

:: Create logs directory
if not exist "logs" mkdir logs

:: Build main application
echo.
echo Building StressSense main application...
pyinstaller --clean --noconfirm stress_app.spec

:: Build service
echo.
echo Building StressSense service...
pyinstaller --clean --noconfirm stress_detection_service.spec

:: Build service installer
echo.
echo Building service installer utility...
pyinstaller --clean --noconfirm install_service.spec

:: Copy additional files
echo.
echo Copying additional files...
if exist "stress_cnn_model.h5" copy "stress_cnn_model.h5" "dist\"

:: Create installer directory and copy files
echo.
echo Preparing installer files...
if not exist "installer" mkdir installer
xcopy /E /I /Y "dist\*.*" "installer\" >nul 2>&1

:: Check for NSIS and create installer
echo.
echo Checking for NSIS...
set "NSIS_PATH="
if exist "%PROGRAMFILES%\NSIS\makensis.exe" (
    set "NSIS_PATH=%PROGRAMFILES%\NSIS\makensis.exe"
) else (
    if exist "%PROGRAMFILES(x86)%\NSIS\makensis.exe" (
        set "NSIS_PATH=%PROGRAMFILES(x86)%\NSIS\makensis.exe"
    )
)

if "%NSIS_PATH%"=="" (
    echo WARNING: NSIS not found! Skipping installer creation.
    echo Install NSIS from: https://nsis.sourceforge.io/Download
    echo Then run: makensis installer.nsi
) else (
    echo Found NSIS at: %NSIS_PATH%
    echo.
    echo Creating NSIS installer...
    "%NSIS_PATH%" installer.nsi
    if exist "StressSense_Setup.exe" (
        if not exist "release" mkdir release
        move /Y "StressSense_Setup.exe" "release\" >nul 2>&1
        echo Installer created: release\StressSense_Setup.exe
    )
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executables created in 'dist' folder:
echo - StressSense.exe (Main application)
echo - StressDetectionService.exe (Windows service)
echo - install_service.exe (Service installer)
echo.
if exist "release\StressSense_Setup.exe" (
    echo Installer created in 'release' folder:
    echo - StressSense_Setup.exe (Complete installer)
)
echo.
pause