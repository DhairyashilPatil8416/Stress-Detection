; Stress Detection App Installer
; This script creates an installer for the bundled Stress Detection application

!include "MUI2.nsh"

; General Configuration
Name "Stress Detection App"
OutFile "StressDetectionInstaller.exe"
Unicode True
InstallDir "$PROGRAMFILES\Stress Detection"
InstallDirRegKey HKCU "Software\StressDetection" ""
RequestExecutionLevel admin

; Modern UI Configuration
!define MUI_ABORTWARNING
;!define MUI_ICON "icon.ico"
;!define MUI_UNICON "icon.ico"
;!define MUI_HEADERIMAGE
;!define MUI_HEADERIMAGE_BITMAP "icon.ico"
;!define MUI_WELCOMEFINISHPAGE_BITMAP "icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Stress Detection App"
VIAddVersionKey "CompanyName" "Your Company"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "FileDescription" "Stress Detection Application Installer"

; Installer Sections
Section "Stress Detection App" SecApp

  SectionIn RO

  SetOutPath "$INSTDIR"

  ; Copy all files from the bundled app
  File /r "dist\stress_app\*.*"

  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\Stress Detection.lnk" "$INSTDIR\stress_app.exe" "" "$INSTDIR\stress_app.exe" 0

  ; Create start menu entries
  CreateDirectory "$SMPROGRAMS\Stress Detection"
  CreateShortCut "$SMPROGRAMS\Stress Detection\Stress Detection.lnk" "$INSTDIR\stress_app.exe"
  CreateShortCut "$SMPROGRAMS\Stress Detection\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; Registry entries for uninstaller
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "DisplayName" "Stress Detection App"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "Publisher" "Your Company"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "NoRepair" 1

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

; Uninstaller Section
Section "Uninstall"

  ; Remove files
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR"

  ; Remove shortcuts
  Delete "$DESKTOP\Stress Detection.lnk"
  RMDir /r "$SMPROGRAMS\Stress Detection"

  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection"
  DeleteRegKey HKCU "Software\StressDetection"

SectionEnd

; Functions
Function .onInit
  ; Check if already installed
  ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StressDetection" "UninstallString"
  ${If} $R0 != ""
    MessageBox MB_YESNO "Stress Detection App is already installed. Do you want to reinstall?" IDYES continue
    Abort
    continue:
  ${EndIf}
FunctionEnd

Function un.onInit
  MessageBox MB_YESNO "Are you sure you want to uninstall Stress Detection App?" IDYES continue
  Abort
  continue:
FunctionEnd