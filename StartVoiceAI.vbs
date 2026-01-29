' Voice AI Complete Launcher - No Terminal Window
' This script ensures Ollama is running before starting Voice AI
' Double-click to run - completely silent operation

Option Explicit

Dim WshShell, fso, scriptDir, appDir, pythonwPath, ollamaRunning, objWMI, colProcesses, objProcess

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
appDir = scriptDir & "\agent-starter-python"

' Check if Ollama is running
ollamaRunning = False
Set objWMI = GetObject("winmgmts://./root/cimv2")
Set colProcesses = objWMI.ExecQuery("SELECT Name FROM Win32_Process WHERE Name = 'ollama.exe'")
For Each objProcess In colProcesses
    ollamaRunning = True
    Exit For
Next

' Start Ollama if not running
If Not ollamaRunning Then
    WshShell.Run "ollama serve", 0, False  ' 0 = hidden window, False = don't wait
    WScript.Sleep 3000  ' Wait 3 seconds for Ollama to start
End If

' Check if app directory exists
If Not fso.FolderExists(appDir) Then
    MsgBox "Error: Could not find agent-starter-python folder." & vbCrLf & vbCrLf & "Expected at: " & appDir, vbCritical, "Voice AI - Error"
    WScript.Quit 1
End If

' Set working directory
WshShell.CurrentDirectory = appDir

' Check for the EXE first (preferred)
If fso.FileExists(appDir & "\dist\VoiceAI.exe") Then
    WshShell.Run """" & appDir & "\dist\VoiceAI.exe""", 1, False
    WScript.Quit 0
End If

' Fall back to running Python script
' Try to find pythonw.exe (windowless Python)
pythonwPath = ""

' Check user's AppData locations for Python 3.10-3.12
If fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe")) Then
    pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe")
ElseIf fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe")) Then
    pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe")
ElseIf fso.FileExists(WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe")) Then
    pythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe")
ElseIf fso.FileExists("C:\Python312\pythonw.exe") Then
    pythonwPath = "C:\Python312\pythonw.exe"
ElseIf fso.FileExists("C:\Python311\pythonw.exe") Then
    pythonwPath = "C:\Python311\pythonw.exe"
ElseIf fso.FileExists("C:\Python310\pythonw.exe") Then
    pythonwPath = "C:\Python310\pythonw.exe"
End If

' If pythonw.exe found, run the desktop app
If pythonwPath <> "" And fso.FileExists(pythonwPath) Then
    WshShell.Run """" & pythonwPath & """ src\desktop_app.py", 0, False
    WScript.Quit 0
End If

' Last resort: Try pyw command
On Error Resume Next
WshShell.Run "pyw src\desktop_app.py", 0, False
If Err.Number = 0 Then
    WScript.Quit 0
End If
On Error GoTo 0

' Nothing worked - show error
MsgBox "Error: Could not find Python or VoiceAI.exe" & vbCrLf & vbCrLf & _
       "Please ensure Python is installed or build the EXE.", vbCritical, "Voice AI - Error"
WScript.Quit 1
