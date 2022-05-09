import subprocess
import platform
import pymssql
import secrets

SQLServer = '172.19.231.12'

parameter = '-n' if platform.system().lower() == 'windows' else '-c'
command = ['ping', parameter, '1', SQLServer]
response = subprocess.run(command, capture_output=True)

if response.returncode == 0:
    print('True')
else:
    print('False')


try:
    # Создаем соединение с нашей базой данных
    # В нашем примере у нас это просто файл базы
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
    print(cursor.fetchall())
    #print(type([1,'SQL error: {0}']))
    #print(channel[2].split('/')[1])

    # Не забываем закрыть соединение с базой данных
    conn.close()
except pymssql.DatabaseError as err:
    print('SQL error: {0}'.format(err))
