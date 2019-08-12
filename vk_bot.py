import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


group_id_string = '183716027'  # id группы вк
login = 'lkirya@ya.ru'
password = ''
token = ''


def wall_post():
    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()
    print(vk.wall.post(
        owner_id="-" + group_id_string,
        message='Hello world!',
        friends_only=0,
        from_group=1,
        signed=0
    ))


def auth_handler():
    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def begin_keyboard():  # возвращаем готовую клавиатуру начального выбора
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Помочь деньгами', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('Волонтерство', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('Требуются вещи/предметы', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('Ссылка на портал', color=VkKeyboardColor.DEFAULT)

    return keyboard.get_keyboard()


def pay_keyboard():  # возвращаем готовую клавиатуру c оплатой
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Банковская карта', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    current_line = keyboard.lines[-1]
    current_line.append({
        'action': {
            "type": "vkpay",
            "hash": "action=transfer-to-group&group_id=" + group_id_string + "&aid=1"
            # aid хз вообще какой для бота указывать :(
        }
    })
    keyboard.add_line()
    keyboard.add_button('Назад', color=VkKeyboardColor.DEFAULT)

    return keyboard.get_keyboard()


def main():
    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk_session = vk_api.VkApi(
        token=token
    )  # токен лонгполла
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id_string)  # id группы

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            print('Для меня от: ', end='')
            user_from = vk.users.get(user_ids=event.obj.from_id)
            print(user_from)
            print('Текст:', event.obj.text)
            print()

            if event.obj.text.lower() == 'начать':
                msg = 'Здравствуйте, ' + user_from[0]['first_name'] + '! Выберите действие:'
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=begin_keyboard()
                )

            elif event.obj.text.lower() == 'назад':
                msg = user_from[0]['first_name'] + ', выберите действие:'
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=begin_keyboard()
                )

            elif event.obj.text.lower() == 'помочь деньгами':
                msg = '''Можно перевести деньги через vkPay или перейти на сайт для оплаты через платежную систему.  
                    Перевод через vkPay распределится среди всех нуждающихся поровну. 
                    Платежом на сайте можно распорядиться по собственному усмотрению''',
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=pay_keyboard()
                )

            elif event.obj.text.lower() == 'ссылка на портал':
                msg = '*Ссылка на главную страницу портала*',
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=begin_keyboard()
                )

            elif event.obj.text.lower() == 'банковская карта':
                msg = '*Ссылка на страницу портала с пожертвованиями*',
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=begin_keyboard()
                )

            elif event.obj.text.lower() == 'волонтерство':
                msg = '*Ссылка на страницу портала с волонтерством*',
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=begin_keyboard()
                )

            elif event.obj.text.lower() == 'требуются вещи/предметы':
                msg = '*Ссылка на страницу портала с вещами/предметами*',
                vk.messages.send(
                    user_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=msg,
                    keyboard=begin_keyboard()
                )

            else:
                if event.obj.text.lower()[0:5] == 'promo':  # тут if на промокод
                    # вызов процедуры отправки оповещения
                    msg = 'Промокод отправлен на модерацию'
                    vk.messages.send(
                        user_id=event.obj.from_id,
                        random_id=get_random_id(),
                        message=msg
                    )

                else:
                    msg = 'Для начала работы с ботом необходимо отправить сообщение: "Начать". Или введите промокод.'
                    vk.messages.send(
                        user_id=event.obj.from_id,
                        random_id=get_random_id(),
                        message=msg
                    )

        # Если получили платеж, уведомляем и отправляем уведомление, что б проверить и отправить подаркок
        elif event.type == VkBotEventType.VKPAY_TRANSACTION:
            # вызов процедуры отправки оповещения
            msg = 'От Вас получен платеж на сумму ' + event.obj.amount + ' руб.'
            msg = msg + ' После модерации Вам будет выслан подарок. Спасибо, что помогли нуждающимся!'
            vk.messages.send(
                user_id=event.obj.from_id,
                random_id=get_random_id(),
                message=msg
            )

        else:
            print(event.type)
            print()


if __name__ == '__main__':
    main()
