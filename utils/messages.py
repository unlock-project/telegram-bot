# Сообщения, которые использует бот
# {} - бот сам подставит вместо этого нужное значения, не меняйте ключ внутри скобок, не добавляйте новые
# (Если вы предварительно не изменили код, где это сообщение используется)
# Здесь присутствует не используемые сообщения, мне лень чистить ;-)
# Форматирование с помощью html-тэгов, список - https://core.telegram.org/bots/api#html-style

welcome_message = """Привет, <b>{name}</b>!
На смене Unlock действует внутренняя валюта — LockCoin, которую можно зарабатывать в течение смены. Люди, накопившие больше всего LockCoin’ов, получат крутые подарки. Этот бот позволяет смотреть баланс, отображать события, а также участвовать в интерактивах.

При посещении каждого мероприятия необходимо показать организатору личный QR-код. За это начисляются LockCoin’ы. Также на командных мероприятиях активность и успешное выполнение заданий будут приносить команде определенное количество LockCoin'ов. На лекциях и мастер-классах самые активные участники будут получать промокоды от спикеров, за которые также можно получить награждения.

Все LockCoin’ы, полученные членами команды, суммируются в командный рейтинг. Команда-победитель в конце смены также получит ценные призы."""
 # name - Имя пользователя, которое вернул бэк

tutorial = """Кнопка <b>«Мой баланс»</b> отобразит личный баланс LockCoin’в. 
По кнопке <b>«Расписание»</b> можно узнать,какие мероприятия запланированы на сегодня.  
Кнопка <b>«Промокод»</b> позволит ввести код, полученный от организаторов или лекторов.  
<b>«Моя команда»</b> - узнать информацию о своей команде.
Кнопка <b>«Показать QR код»</b> позволяет посмотреть свой QR-код.
"""


user_not_found = "Я не нашёл тебя в базе данных. Пожалуйста, обратись к тьютору."

score_message = "На балансе <b>{score}</b> LockCoin." # score - текущий баланс пользователя

daily_report_message = "На сегодня запланировано: " \
                       "\n{report}\n\n" # report - сегодняшние мероприятия построчно
no_event_today = "Нет запланированных событий."


team_message = """
Название команды: {name}
Баллы: {score}
Тьютор: {tutor}
""" # name - название команды
    # score - баллы команды
    # tutor - Имя Фамилия Тьютора

error_message = "Произошла ошибка. Ваши верные подданые уже бегут её исправлять"

error_report = "ОШИБКА!\nНомер ошибки - <code>{error_id}</code>\nПодробнее по <a href=\"{error_url}\">ссылке</a>"
# error_id - номер ошибки
# error-url - ссылка на трейсбэк ошибки

already_met = "Мы уже познакомились"

not_met = "Мы ещё не познакомились. Напиши /start боту @{bot}" # bot - Username бота

cleared_message = "Клавиатура убрана, мой господин."

enter_promocode_message = "Введите код:"

admin_mode = "Админ режим <b>{state}</b>" # state - Включен/Выключен

enter_text_to_broadcast_message = "Отправьте мне текст, который нужно разослать"

ok_message = "Окей"

updated_message = "Обновлено"

promocode_not_found_message = "Такой промокод не найден, проверь, правильно ли ты его ввёл."

choose_what_to_send_message = "Выберете, что я должен отправить"

data_not_found_message = "Я не нашёл запрашиваемые данные"

question_arrived_message = "У меня к тебе появился вопрос. Ответишь?"

question_message = "Чтобы ответить на вопрос, напиши мне сообщение с ответом."

qr_code_message = "Вот твой персональный QR-код, сохрани его к себе, чтобы не потерять!"
qr_code_view = "Чтобы посмотреть свой QR-код, нажмите на кнопку под сообщением!"
choose_companion = "Введите user_id человека, к которому хотите подключится. Чтобы отменить введите \"-1\""

tunnel_started = "{role} начал с вами беседу, все сообщения которые вы пишите мне отправляются вашему напарнику, " \
                 "равно как и наоборот.\n\n" \
                 "Чтобы прервать беседу нажмите на кнопку или напишите \"Отключится\"" # role - Админ/Участник


scanner_message = "Вот твой сканер, чтобы отметить присутвующих на мероприятии {event_name}"
                    # event_name - Название мероприятия

throttled = "Не так быстро!"


became_admin = "{admin_name} назначил вас администратором. /start - чтобы обновить клавиатуру"
appointed_admin = "Вы назначили {user_name} администратором"
already_admin = "Этот пользователь уже администратор"
not_admin = "Этот пользователь не администратор"
no_longer_admin = "{admin_name} снял с вас права администратора. /start - чтобы обновить клавиатуру"
revoked_admin = "Вы сняли с {user_name} права администратора"
ban_user = "Вы забанили {user_name}!"
unban_user = "Вы разбанили {user_name}!"
banned_user = "Вас забанил {admin_name}! Я теперь не могу принимать от тебя сообщения ;-("
unbanned_user = "Вас разбанил {admin_name}! Я теперь могу принимать от тебя сообщения :-)"
already_banned = "Этот пользователь уже забанен"
not_banned = "Этот пользователь не забанен"
team_not_found = "Команда не найдена"

# Phrases in buttons

qr_request = "Показать QR код"
score_request = "Мой баланс"
daily_report = "Расписание"
team_report = "Моя команда"
promocode = "Промокод"
cancel = "Отмена"
turn_on_admin = "Админ режим"
turn_off_admin = "Выйти из админ режима"
broadcast = "Разослать сообщение"
update_db = "Обновить бд"
votes = "Голосования"
registrations = "Регистрации"
questions = "Вопросы"
back = "Назад"
answer = "Ответить"
start_tunnel = "Подключиться к диалогу"
stop_tunnel = "Отключиться"
go_to_web = "Перейти" # Not used in production
open_scanner = "Открыть сканер"
see_qr = "Посмотреть"

