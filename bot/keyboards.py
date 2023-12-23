from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton

import datetime


class AdminConfirmEventDataKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')
    # btn2 = InlineKeyboardButton('Подтвердить', callback_data='add-event')
    btn2 = InlineKeyboardButton('Подтвердить', callback_data='confirm-event-field')

    markup.add(btn1, btn2)

class EmpCancel:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Отмена', callback_data='emp-cancel'))


class AdminCancel:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Отмена', callback_data='admin-cancel'))


class AdminConfirmEmpAdd:
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')
    btn2 = InlineKeyboardButton('Подтвердить', callback_data='confirm-emp-reg')

    markup.add(btn1, btn2)


class AdminStartKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Добавить мероприятие', callback_data='select-event-type')
    btn2 = InlineKeyboardButton('Удалить мероприятие', callback_data='del-event')
    btn3 = InlineKeyboardButton('Изменить мероприятие', callback_data='edit-event')
    btn4 = InlineKeyboardButton('Управлять персоналом', callback_data='control-emps')
    btn5 = InlineKeyboardButton('Календарь мероприятий', callback_data='all-events')
    btn6 = InlineKeyboardButton('Резервная копия базы', callback_data='dump-db')

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)


class ParseDatesKeyboard:
    def __init__(self, dates, mode='adm'):
        self.markup = InlineKeyboardMarkup(row_width=4)
        self.markup.add(*sorted(list({InlineKeyboardButton(date, callback_data=f'day:{date[:2]}-mon:{date[3:5]}-year:{date[6:]}') for date in dates}), key=lambda x: (int(x.callback_data[19:]), int(x.callback_data[11:13]), int(x.callback_data[4:6]))))
        if mode == 'adm':
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='admin-cancel'))
        elif mode == 'emp':
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='emp-cancel'))
        else:
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='client-cancel'))
    

class ParseEventsByDateKeyboard:
    def __init__(self, events, mode='adm'):
        self.markup = InlineKeyboardMarkup(row_width=1)
        self.markup.add(*sorted([InlineKeyboardButton(f"{event[1] if event[3] else event[2]} - {event[4]}", callback_data=f"id:{event[0]}-time:{event[4]}") for event in events], key=lambda x: (int(x.callback_data[::-1][3:5]), int(x.callback_data[::-1][:2]))))
        # self.markup.add(*sorted([InlineKeyboardButton(f"{event[1]} - {event[2]}", callback_data=f"name:{event[1]}-time:{event[2]}") for event in events], key=lambda x: (int(x.callback_data[x.callback_data.index(":", x.callback_data.index(":")+1) - 2:x.callback_data.index(":", x.callback_data.index(":")+1)]), int(x.callback_data[x.callback_data.index(":", x.callback_data.index(":")+1):]))))
        if mode == 'adm':
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='admin-cancel'))
        elif mode == 'emp':
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='emp-cancel'))
        else:
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='client-cancel'))
    

class SelectPlatform:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Войковская', callback_data='select-voyk')
    btn2 = InlineKeyboardButton('Верхние Лихоборы', callback_data='select-verh')
    btn3 = InlineKeyboardButton('\"Живописно\"', callback_data='select-zhiv')
    btn4 = InlineKeyboardButton('Музей Света и Цвета', callback_data='select-musm')
    btn5 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')

    markup.add(btn1, btn2, btn3, btn4, btn5)

class SearchSelectPlatform:
    def __init__(self, role):
        self.markup = InlineKeyboardMarkup(row_width=2)
        btn1 = InlineKeyboardButton('Войковская', callback_data='select-voyk')
        btn2 = InlineKeyboardButton('Верхние Лихоборы', callback_data='select-verh')
        btn3 = InlineKeyboardButton('\"Живописно\"', callback_data='select-zhiv')
        btn4 = InlineKeyboardButton('Музей Света и Цвета', callback_data='select-musm')
        if role == 'adm':
            btn5 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')
        elif role == 'emp':
            btn5 = InlineKeyboardButton('Отмена', callback_data='emp-cancel')
        else:
            btn5 = InlineKeyboardButton('Отмена', callback_data='client-cancel')

        self.markup.add(btn1, btn2, btn3, btn4, btn5)

class SelectType:
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Закрытое', callback_data='select-private')
    btn2 = InlineKeyboardButton('Открытое', callback_data='select-public')
    btn3 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')

    markup.add(btn1, btn2, btn3)


class AdminAddPublicKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Ввести название мероприятия', callback_data='enter-event-name')
    btn3 = InlineKeyboardButton('Выбрать площадку', callback_data='enter-event-platform')
    btn4 = InlineKeyboardButton('Ввести количество гостей', callback_data='enter-event-quota')
    btn5 = InlineKeyboardButton('Ввести описание', callback_data='enter-event-description')
    btn6 = InlineKeyboardButton('Ввести дату и время мероприятия', callback_data='enter-event-datetime')
    btn8 = InlineKeyboardButton('Подтвердить', callback_data='confirm-event-reg')
    btn9 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')


    markup.add(btn1, btn6, btn3, btn4, btn5)
    markup.row(btn8, btn9)


class AdminAddPrivateKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn2 = InlineKeyboardButton('Ввести имя клиента', callback_data='enter-client-name')
    btn3 = InlineKeyboardButton('Выбрать площадку', callback_data='enter-event-platform')
    btn5 = InlineKeyboardButton('Ввести описание', callback_data='enter-event-description')
    btn6 = InlineKeyboardButton('Ввести дату и время мероприятия', callback_data='enter-event-datetime')
    btn8 = InlineKeyboardButton('Подтвердить', callback_data='confirm-event-reg')
    btn9 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')

    markup.add(btn2, btn6, btn3, btn5)
    markup.row(btn8, btn9)



class AdminEditPublicKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Ввести название мероприятия', callback_data='enter-event-name')
    btn3 = InlineKeyboardButton('Выбрать площадку', callback_data='enter-event-platform')
    btn4 = InlineKeyboardButton('Ввести количество гостей', callback_data='enter-event-quota')
    btn5 = InlineKeyboardButton('Ввести описание', callback_data='enter-event-description')
    btn6 = InlineKeyboardButton('Ввести дату и время мероприятия', callback_data='enter-event-datetime')
    btn8 = InlineKeyboardButton('Подтвердить', callback_data='confirm-event-edit')
    btn9 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')

    markup.add(btn1, btn6, btn3, btn4, btn5)
    markup.row(btn8, btn9)


class AdminEditPrivateKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)

    btn2 = InlineKeyboardButton('Ввести имя клиента', callback_data='enter-client-name')
    btn3 = InlineKeyboardButton('Выбрать площадку', callback_data='enter-event-platform')
    btn5 = InlineKeyboardButton('Ввести описание', callback_data='enter-event-description')
    btn6 = InlineKeyboardButton('Ввести дату и время мероприятия', callback_data='enter-event-datetime')
    btn8 = InlineKeyboardButton('Подтвердить', callback_data='confirm-event-edit')
    btn9 = InlineKeyboardButton('Отмена', callback_data='admin-cancel')

    markup.add(btn2, btn6, btn3, btn5)
    markup.row(btn8, btn9)


class AdminControlEmpsKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Добавить сотрудника', callback_data='add-emp')
    btn2 = InlineKeyboardButton('Удалить сотрудника', callback_data='del-emp')
    # btn3 = InlineKeyboardButton('Посмотреть сотрудников', callback_data='view-emps')

    markup.add(btn1, btn2)


class AdminSelectEmpToDel:
    def __init__(self, emps):
        self.markup = InlineKeyboardMarkup(row_width=4)
        self.markup.add(*(InlineKeyboardButton(x.name, callback_data=f"select-{x.id}") for x in emps))
        self.markup.row(InlineKeyboardButton('Отмена', callback_data='admin-cancel'))

class AdminSelectTypeKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Закрытое мероприятие', callback_data='add-private-event')
    btn2 = InlineKeyboardButton('Открытое мероприятие', callback_data='add-public-event')

    markup.add(btn1, btn2)

class EmpStartKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Календарь мероприятий', callback_data="all-events")

    markup.add(btn1)


class StartKeyboard:
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Подписки', callback_data='subscriptions')
    btn2 = InlineKeyboardButton('Мои мероприятия', callback_data='my-events')
    btn3 = InlineKeyboardButton('Ближайшие мероприятия', callback_data='upcoming-events')

    markup.add(btn1, btn2, btn3)


# class MyEventsKeyboard:
#     markup = InlineKeyboardMarkup(row_width=2)
#     btn1 = InlineKeyboardButton('Подписки', callback_data='subscriptions')
#     btn2 = InlineKeyboardButton('Мои мероприятия', callback_data='my-events')
#     btn3 = InlineKeyboardButton('Ближайшие мероприятия', callback_data='upcoming-events')

#     markup.add(btn1, btn2, btn3)


# class UpcomingEventsKeyboard:
#     markup = InlineKeyboardMarkup(row_width=2)
#     btn1 = InlineKeyboardButton('Подписки', callback_data='subscriptions')
#     btn2 = InlineKeyboardButton('Мои заявки', callback_data='my-events')
#     btn3 = InlineKeyboardButton('Ближайшие мероприятия', callback_data='upcoming-events')
#     for i in [datetime.datetime.today() + datetime.timedelta(days=x) for x in range(31)]:
#         markup.add(InlineKeyboardButton(f'{i.strftime("%d.%m")}', callback_data=f'event-{i.strftime("%d-%m")}'))

#     markup.add(btn1, btn2, btn3)


class SubscriptionsKeyboard:
    def __init__(self, subs):
        self.markup = InlineKeyboardMarkup(row_width=2)
        checks = {'verh': '❌', 'voyk': '❌', 'zhiv': '❌', 'musm': '❌'}
        for i in subs:
            checks[i.platform] = '✅'
        btn1 = InlineKeyboardButton(f'{checks["voyk"]} Войковская', callback_data='sub-voyk')
        btn2 = InlineKeyboardButton(f'{checks["verh"]} Верхние Лихоборы', callback_data='sub-verh')
        btn3 = InlineKeyboardButton(f'{checks["zhiv"]} \"Живописно\"', callback_data='sub-zhiv')
        btn4 = InlineKeyboardButton(f'{checks["musm"]} Музей света и цвета', callback_data='sub-musm')
        btn5 = InlineKeyboardButton('Назад', callback_data='client-cancel')

        self.markup.add(btn1, btn2, btn3, btn4, btn5)


class SubscribeKeyboard:
    def __init__(self, event_id):
        self.markup = InlineKeyboardMarkup(row_width=1)
        btn1 = InlineKeyboardButton('Подать заявку', callback_data=f'apply-{event_id}')
        btn2 = InlineKeyboardButton('Меню', callback_data="client-cancel")

        self.markup.add(btn1, btn2)

class ClientConfirmName:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Подтвердить', callback_data='confirm-client-user-name'))


class ClientConfirmPhone:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Подтвердить', callback_data='confirm-client-phone'))


class FillApplicationKeyboard:
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton('Ввести имя контактного лица', callback_data='client-fill-name')
    btn2 = InlineKeyboardButton('Ввести имя ребенка (или детей)', callback_data='client-fill-children-name')
    btn3 = InlineKeyboardButton('Ввести контактный телефона', callback_data='client-fill-phone-number')
    btn4 = InlineKeyboardButton('Ввести количество детей', callback_data='client-fill-children-amount')
    btn5 = InlineKeyboardButton('Отправить заявку', callback_data='client-confirm-application')
    btn6 = InlineKeyboardButton('Отмнена', callback_data="client-cancel")

    markup.add(btn1, btn2, btn3, btn4)
    markup.row(btn5, btn6)

class ClientConfirmCancelApplicationFields:
    def __init__(self, event_id):
        self.markup = InlineKeyboardMarkup(row_width=2)
        self.markup.add(InlineKeyboardButton('Подтвердить', callback_data=f'apply-{event_id}'),
                InlineKeyboardButton('Отмена', callback_data='client-cancel'))

class ClientCancel:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Отмена', callback_data='client-cancel'))

class ClientMyEvents:
    def __init__(self, events, mode):
        self.markup = InlineKeyboardMarkup(row_width=2)
        self.markup.add(*sorted([InlineKeyboardButton(f"{event[1] if event[3] else event[2]} - {event[4]}", callback_data=f"id:{event[0]}-time:{event[4]}") for event in events], key=lambda x: (int(x.callback_data[::-1][3:5]), int(x.callback_data[::-1][:2]))))
        if mode == 'usr':
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='client-cancel'))
        else:
            self.markup.add(InlineKeyboardButton('Отмена', callback_data='client-cancel'))
        # self.markup.add((InlineKeyboardButton(f"", callback_data=f"id:{x.id}") for x in applications))

class ClientMyEventsUnsubscribe:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Отменить запись', callback_data='client-cancel-application'),
               InlineKeyboardButton('Меню', callback_data='client-cancel'))
    

class AdminView:
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Посмотреть заявки', callback_data='admin-seek-applications'),
               InlineKeyboardButton('Отмена', callback_data='admin-cancel'))
    

class AdminViewApplications:
    def __init__(self, applications):
        self.markup = InlineKeyboardMarkup(row_width=2)
        self.markup.add(*[InlineKeyboardButton(f"{application[1]}", callback_data=f"id:{application[0]}-client_name:{application[1]}") for application in applications])
        self.markup.add(InlineKeyboardButton('Отмена', callback_data='admin-cancel'))
    

class ClientSendConfirm:
    def __init__(self, application_id):
        self.markup = InlineKeyboardMarkup(row_width=1)
        self.markup.add(InlineKeyboardButton('Подтвердить', callback_data=f'confirm-{application_id}'),
                        InlineKeyboardButton('Отменить заявку', callback_data=f'decline-{application_id}'))
        
        