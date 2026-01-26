Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\agent-starter-python"
WshShell.Run """C:\Users\maxwe\AppData\Local\Programs\Python\Python310\pythonw.exe"" src/desktop_app.py", 0, False
