print("Step 1. Importing")
import pandas as pd
import vk_api, random, json, sys
from time import sleep
from pymorphy2 import MorphAnalyzer
from RoleTree import Students


print("Step 2. Connecting")

# TO_DO: Прицепить методичку в ветке методичка старосты

morph = MorphAnalyzer()    # Обработка слов на русском языке
alf = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя ")
dct = open("syn.txt", "r", encoding="utf-8").read().split("\n")
bad_words = open("bad_words.txt", "r", encoding="utf-8").read().split("\n")
frmt_dct = []
for txt in dct:                         # ???
    frmt_dct.append(txt.split("|"))     # ???
del dct
print("Dictionary has been analyzed")
run_for_all = True
run_for_admin = False
KEY = "эхо"

vk = vk_api.VkApi(token="4da22115eb7502da463a8b0e5a677bac474a8a9e10339d16000817efe052163924a57ba95c31e833b4216")
vk._auth_token()

print("Step 3. All stuff goes here...")

def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


kb_otm = {
    "one_time": True,
    "buttons": [[get_button(label="Отмена", color="negative")]]
}

kb_otm = json.dumps(kb_otm, ensure_ascii=False).encode('utf-8')
kb_otm = str(kb_otm.decode('utf-8'))

kb_vyh = {
    "one_time": True,
    "buttons": [[get_button(label="Выход", color="negative")]]
}

kb_vyh = json.dumps(kb_vyh, ensure_ascii=False).encode('utf-8')
kb_vyh = str(kb_vyh.decode('utf-8'))

kb_vyh_otm = {
    "one_time": True,
    "buttons": [[get_button(label="Отмена", color="default"), get_button(label="Выход", color="negative")]]
}

kb_vyh_otm = json.dumps(kb_vyh_otm, ensure_ascii=False).encode('utf-8')
kb_vyh_otm = str(kb_vyh_otm.decode('utf-8'))

kb_main = {
    "one_time": False,
    "buttons": [[get_button(label="Меню", color="primary"), get_button(label="Поиск", color="default"), \
    get_button(label="Библиотека", color="default")]]
}

kb_main = json.dumps(kb_main, ensure_ascii=False).encode('utf-8')
kb_main = str(kb_main.decode('utf-8'))

kb_star = {
    "one_time": False,
    "buttons": [[get_button(label="Меню", color="primary"), get_button(label="Поиск", color="default"), \
    get_button(label="Библиотека", color="default"), get_button(label="Методичка для старосты", color="primary")]]
}

kb_star = json.dumps(kb_star, ensure_ascii=False).encode('utf-8')
kb_star = str(kb_star.decode('utf-8'))

''' Создание списка кнопок

    Возможные варианты Tree_Role:
    RoleTree.Students
    RoleTree.Teachers
    RoleTree.Staff
'''
# def TreeKeyboard(Tree_Role):
btns = []
for wrd in list(Students):   # Вместо Students вставить RoleTree.Students и т.д.
    knpk = [get_button(label=wrd, color="default")]
    btns.append(knpk)
nd = [get_button(label="Выход", color="negative")]
btns.append(nd)
kb_dikk = {
    "one_time": True,
    "buttons": btns
}

kb_dikk = json.dumps(kb_dikk, ensure_ascii=False).encode('utf-8')
kb_dikk = str(kb_dikk.decode('utf-8'))
# return kb_dikk

''' Работа со словарем '''
def UpdateTxtFile(file, headers, bodies, formated_headers):
    """
    file - обрабатываемый файл
    headers - заголовки
    bodies - текст заголовка
    formated_headers - форматированные заголовки
    """
    all_txt = open(file, encoding='utf-8').read().split("\n" + "===" + "\n"*2)
    # print(all_txt)
    frmt_txt = []
    for txt in all_txt:
        frmt_txt.append(txt.split("\n---\n"))
    # print(frmt_txt)
    # all_txt.close()
    for txt in frmt_txt:
        headers.append(txt[0])
        bodies.append(txt[1])
    for wrds in headers:
        formated_headers += [MorpH(wrds)]

''' Отправка сообщений пользователю '''
def SendMessage(id, message, keyboard=kb_main):
    vk.method("messages.send",
              {"peer_id": id, "message": message, "keyboard": keyboard, "random_id": random.randint(1, 2147483647)})

def SendMessage2(id, message, keyboard, type, owner_id, media_id): #type - тип вложения[photo, video, audio, doc, wall, market(товар), poll(опрос)]
    vk.method("messages.send",
            {"peer_id": id, "message": message, "keyboard": keyboard, "random_id": random.randint(1, 2147483647), "attachment": type+owner_id+"_"+media_id})

''' Формирование списка обработанных слов из введеной строки '''
def MorpH(words):
    words = words.lower()  # Нижний регистр
    words = list(words) # Преобразование в лист букв
    for i in words:
        tf = []
        for k in alf:
            tf.append([i == k])

        if not (any(i == [True] for i in tf)):
            words.remove(i)
    frmt_words = ""

    for wrd in words:
        frmt_words += wrd
    frmt_words = frmt_words.split(" ")

    for i in range(len(frmt_words)):
        frmt_words[i] = morph.parse(frmt_words[i])[0].normal_form

    for frmt_wrd in frmt_words:
        for bd_wrd in bad_words:
            if frmt_wrd == bd_wrd:
                try:
                    frmt_words.remove(bd_wrd)
                except:
                    pass
    return frmt_words

def CheckID(id):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result = df[df["id"] == id]
    if len(result) == 0:
        user_info = vk.method("users.get",
                              {"user_ids": id, "fields": "first_name, last_name, sex"})
        user_id = user_info[0]["id"]
        user_name = user_info[0]["first_name"]
        user_surname = user_info[0]["last_name"]
        user_sex = user_info[0]["sex"]
        df = df.append({"id": user_id,
                        "Name": user_name,
                        "Surname": user_surname,
                        "Sex": user_sex,
                        "Role": 0,
                        "Subscription": 1,
                        "Admin": 0,
                        "InAuth": 0,
                        "InAdmAct": 0,
                        "InMakeNews": 0,
                        "InMakeMnl": 0,
                        "InPy": 0,
                        "InSearch": 0,
                        "InHelpMenu": 0,
                        "Keys": 0,
                        "InLibrary": 0
                        },

                       ignore_index=True)
        df.to_csv("data.csv", encoding='utf-8', index=False)
        return False
    else:
        return True


def CheckParam(id, param):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result = df[df["id"] == id]
    #df.to_csv("data.csv", index=False, encoding='utf-8')
    if result[param].any():
        return True
    else:
        return False


def SayMyName(id):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result = df[df["id"] == id]
    return result["Name"].values[0]


def SayMySurName(id):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result = df[df["id"] == id]
    return result["Surname"].values[0]

def CheckRole(id):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result = df[df["id"] == id]
    return result["Role"].values[0]

def CheckStarostaKb(id):
	df = pd.read_csv("data.csv", header=0, encoding='utf-8')
	result = df[df["id"] == id]
	if result["Role"].values[0] == 1.5:
		return kb_star
	else:
		return kb_main

def CheckAdmin(id):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result = df[df["id"] == id]
    if result["Admin"].item() == 2:
        return True
    else:
        return False


def SetParam(id, param, k):
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    df.loc[df["id"] == id, param] = k
    df.to_csv("data.csv", index=False, encoding='utf-8')


def InLobby(id):
    if CheckParam(id, "InAuth") == False \
    and CheckParam(id, "InAdmAct") == False \
    and CheckParam(id, "InMakeNews") == False \
    and CheckParam(id, "InMakeMnl") == False \
    and CheckParam(id, "InPy") == False\
    and CheckParam(id, "InSearch") == False\
    and CheckParam(id, "InHelpMenu") == False\
    and CheckParam(id, "InLibrary") == False\
    and CheckParam(id, "InLibSearch") == False:
        return True
    else:
        return False


def BackToLobby(id):
    SetParam(id, "InAuth", 0)
    SetParam(id, "InAdmAct", 0)
    SetParam(id, "InMakeNews", 0)
    SetParam(id, "InMakeMnl", 0)
    SetParam(id, "InPy", 0)
    SetParam(id, "InSearch", 0)
    SetParam(id, "InHelpMenu", 0)
    SetParam(id, "Keys", 0)
    SetParam(id, "InLibrary", 0)
    SetParam(id, "InLibSearch", 0)

def MakeKeyboard(lst):
    btns = []
    for wrd in lst:
        knpk = [get_button(label=wrd, color="default")]
        btns.append(knpk)
    vyh = [get_button(label="Выход", color="negative")]
    btns.append(vyh)
    kb = {
        "one_time": True,
        "buttons": btns
    }

    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))
    return kb

def Menu(id, body):
    """
        key - ветка до выбора
        keys - ветка после выбора

        Сейчас каждый выбранный вариант записывается в файл data.csv
        в формате: ["Выбранный_вариант_1"]["Выбранный_вариант_2"]...   line 305
    """
    df = pd.read_csv("data.csv", header=0, encoding='utf-8')
    result_df = df[df["id"] == id]
    key = result_df["Keys"]
    key = list(key)[0]
    if key == "0" or key == 0:
        key = ""
    keys = key + '["' + body + '"]'
    exec('''
try:
    try:
        # Проверка роли на преподавателя
        if CheckRole(id) == 2:
            result_key = Teachers{0}
            result_keys = Teachers{1}

        # Проверка роли на Дирекцию
        elif CheckRole(id) == 3:
            result_key = Staff{0}
            result_keys = Staff{1}

        else:
            result_key = Students{0}
            result_keys = Students{1}
        F = True
    except Exception as e:
        print(e)
        F = False
        SetParam(id, "Keys", 0)
        SendMessage(id, "Выбран неверный пункт", CheckStarostaKb(id))
    if F == True:
        if len(list(result_keys)[0]) != 1:
            print("key=", key,"keys=", keys)
            SetParam(id, "Keys", keys)
            kb = MakeKeyboard(list(result_keys))
            SendMessage(id, 'Идем дальше', kb)   #Попробовать сделать пустое сообщение-ответ через str()

            # Отправка картинки в случае выбора соответсвующей ветки
            #if keys == \'["Где покушать?"]["Фастфуд"]\':
            #   SendMessage2(id, "", None, "photo", "-4290276", "457375339")

        else:
            # Отправка картинки в случае выбора соответсвующего конечного варианта
            if '["KFC"]' in keys:
                SendMessage2(id, "", None, "photo", "-4290276", "457375339")
            print(key, keys)
            SetParam(id, "Keys", 0)
            BackToLobby(id)
            SendMessage(id, result_keys, CheckStarostaKb(id)) #После конечного ответа возвращает в лобби

except Exception as e:
    SetParam(id, "Keys", 0)
    msg = "vk.com/id" + id + str(e)
    SendMessage(18104211, msg, None)
        '''.format(key, keys))

''' Консоль '''
def Cons():
    try:
        try:
            sys.stdout = open('log.txt', 'w')
            exec(body)
            sys.stdout.close()
            out = open('log.txt').read()
            SendMessage(id, sys.argv[0] + "\n" * 2 + str(out) + "\n\nProcess finished with exit code 0", kb_vyh_otm)
        except Exception as e:
            SendMessage(id,
                        sys.argv[0] + "\n" * 2 + "Error: " + str(e) + "\n\nProcess finished with exit code 1",
                        kb_vyh_otm)
    except Exception as e:
        SendMessage(id, sys.argv[0] + "\n" * 2 + "Error: " + str(e) + "\n\nProcess finished with exit code 1",
                    kb_vyh_otm)


def News(rassylka):
    if rassylka.lower() == "отмена":
        rassylka = ""
        SendMessage(id, "Создание рассылки отменено", kb_vyh)
        SetParam(id, "InMakeNews", 0)
    elif rassylka == "рассылка":
        rassylka = ""
        SendMessage(id, "Введите текст", None)
    else:
        df = pd.read_csv("data.csv", header=0, encoding='utf-8')
        result = df[df["Subscription"] == 1]["id"]
        for usr_id in result:
            try:
                SendMessage(usr_id, rassylka, None)
            except:
                er_msg = "Пользователю " + SayMyName(usr_id) + " " + SayMySurName(usr_id) + " (vk.com/id" + str(
                    usr_id) + ") сообщение не доставлено"
                SendMessage(id, er_msg, None)
        rassylka = ""
        SetParam(id, "InMakeNews", 0)
        SendMessage(id, "Рассылка завершена", kb_vyh)


def MakeText(text):
    text = body
    n = 0
    for i in range(2, len(text)):
        if text[i - 3:i] == "---":
            n += 1
    if len(text) < 5:
        SendMessage(id, "Текст слишком короткий. Впишите текст заново.", kb_vyh_otm)
    elif n != 1:
        SendMessage(id, "Количество разделителей не равно 1. Впишите текст заново.", kb_vyh_otm)
    else:
        file = open("texts.txt", "a", encoding='utf-8')
        file.write(text +"\n" * 1 + "===" + "\n" * 1)
        file.close()
        SendMessage(id, "Текст записан", kb_vyh)
        UpdateTxtFile("texts.txt", TextHeaders, TextBodies, TextFrmtHeaders)
        SetParam(id, "InMakeMnl", 0)

def SendSearchResults(words, bodies, formated_headers):
    """
    words - введеный текст
    bodies - текст заголовков
    formated_headers - форматированные заголовки
    """
    frmt_words = MorpH(words)
    new_words = []
    for wrd in words:  # in frmt_words ?!
        new_words.append(wrd)
    for d_wrds in frmt_dct:
        for f_wrd in frmt_words:
            if d_wrds[0] == f_wrd:
                new_words += d_wrds

    new_words = list(set(new_words))
    for nw_wrd in new_words:
        for bd_wrd in bad_words:
            if nw_wrd == bd_wrd:
                try:
                    new_words.remove(bd_wrd)
                except:
                    pass

    nums = [] # Номера найденных заголовков

    for i in range(len(formated_headers)):
        for nw_wrd in new_words:
            for wrd in formated_headers[i]:
                if wrd == nw_wrd:
                    nums.append(i)
                    break
    print(nums)
    answer = []

    for i in nums:
        answer.append(bodies[i])
    if len(answer) == 0:
        # Если поиск ведется через вкладку "Меню"
        if bodies == TextBodies:
            SendMessage(id, 'По запросу "{}" ничего не нашлось. Ваш запрос будет перенаправлен модераторам. Ожидайте ответа в течение 24 часов'.format(body), kb_vyh)
        # В случае неудачного поиска через "Меню" запрос отправляется модератору; пользователю сообщение о скором ответе в течение 24 часов
            person = SayMyName(id) + ' ' + SayMySurName(id)
            SendMessage(132255549, 'Вот этот человек ->{0}\nПопытался найти какой-то бред: {1}'.format(person, body), None)
        else:
            SendMessage(id, 'По запросу "{}" ничего не нашлось', kb_vyh)
    else:
        if CheckParam(id, "InLibrary"):
            SendMessage(id, "В архиве кое-что есть:", kb_vyh)
        else:
            SendMessage(id, "Результат поиска:", kb_vyh)
        for ans in answer:
            SendMessage(id, ans, None)

def Library():
    with open("library.txt", encoding='utf-8') as lib:
        content = lib.read()
        result = """Добро пожаловать в библиотеку!\n{}""".format(content)
    return result
###
print("Starting...Everything should be fine.")
''' Процесс работы '''
TextHeaders = []
TextBodies = []
TextFrmtHeaders = []
UpdateTxtFile("texts.txt", TextHeaders, TextBodies, TextFrmtHeaders)

BookHeaders = []
BookBodies = []
BookFrmtHeaders = []
UpdateTxtFile("books.txt", BookHeaders, BookBodies, BookFrmtHeaders)
while run_for_all:
    sleep(2)  #Снижение нагрузки путем задержки
    messages = vk.method("messages.getConversations", {"offset": 0, "count": 200, "filter": "unanswered"})
    if messages["count"] >= 1:
        id = messages['items'][0]['last_message']['peer_id']
        body = messages['items'][0]['last_message']['text']

# Выход
        if body.lower() == "выход" and not (InLobby(id)):
            BackToLobby(id)
            SendMessage(id, "Возвращаю в лобби", CheckStarostaKb(id))
# Лобби
        elif InLobby(id):
    # Начать
            if body.lower() == "начать":
                CheckID(id)
                SendMessage(id, "Добро пожаловать. Снова.")
    # Test SendMessage2
            elif body.lower() == "тест":
                CheckID(id)
                SendMessage2(id, "", None, "photo", "-4290276", "457375339")
    # Методичка для старосты
            elif body.lower() == "методичка для старосты":
                CheckID(id)
                if CheckRole(id) == 1.5:
                    SendMessage(id, "Вы нашли \"Методичка для старосты\" x1", kb_star)
                answer = ["Непонятный запрос", "Не знаю такого", "В моей памяти нет такой информации"]
                SendMessage(id, random.choice(answer))
    # Привет
            elif body.lower() == "привет":
                CheckID(id)
                SendMessage(id, "Привет, " + SayMyName(id), CheckStarostaKb(id))
    # Поиск
            elif body.lower() == "поиск":
                CheckID(id)
                SetParam(id, "InSearch", 1)
                SendMessage(id, "Найдется всё! Наверное...\nИтак, что ищем?", kb_vyh)
    # Меню
            elif body.lower() == "меню":
                CheckID(id)
                SetParam(id, "InHelpMenu", 1)
                SendMessage(id, "Наше меню", kb_dikk)
    # Библиотека
            elif body.lower() == "библиотека":
                CheckID(id)
                SetParam(id, "InLibrary", 1)
                kb = MakeKeyboard(["Архив"])
                SendMessage(id, Library(), kb)
            elif body.lower() == "архив":
                CheckID(id)
                SendMessage(id, "Вам следует зайти в библиотеку")
    # Авторизация
            elif body.lower() == "консось" and (CheckParam(id, "Admin") or CheckAdmin(id)):
                SendMessage(id, "Назовите кодовое слово", kb_otm)
                SetParam(id, "InAuth", 1)
    # Заглушка
            else:
                CheckID(id)
                answer = ["Непонятный запрос", "Не знаю такого", "В моей памяти нет такой информации"]
                SendMessage(id, random.choice(answer), CheckStarostaKb(id))
#  CONSOLE
        elif CheckParam(id, "InAuth"):
    # Ключевое слово введено верно
            if body.lower() == KEY and (CheckParam(id, "Admin") or CheckAdmin(id)):
                SendMessage(id, "Кодовое слово введено верно. Добро пожаловать.", kb_vyh)
                SetParam(id, "InAuth", 0)
                SetParam(id, "InAdmAct", 1)
    # Отмена
            elif body.lower() == "отмена" and (CheckParam(id, "Admin") or CheckAdmin(id)):
                SendMessage(id, "Отмена авторизации", None)
                BackToLobby(id)
    # Ключевое слово введено неверно
            elif CheckParam(id, "Admin") or CheckAdmin(id):
                SendMessage(id, "Кодовое слово введено неверно.", kb_otm)
# In Active Panel
        elif CheckParam(id, "InAdmAct"):
    # Отмена
            if body.lower() == "отмена" and (CheckParam(id, "Admin") or CheckAdmin(id)):
                SendMessage(id, "Операция отменена", kb_vyh)
                BackToLobby(id)
                SetParam(id, "InAdmAct", 1)
    # Создание текста
            elif body.lower() == "запись":
                SendMessage(id, "Впишите текст", kb_vyh_otm)
                SetParam(id, "InMakeMnl", 1)
    # Создание рассылки
            elif body.lower() == "рассылка":
                SendMessage(id, "Введите текст рассылки", kb_vyh_otm)
                SetParam(id, "InMakeNews", 1)
    # Консоль
            elif body.lower() == "консоль":
                SendMessage(id, "Консоль запущена", kb_vyh_otm)
                SetParam(id, "InPy", 1)
    # Помощь
            elif body.lower() == "помощь":
                SendMessage(id, "Текст с командами и что они делают", kb_vyh_otm) # Для модераторов
    # In Console
            elif CheckParam(id, "InPy"):
                Cons()
    # In Make News
            elif CheckParam(id, "InMakeNews"):
                News(body)
    # In Make Manual
            elif CheckParam(id, "InMakeMnl"):
                MakeText(body)
    # Заглушка
            else:
                SendMessage(id, "Такой команды не существует", None)
# In Menu
        elif CheckParam(id, "InHelpMenu"):
            Menu(id, body)
# In Search
        elif CheckParam(id, "InSearch"):
            SendSearchResults(body, TextBodies, TextFrmtHeaders)
# In Library
        elif CheckParam(id, "InLibrary"):
            if body.lower() == "архив":
                SetParam(id, "InLibSearch", 1)
                SetParam(id, "InLibrary", 0)
                SendMessage(id, "Какую бы книгу Вы хотели найти?", kb_vyh)
            else:
                CheckID(id)
                answer = ["Обратитесь к списку книг", "В библиотеке нет такой информации"]
                kb = MakeKeyboard(["Архив"])
                SendMessage(id, random.choice(answer), kb)
        elif CheckParam(id, "InLibSearch"):
            if body.lower() == "выход":
                BackToLobby(id)
            elif body.lower() == "книга":
                SendSearchResults(body, BookBodies, BookFrmtHeaders)
            else:
                SendMessage(id, "Вам не стоит здесь находиться", kb_vyh)