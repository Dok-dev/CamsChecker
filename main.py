# coding: utf8
# CamsFilesCheck v 0.9 beta
# author Timofey Biryukov

import os
import time
import smtplib
import subprocess
import pymssql
# import pyodbc
import platform

# Импорт файлов проекта
import secrets


def getChannels(SQLServer):
    """
    Get channels info from server
    """
    try:
        # Создаем соединение с нашей базой данных
        conn = pymssql.connect(server=SQLServer + r'\SQLEXPRESS', database='tvm_conf', user=secrets.sqlUser, password=secrets.sqlPass)

        # Создаем курсор - это специальный объект который делает запросы и получает их результаты
        cursor = conn.cursor()

        if 'police1' in SQLServer.lower():
            cursor.execute("""  SELECT [tvm_conf].[dbo].[Channels].[id],[tvm_conf].[dbo].[Channels].[name],[storage_path] as path,[host],[role]
                                    FROM [tvm_conf].[dbo].[Channels]
                                    LEFT JOIN [tvm_conf].[dbo].[ChannelStorage]
                                    ON [tvm_conf].[dbo].[Channels].[id] = [tvm_conf].[dbo].[ChannelStorage].[channel]
                                    LEFT JOIN [tvm_conf].[dbo].[ChannelIngest]
                                    ON [tvm_conf].[dbo].[Channels].[id] = [tvm_conf].[dbo].[ChannelIngest].[channel]
                                    LEFT JOIN [tvm_conf].[dbo].[Servers]
                                    ON [tvm_conf].[dbo].[ChannelIngest].[ingest_server] = [tvm_conf].[dbo].[Servers].[id]
                                    LEFT JOIN [tvm_conf].[dbo].[ServerRoles]
                                    ON [tvm_conf].[dbo].[Servers].[id] = [tvm_conf].[dbo].[ServerRoles].[server]
                                WHERE
                                    [role] = (select max([role]) FROM [tvm_conf].[dbo].[ServerRoles]
                                    WHERE [tvm_conf].[dbo].[Servers].[id] = [tvm_conf].[dbo].[ServerRoles].[server])
                                    AND [tvm_conf].[dbo].[ChannelIngest].[ingest_server] != 2
                                    AND [tvm_conf].[dbo].[ChannelStorage].[storage_server] != -1
                                ORDER BY [tvm_conf].[dbo].[Channels].id
                           """)
        else:
            cursor.execute("""  SELECT [tvm_conf].[dbo].[Channels].[id],[tvm_conf].[dbo].[Channels].[name],[path],[host],[role]
                                    FROM [tvm_conf].[dbo].[Channels]
                                    LEFT JOIN [tvm_conf].[dbo].[Servers]
                                    ON [tvm_conf].[dbo].[Channels].[server] = [tvm_conf].[dbo].[Servers].[id]
                                    LEFT JOIN [tvm_conf].[dbo].[ServerRoles]
                                    ON [tvm_conf].[dbo].[Servers].[id] = [tvm_conf].[dbo].[ServerRoles].[server]
                                WHERE
                                    [role] = (SELECT MAX([role]) FROM [tvm_conf].[dbo].[ServerRoles]
                                    WHERE
                                        [tvm_conf].[dbo].[Servers].[id] = [tvm_conf].[dbo].[ServerRoles].[server])
                                ORDER BY [tvm_conf].[dbo].[Channels].id
                           """)

        return cursor.fetchall()
        # Не забываем закрыть соединение с базой данных
        conn.close()
    except pymssql.DatabaseError as err:
        print('SQL error: {0}'.format(err))
        return [0,'SQL error: {0}'.format(err)]


def send_email(subject, body_text):
    """
    Send an email
    """

    BODY = "\r\n".join((
        "From: %s" % secrets.from_addr,
        "To: %s" % secrets.to_addr,
        "Subject: %s" % subject,
        "",
        body_text
    ))

    SMTPserver = smtplib.SMTP(secrets.SMTPrelay, secrets.port)
    SMTPserver.sendmail(secrets.from_addr, [secrets.to_addr], BODY.encode("utf8"))
    SMTPserver.quit()



def newestFileTime(path):
    """
    Get newest file in folder
    Функция возвращает время изменения самого свежего файла
    """
    try:
        files = os.listdir(path)
        if len(files) > 0:
            paths = [os.path.join(path, basename) for basename in files]
            newestFile = max(paths, key=os.path.getctime)
            # т.к. файл открытый нужно тоже его открыть и запросить размер с помощью fstat
            a = open(newestFile)
            RealFileSize = os.fstat(a.fileno()).st_size
            #    subprocess.call(f'powershell.exe (Get-Item "{newestFile}").length', shell=True)
            #    return time.ctime(os.path.getmtime(newestFile))
            return [os.path.getmtime(newestFile), RealFileSize, '']
        else:
            return [0, 0, '']
    except OSError as err:
        print('OS error: {0}'.format(err))
        return [0, 0, 'OS error: {0}'.format(err)]


def runPowershell(cmd):
    """
    Run powershell cmdlet as one line
    """
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def pingGood(host):
    """
    Check ping-echo answer
    """
    parameter = '-n' if platform.system().lower() == 'windows' else '-c'

    command = ['ping', parameter, '1', host]
    response = subprocess.run(command, capture_output=True)

    if response.returncode == 0:
        return True
    else:
        return False

def userInSystem(host):
    errCount = 0
    error = ''
    for cred in secrets.winCredentials:
        logOffInfo = runPowershell(
            f'((Get-WmiObject -ComputerName "{host}" -Class Win32_ComputerSystem -Credential (New-Object System.Management.Automation.PSCredential ("{cred["user"]}", (ConvertTo-SecureString "{cred["password"]}" -AsPlainText -Force)))).UserName' + r'-split "\\")[1]'
        )
        if (logOffInfo.returncode == 0) and logOffInfo.stderr == b'':
            if logOffInfo.stdout == b'':
                print(f'{host} on is logged off.')
                return [False, '']
            else:
                return [True, '']
        else:
            errCount += 1
            error = logOffInfo.stderr
    if errCount == len(secrets.winCredentials):
        print(error)
        return [True, error]
    else:
        return [True, '']


# Если время суточного отчета выставояем тригер для его формирования
if time.localtime(time.time()).tm_hour == 8:
    dailyReport = True
    daily_email_body = ''
else:
    dailyReport = False

print('Файлы каналов нуждающиеся в дополнительной проверке:')
print('|         изменен        |            путь                   |           размер')


for policeServer in secrets.servers:
    serverChannels = getChannels(policeServer['url'])
    if serverChannels[0] == 0:
        email_subject = f'SQL error on reading channels {policeServer["name"]}!'
        email_body = (serverChannels[1])
        send_email(email_subject, email_body)
    else:

        if os.path.exists(policeServer['path']):
            print(f'проверка {policeServer["name"]}...')
            # channels = os.listdir(server['path'])
            for channel in serverChannels:
                # Получаем папку канала и проверяем правильность ее настройки.
                if channel[2] != '':
                    try:
                        FilesPath = os.path.join(policeServer['path'], channel[2].split('/')[1])
                    except IndexError as err:
                        print(f'Неправильный путь в настройках канала {channel[1]}')
                        email_subject = f'Error path on channel {channel[1]}, {policeServer["name"]}!'
                        email_body = f'Неправильный путь (возможно default) в настройках канала {channel[1]} на {policeServer["name"]}.'
                        FilesPath = os.path.join(policeServer['path'], channel[2])
                # Проверяем существование полученного пути.
                if os.path.isdir(FilesPath):
                    # получаем данные по файлу из функции в лист NewestFileData
                    NewestFileData = newestFileTime(FilesPath)
                    # проверяем нет ли ошибок чтения
                    if NewestFileData[2] == '':
                        NewestFileTimeInChanel = NewestFileData[0]
                        FileSize = NewestFileData[1]

                        # проверяем за текущий час разницу времени и время изменения
                        if (NewestFileTimeInChanel != 0) and (7200 > (int(time.time()) - NewestFileTimeInChanel) > 60):
                            time.sleep(6)
                            # Повторная провекка через 6 сек.
                            if newestFileTime(FilesPath)[1] == FileSize:
                                email_subject = f'Stop recording channel {channel[1]} on {policeServer["name"]}!'
                                email_body = (
                                                f'Проверьте канал {channel[1]} на {policeServer["name"]}. Файл перестал расти.' +
                                                '\n\nвремя последнего изменения по метке: ' + time.ctime(NewestFileTimeInChanel) +
                                                '\n\nтекущий размер файла: ' + str(round(FileSize / (1024 * 1024), 2)) + 'Мб'
                                            )
                                # Если канал является скринкастом
                                if channel[4] == 1:
                                    # Проверяем включен ли комп
                                    if pingGood(channel[3]):
                                        # Проверяем залогинен ли пользователь в систему
                                        logon = (userInSystem(channel[3]))
                                        if logon[1] != '':
                                            email_body += f' - Ошибка при попытке проверки пользователя в системе на {channel[3]} ({policeServer["name"]}): \n\{logon[1]}'
                                            send_email(email_subject, email_body)
                                            print(time.ctime(NewestFileTimeInChanel), ' ', FilesPath, '      ', round(FileSize / (1024 * 1024), 1), 'Мб')
                                        else:
                                            if not logon[0]:
                                                print(f'{channel[3]} on {policeServer["name"]} is logged off.')
                                    else:
                                        email_subject = f'{channel[3]} on {policeServer["name"]} is shutdown or inaccessible.'
                                        email_body = (f'Хост {channel[3]} канала {channel[1]} на {policeServer["name"]} был выключен или стал недоступен.' +
                                                     '\n\nДанное сообщение являтся информационным.')
                                        print(f'{channel[3]} on {policeServer["name"]} is shutdown or inaccessible.')
                                else:
                                    print(time.ctime(NewestFileTimeInChanel), ' ', FilesPath, '      ', round(FileSize / (1024 * 1024), 1), 'Мб')
                                    send_email(email_subject, email_body)

                    else:
                        email_subject = f'File reading problem on channel {channel[1]} on {policeServer["name"]}!'
                        email_body = (f'Проверьте канал {channel[1]} на {policeServer["name"]}. Файл недоступен.' +
                                      NewestFileData[2])
                        send_email(email_subject, email_body)

                    # набираем строки для письма с отчетом за сутки
                    if dailyReport:
                        # проверяем нет ли ошибок чтения
                        if NewestFileData[2] == '':
                            # проверяем разницу текущего времени и изменения файла
                            if (NewestFileTimeInChanel != 0) and (86400 > (int(time.time()) - NewestFileTimeInChanel) > 60):
                                time.sleep(6)
                                if newestFileTime(FilesPath)[1] <= FileSize:
                                    print(time.ctime(NewestFileTimeInChanel), ' ', FilesPath, '      ',
                                          round(FileSize / (1024 * 1024), 1), 'Мб')
                                    # Если канал является скринкастом
                                    if channel[4] == 1:
                                        # Проверяем включен ли комп
                                        if pingGood(channel[3]):
                                            # Проверяем залогинен ли пользователь в систему
                                            logon = (userInSystem(channel[3]))
                                            if logon[1] != '':
                                                daily_email_body += f'Ошибка при попытке проверки пользователя в системе на {channel[3]} ({policeServer["name"]}): \n\{logon[1]}'
                                            else:
                                                if not logon[0]:
                                                    print(f'{channel[3]} on {policeServer["name"]} is logged off.')
                                                    daily_email_body += f'Канал {channel[1]}(хост {channel[3]}) на {policeServer["name"]} - не обновляется т.к. в системе нет пользователя.'
                                                else:
                                                    daily_email_body += f'{channel[1]} на {policeServer["name"]} - не обновляется.'
                                        else:
                                            daily_email_body += f'Хост {channel[3]} канала {channel[1]} на {policeServer["name"]} выключен или недоступен.'
                                    else:
                                        daily_email_body += f'{channel[1]} на {policeServer["name"]} - не обновляется.'

                                    daily_email_body += (' | время последнего изменения по метке: ' +
                                                         time.ctime(NewestFileTimeInChanel) + ' | текущий размер файла: ' +
                                                         str(round(FileSize / (1024 * 1024), 2)) + 'Мб\n\n')
                            # если больше суток то
                            elif 2678400 > (int(time.time()) - NewestFileTimeInChanel) >= 86400:
                                print(time.ctime(NewestFileTimeInChanel), ' ', FilesPath, '  ', 'не пишется более суток')
                                daily_email_body += (f'{channel[1]} на {policeServer["name"]} - не пишется более суток.' +
                                                    ' | время последнего изменения: ' + time.ctime(NewestFileTimeInChanel) +
                                                    ' - таймаут до забытия ' + str(round(30 - (int(time.time()) - NewestFileTimeInChanel) / 86400)) + 'дн.\n\n')
                        else:
                            daily_email_body += (
                                    f'{channel[1]} на {policeServer["name"]} - ошибка открытия -' + NewestFileData[2])
        else:
            print(f'Storage {policeServer["path"]} unavailable or does not exist!')
            email_subject = f'Storage {policeServer["path"]} unavailable or does not exist!'
            email_body = (f'Storage {policeServer["path"]} unavailable or does not exist!')
            send_email(email_subject, email_body)

if dailyReport:
    email_subject = 'Суточный отчет по файлам каналов полиции.'
    if daily_email_body == '':
        daily_email_body = 'Проблемные каналы отсутствуют.'
    send_email(email_subject, daily_email_body)

print('\n Records verification completed')
# print('\n Type ENTER for close')
# input()
