' Voice AI Launcher - No Terminal Window
' Double-click to run the Voice AI desktop application

Option Explicit

Dim WshShell, fso, scriptDir, appDir, pythonwPath, pythonPath

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
appDir = scriptDir & "\agent-starter-python"

' Check if app directory exists
If Not fso.FolderExists(appDir) Then
    MsgBox "Error: Could not find agent-starter-python folder." & vbCrLf & vbCrLf & "Expected at: " & appDir, vbCritical, "Voice AI - Error"
    WScript.Quit 1
End If

' Set working directory
WshShell.CurrentDirectory = appDir

' Try to find pythonw.exe (windowless Python)
' Check common locations
pythonwPath = ""

' Try py launcher first (most reliable on Windows)
On Error Resume Next
pythonwPath = WshShell.RegRead("HKEY_CURRENT_USER\Software\Python\PythonCore\3.10\InstallPath\ExecutablePath")
If pythonwPath <> "" Then pythonwPath = fso.GetParentFolderName(pythonwPath) & "\pythonw.exe"
On Error GoTo 0

' Check user's AppData locations
If pythonwPath = "" Or Not fso.FileExists(pythonwPath) Then
    If fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe")) Then
        pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe")
    ElseIf fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe")) Then
        pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe")
    ElseIf fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe")) Then
        pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe")
    ElseIf fso.FileExists("C:\Python310\pythonw.exe") Then
        pythonwPath = "C:\Python310\pythonw.exe"
    ElseIf fso.FileExists("C:\Python311\pythonw.exe") Then
        pythonwPath = "C:\Python311\pythonw.exe"
    ElseIf fso.FileExists("C:\Python312\pythonw.exe") Then
        pythonwPath = "C:\Python312\pythonw.exe"
    End If
End If

' If pythonw not found, try using pyw.exe (Python launcher for Windows)
If pythonwPath = "" Or Not fso.FileExists(pythonwPath) Then
    If fso.FileExists(WshShell.ExpandEnvironmentStrings("%WINDIR%\pyw.exe")) Then
        pythonwPath = WshShell.ExpandEnvironmentStrings("%WINDIR%\pyw.exe")
    ElseIf fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Launcher\pyw.exe")) Then
        pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Launcher\pyw.exe")
    End If
End If

' Last resort - try to find pythonw in PATH
If pythonwPath = "" Or Not fso.FileExists(pythonwPath) Then
    pythonwPath = "pythonw"
End If

' Run the desktop app (0 = hidden window, False = don't wait)
On Error Resume Next
WshShell.Run """" & pythonwPath & """ src\desktop_app.py", 0, False

If Err.Number <> 0 Then
    MsgBox "Error starting Voice AI:" & vbCrLf & vbCrLf & Err.Description & vbCrLf & vbCrLf & "Make sure Python is installed.", vbCritical, "Voice AI - Error"
End If
On Error GoTo 0

Set fso = Nothing
Set WshShell = Nothing
