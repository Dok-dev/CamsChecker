import subprocess
import platform

def runPowershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

def pingGood(host):
    parameter = '-n' if platform.system().lower() == 'windows' else '-c'

    command = ['ping', parameter, '1', host]
    response = subprocess.run(command, capture_output=True)

    if response.returncode == 0:
        return True
    else:
        return False


print(pingGood('172.27.68.107'))
