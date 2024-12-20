-bot-name = Apples Bot
dpi-ratio = Your DPI ratio is { NUMBER($ratio, minimumFractionDigits: 3) }
pref-page =
    .title = { PLATFORM() ->
        [windows] Options
       *[other] Preferences
    }
emails = { $unreadEmails ->
        [one] You have one unread email.
        [42] You have { $unreadEmails } unread emails. So Long, and Thanks for All the Fish.
       *[other] You have { $unreadEmails } unread emails.
    }
start = Привет { $name }. {-bot-name}.
button-back = «
button-cancel = 🚫 Отмена
button-back_to_prev = « Назад
button-quit = « Выйти

channel-subscribe = 🔻 Для продолжения нужно подписаться на каналы
channel-button-subscribe = ≻ Подписаться
channel-button-subscribed = ✔️ Я подписался
