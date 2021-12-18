# coding: utf8

import os
import time
import subprocess
import platform

# Импорт файлов проекта
import secrets


def runPowershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

errCount = 0
for cred in secrets.winCredentials:
    logOffInfo = runPowershell(
        # $password = ConvertTo-SecureString "p123456" -AsPlainText -Force
        # $Cred = New-Object System.Management.Automation.PSCredential ("domain\user1", $password)
        # ((Get-WmiObject -ComputerName "10.10.10.10" -Class Win32_ComputerSystem).UserName -split "\\")[1]
        f'((Get-WmiObject -ComputerName "172.18.1.126" -Class Win32_ComputerSystem -Credential (New-Object System.Management.Automation.PSCredential ("{cred["user"]}", (ConvertTo-SecureString "{cred["password"]}" -AsPlainText -Force)))).UserName' + r'-split "\\")[1]'
    )
    if logOffInfo.returncode == 0:
        if logOffInfo.stdout == b'':
            print('user logoff')
            userInSystem = False
        else:
            userInSystem = True
            print(logOffInfo.stdout.decode("utf-8"))
    else:
        userInSystem = True
        errCount += 1
        Error = logOffInfo.stderr
if errCount == len(secrets.winCredentials):
    print(Error)

# print(logOffInfo.returncode)
# print(logOffInfo.stdout.decode("utf-8"))

