import logging
import re
import paramiko
import os
from dotenv import load_dotenv

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import psycopg2
from psycopg2 import Error

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding='utf-8'
)

logger = logging.getLogger(__name__)


def SshCreateConnection():
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username, password=password, port=port)
    except Exception as e:
        logging.error(e)
        return None
    return client


def DbCreateConnection():
    connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv('DB_PASSWORD'),
                                    host=os.getenv('DB_HOST'),
                                    port=os.getenv('DB_PORT'), 
                                    database=os.getenv('DB_DATABASE'))

    cursor = connection.cursor()
    return connection, cursor


def SshExecCommand(client, command):
    if client == None:
        logging.error('Ошибка выполнения команды на удаленном сервере')
        return 'Не удалось соединиться с удаленным сервером'
        
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


def DbExecSelectCommand(command):  
    try:
        connection, cursor = DbCreateConnection()
        cursor.execute(command)
        res = cursor.fetchall()
        data = '' # Создаем строку, в которую будем записывать данные
        
        for row in res:
            data += f'{row[0]}. {row[1]}\n' # Записываем красивый вывод --  id. данные

        logging.info(f"Команда {command} успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        return data


def DbExecInsertCommand(command):  
    try:
        connection, cursor = DbCreateConnection()
        cursor.execute(command)
        connection.commit()

        logging.info(f"Команда {command} успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        return 

def start(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /start')
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}!')


def helpCommand(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /help')
    update.message.reply_text(' Что умееет этот бот:\n\n' +
                            '/help - Вывод инормации о командах\n' +
                            '/find_phone_number - Выделить номера телефонов из текста\n' +
                            '/find_email - Выделить email из текса\n' +
                            '/verify_password - Проверить сложность пароля\n' +
                            '/get_release - Мониторинг Linux-системы. Выводит информацию о релизе Linux системы на удаленном сервере\n' +
                            '/get_uname - Мониторинг Linux-системы. Выводит информацию об архитектуры процессора, имени хоста системы и версии ядра\n' +
                            '/get_uptime - Мониторинг Linux-системы. Выводит информацию о времени работы\n' +
                            '/get_df - Мониторинг Linux-системы. Выводит информацию о состоянии файловой системы\n'+
                            '/get_free - Мониторинг Linux-системы. Выводит информацию о состоянии оперативной памяти\n' +
                            '/get_mpstat - Мониторинг Linux-системы. Выводит информацию о производительности системы\n' +
                            '/get_w - Мониторинг Linux-системы. Выводит информацию о работающих в данной системе пользователях\n' +
                            '/get_auths - Мониторинг Linux-системы. Выводит последние 10 входов в систему\n' +
                            '/get_critical - Мониторинг Linux-системы. Выводит последние 5 критических события\n' +
                            '/get_ps - Мониторинг Linux-системы. Выводит информацию о запущенных процессах\n' +
                            '/get_ss - Мониторинг Linux-системы. Выводит информацию об используемых портах\n' +
                            '/get_apt_list - Мониторинг Linux-системы. Выводит информацию об установленных пакетах\n' +
                            '/get_services - Мониторинг Linux-системы. Выводит информацию о запущенных сервисах\n' +
                            '/get_repl_logs - Вывести логи репликации\n' +
                            '/get_emails - Вывести сохраненные email\n' +
                            '/get_phone_numbers - Вывести сохраненные номера '    )


def findPhoneNumbersCommand(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /find_phone_number')
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findEmailsCommand(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /find_email')
    update.message.reply_text('Введите текст для поиска email: ')

    return 'findEmails'


def verifyPasswordCommand(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /verify_password')
    update.message.reply_text('Введите ваш пароль для проверки: ')

    return 'verifyPassword'


def getAptListCommand(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_apt_list_command')
    update.message.reply_text('Введите название пакета, для вывода информации о нем. Для вывода информации о всех пакетах введите "все": ')

    return 'getAptList'


def getRelease(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_release')
    client = SshCreateConnection()
    data = SshExecCommand(client, 'lsb_release -a')

    update.message.reply_text("Информация о релизе:\n\n" + data)
    return ConversationHandler.END


def getUname(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_uname')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'uname -a')

    update.message.reply_text("Информация об архитектуре процессора, имени хоста системы и версии ядра:\n\n" + data)
    return ConversationHandler.END


def getUptime(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_uptime')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'uptime -p')

    update.message.reply_text("Информация о времени работы:\n\n" + data)
    return ConversationHandler.END


def getDf(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_df')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'df -h')
    
    update.message.reply_text("Информация о состоянии файловой системы:\n\n" + data)
    return ConversationHandler.END


def getFree(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_free')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'free -h')
    
    update.message.reply_text("Информация о состоянии оперативной памяти:\n\n" + data)
    return ConversationHandler.END


def getMpstat(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_mpstat')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'mpstat')
    
    update.message.reply_text("Информация о производительности системы:\n\n" + data)
    return ConversationHandler.END


def getW(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_w')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'w')
    
    update.message.reply_text("Информация о работающих в данной системе пользователях:\n\n" + data)
    return ConversationHandler.END


def getAuths(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_auths')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'last -10')
    
    update.message.reply_text("Логи c последними 10 входами в систему:\n\n" + data)
    return ConversationHandler.END


def getCritical(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_critical')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'journalctl --priority 2 -n5') # level 2 - critical conditions
    
    update.message.reply_text("Логи с последними 5 критическими событиями (возможно пусто):\n\n" + data)
    return ConversationHandler.END


def getPs(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_ps')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'ps -A | tail')
    
    update.message.reply_text("Информация о запущеных процессах (последние 10):\n\n" +data)
    return ConversationHandler.END


def getSs(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_ss')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'ss -tlpn')
    
    update.message.reply_text("Информация об используемых портах:\n\n" + data)
    return ConversationHandler.END


def getServices(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_services')

    client = SshCreateConnection()
    data = SshExecCommand(client, 'systemctl list-units --type=service --state=running')
    
    update.message.reply_text("Информация о запущенных сервисах:\n\n" + data)
    return ConversationHandler.END


def getAptList(update: Update, context):
    user_input = update.message.text 
    client = SshCreateConnection()

    if user_input.lower() == 'все' or user_input.lower() == 'all':
        data = SshExecCommand(client, 'dpkg -l | head -n15')
        text = 'Информация о всех установленных пакетах (первые 15):\n\n'
    
    elif re.match(r"^[A-Za-z0-9\-\+\:\.]*$", user_input):
        data = SshExecCommand(client, f'dpkg -l | grep -i {user_input} | head -n10')
        text = f'Информация о найденных пакетах {user_input}:\n\n'
    else:
        update.message.reply_text('Неверное название пакета')
        return ConversationHandler.END

    update.message.reply_text(text + data)
    return ConversationHandler.END


def getReplLogs(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_repl_logs')
    path = '/var/log/postgresql/postgres.log'
    file = open(path)
    logs = ''
    data = file.readlines()[-20::]
    for line in data:
        if 'repl' in line:
            logs += line
    
    update.message.reply_text("Логи о репликации:\n\n" + logs)
    return ConversationHandler.END


def getEmails(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_emails')
    
    data = DbExecSelectCommand('SELECT * FROM email_addresses;')

    update.message.reply_text("Сохраненные email адреса:\n\n" + str(data))
    return ConversationHandler.END


def getPhoneNumbers(update: Update, context):
    logging.info(f'Пользователь {update.effective_user.full_name} ввел команду /get_phone_numbers')
    
    data = DbExecSelectCommand('SELECT * FROM phone_numbers;')

    update.message.reply_text("Сохраненные телефонные номера:\n\n" + str(data))
    return ConversationHandler.END


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:8|\+7)[\- ]?\(?\d{3}\)?[\- ]?\d{3}[\- ]?\d{2}[\- ]?\d{2}') 
                        
    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END# Завершаем выполнение функции
    
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        if phoneNumberList[i] not in phoneNumbers:
            phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text('Найденные номера:\n\n' + phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text('Записать найденные номера?')
    context.user_data['numbers'] = phoneNumberList
    return 'addPhoneNumbers'


def findEmails (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email

    emailRegex = re.compile(r'[A-Za-z0-9\_\-\.]+@[a-zA-Z0-9\.\_\-]+\.[A-Za-z\_\-]{2,}') # 
                        
    emailList = emailRegex.findall(user_input) # Ищем email

    if not emailList: # Обрабатываем случай, когда email нет
        update.message.reply_text('email не найдены')
        return ConversationHandler.END # Завершаем диалог
    
    emails = '' # Создаем строку, в которую будем записывать email
    for i in range(len(emailList)):
        if emailList[i] not in emails:
            emails += f'{i+1}. {emailList[i]}\n' # Записываем очередной email
        
    update.message.reply_text('Найденные email:\n\n' + emails) # Отправляем сообщение пользователю
    update.message.reply_text('Записать найденные email\'ы?')
    context.user_data['emails'] = emailList
    return 'addEmails'
    

def addEmails(update: Update, context):
    answer = update.message.text
    data = context.user_data["emails"]
    if answer.lower() == 'yes' or answer.lower() == 'да':
        for i in range(len(data)):
            res = DbExecInsertCommand(f"INSERT INTO email_addresses (email) VALUES ('{data[i]}');")
        update.message.reply_text('Данные успешно записаны!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Данные не будут записаны')
        return ConversationHandler.END
    

def addPhoneNumbers(update: Update, context):
    answer = update.message.text
    data = context.user_data["numbers"]
    if answer.lower() == 'yes' or answer.lower() == 'да':
        for i in range(len(data)):
            res = DbExecInsertCommand(f"INSERT INTO phone_numbers (number) VALUES ('{data[i]}');")
        update.message.reply_text('Данные успешно записаны!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Данные не будут записаны')
        return ConversationHandler.END


def verifyPassword (update: Update, context):
    user_input = update.message.text # Получаем текст

    strongPasswordRegex = re.compile(r'(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}') # 
                        
    password = strongPasswordRegex.match(user_input)
    
    if (password == None): # Обрабатываем случай, когда email нет
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END# Завершаем выполнение функции

    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'addPhoneNumbers' : [MessageHandler(Filters.text & ~Filters.command, addPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'addEmails' : [MessageHandler(Filters.text & ~Filters.command, addEmails)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList= ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'getAptList': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )


		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbers))
    

		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
