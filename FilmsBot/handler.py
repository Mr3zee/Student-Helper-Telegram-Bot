from time import sleep
from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, CallbackQueryHandler, ConversationHandler, \
    CommandHandler

import FilmsBot.server as server
import FilmsBot.keyboard as keyboard
from FilmsBot.message import get_text, make_list
from log import log_handler

handlers = {}

commands = {}

LOGIN, PASSWORD, MAIN, \
CHANGING, ADD, LIST_USER, \
ADMIN_AUTH, CONTROL, ADD_USER_ADMIN, \
CHG_CALLBACK_ADMIN, CHG_ADMIN, RM_USER_ADMIN, \
CONFIRM_RM_USER_ADMIN, DISCONNECT = range(14)


@log_handler
def unauthorized(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('unauthorized_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def stop_auth(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('stop_auth_text', language_code),
    )
    return ConversationHandler.END


stop_auth_hld = CommandHandler('stop_auth', stop_auth)


@log_handler
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('start_text', language_code),
    )
    return LOGIN


@log_handler
def login(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('login_user_text', language_code),
        reply_markup=keyboard.usernames_keyboard(),
    )
    return LOGIN


@log_handler
def echo(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('echo_text', language_code),
    )
    return MAIN


@log_handler
def echo_auth(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('echo_auth_text', language_code),
    )
    return LOGIN


@log_handler
def help_(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    text = get_text('help_text', language_code).format(server.get_link())
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )
    return MAIN


@log_handler
def auth(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    username = keyboard.keys_users[query.data]

    query.answer()

    if server.user_authorized(username):
        chat_id = update.effective_chat.id
        if username == server.get_username(chat_id):
            query.edit_message_text(
                text=get_text('logged_in_text', language_code),
            )
            return LOGIN
        query.edit_message_text(
            text=get_text('error_text', language_code),
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=get_text('bad_auth_text', language_code),
            reply_markup=keyboard.usernames_keyboard(),
        )
        return LOGIN

    context.user_data['username'] = username

    query.edit_message_text(
        text=get_text('login_password_text', language_code),
    )
    return PASSWORD


@log_handler
def password_handler(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.user_data['password'] = update.message.text
    chat_id = update.effective_chat.id
    if not server.auth_user(context.user_data, chat_id):
        context.bot.send_message(
            chat_id=chat_id,
            text=get_text('bad_password_text', language_code),
        )
        return ConversationHandler.END
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('auth_text', language_code).format(context.user_data['username']),
    )
    context.user_data.clear()
    return MAIN


def callback_auth(update: Update, context: CallbackContext):
    query_data = update.callback_query.data
    if query_data in keyboard.keys_users.keys():
        return auth(update, context)
    return echo(update, context)


@log_handler
def log_out(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    server.unauth_user(chat_id)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('log_out_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def random(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    current_film = server.random_film()
    message_id = context.bot.send_message(
        chat_id=chat_id,
        text=get_text('random_film_process_text', language_code).format(current_film),
    ).message_id
    last_film = current_film
    for i in range(15):
        current_film = server.random_film()
        if current_film == last_film:
            continue
        sleep(0.05)
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=get_text('random_film_process_text', language_code).format(current_film)
        )
        last_film = current_film
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=get_text('random_film_text', language_code).format(server.random_film()),
    )
    return MAIN


@log_handler
def to_tick(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('tick_text', language_code),
        reply_markup=keyboard.tick_keyboard(language_code),
    )
    return CHANGING


@log_handler
def to_untick(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('untick_text', language_code),
        reply_markup=keyboard.untick_keyboard(language_code),
    )
    return CHANGING


@log_handler
def callback_changing(update: Update, context: CallbackContext):
    query_data = update.callback_query.data
    if query_data == keyboard.COMPLETE_BUTTON:
        return complete_query(update, context)
    elif len(query_data) >= 4 and query_data[:4] == 'tick':
        return tick(update, context)
    elif len(query_data) >= 6 and query_data[:6] == 'untick':
        return untick(update, context)
    elif len(query_data) >= 6 and query_data[:6] == 'remove':
        return remove(update, context)
    return need_to_complete(update, context)


@log_handler
def tick(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    query.edit_message_reply_markup(
        reply_markup=keyboard.tick_keyboard(language_code, query.data)
    )
    return CHANGING


@log_handler
def untick(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    query.edit_message_reply_markup(
        reply_markup=keyboard.untick_keyboard(language_code, query.data)
    )
    return CHANGING


@log_handler
def complete_query(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    keyboard.done_marked_buttons()
    update.callback_query.edit_message_text(
        text=get_text('completed_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def complete(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('completed_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def need_to_complete(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('need_to_complete_text', language_code),
    )
    return CHANGING


@log_handler
def to_add(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('add_text', language_code),
    )
    return ADD


def add(update: Update, context: CallbackContext):
    server.add_films(update.message.text.split('\n'))
    return complete(update, context)


@log_handler
def to_remove(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('remove_text', language_code),
        reply_markup=keyboard.remove_keyboard(language_code),
    )
    return CHANGING


@log_handler
def remove(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    query.edit_message_reply_markup(
        reply_markup=keyboard.remove_keyboard(language_code, query.data)
    )
    return CHANGING


@log_handler
def list_(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)

    text = make_list(
        server.get_films(server.get_username(chat_id)),
        get_text('self_films_list_text', language_code),
        language_code,
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=None,
    )
    return MAIN


@log_handler
def to_list_user(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    if not server.check_auth(chat_id):
        return unauthorized(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('enter_username_list_text', language_code),
        reply_markup=keyboard.usernames_keyboard(),
    )
    return LIST_USER


@log_handler
def callback_list_user(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query

    name = keyboard.keys_users[query.data]
    text = make_list(
        server.get_films(name),
        get_text('user_films_list_text', language_code),
        language_code,
    ).format(name)
    # todo fix key_users

    query.edit_message_text(
        text=text,
    )
    return ConversationHandler.END


@log_handler
def enter_username(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('echo_username_text', language_code),
    )
    return LIST_USER


@log_handler
def admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('auth_admin_text', language_code),
    )
    return ADMIN_AUTH


@log_handler
def auth_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    text = update.message.text
    if text == '/cancel':
        return exit_admin(update, context)
    if server.auth_admin(text.split('\n')):
        return help_admin(update, context)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('auth_admin_error_text', language_code),
    )
    return ADMIN_AUTH


@log_handler
def exit_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('exit_admin_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def help_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('help_admin_text', language_code),
    )
    return CONTROL


@log_handler
def echo_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('echo_admin_text', language_code),
    )
    return CONTROL


@log_handler
def all_users_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    text = get_text('users_list_admin_text', language_code)
    for user in server.get_users():
        text += user \
                + (get_text('user_authorized_mark', language_code)
                   if server.user_authorized(user)
                   else get_text('user_unauthorized_mark', language_code)) \
                + '\n\n'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
    return CONTROL


@log_handler
def to_add_user_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('add_user_admin_text', language_code),
    )
    return ADD_USER_ADMIN


def add_user_admin(update: Update, context: CallbackContext):
    text = update.message.text
    if server.add_user(text.split('\n')):
        return done_admin(update, context)
    return user_data_error_admin(update, context, ADD_USER_ADMIN)


@log_handler
def user_data_error_admin(update: Update, context: CallbackContext, retval):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('user_data_error_admin_text', language_code),
    )
    return retval


@log_handler
def done_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('done_admin_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def stop_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.user_data.clear()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('stop_admin_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def to_change_user_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('choose_user_admin_text', language_code),
        reply_markup=keyboard.usernames_keyboard(),
    )
    return CHG_CALLBACK_ADMIN


@log_handler
def chg_admin_callback(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    if query.data == keyboard.USERNAME_BUTTON or query.data == keyboard.PASSWORD_BUTTON:
        context.user_data['field'] = query.data
        query.edit_message_text(
            text=get_text('new_field_admin_text', language_code),
        )
        return CHG_ADMIN

    username = keyboard.keys_users[query.data]
    context.user_data['username'] = username

    query.edit_message_text(
        text=get_text('change_user_admin_text', language_code),
    )
    query.edit_message_reply_markup(
        reply_markup=keyboard.change_user_admin_keyboard(language_code),
    )
    return CHG_CALLBACK_ADMIN


@log_handler
def to_rm_user_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('to_rm_user_admin_text', language_code),
        reply_markup=keyboard.usernames_keyboard(),
    )
    return RM_USER_ADMIN


@log_handler
def rm_callback_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    chat_id = update.effective_chat.id

    username = keyboard.keys_users[query.data]

    if server.valid_rm_user(username, chat_id):
        query.edit_message_text(
            text=get_text('selected_to_rm_user_admin_text', language_code).format(username),
        )
        context.user_data['username'] = keyboard.keys_users[query.data]
        context.bot.send_message(
            chat_id=chat_id,
            text=get_text('confirm_rm_admin_text', language_code),
        )
        return CONFIRM_RM_USER_ADMIN
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('bad_rm_user_admin_text', language_code),
    )
    query.answer()
    return RM_USER_ADMIN


@log_handler
def rm_user_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    text = update.message.text
    chat_id = update.effective_chat.id

    status_ok, user_chat_id = server.rm_user(text.split('\n'), context.user_data['username'])

    if status_ok:
        if user_chat_id:
            alert_removal(update, context, user_chat_id)
        context.user_data.clear()
        return done_admin(update, context)

    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('bad_password_rm_user_admin_text', language_code),
    )
    return CONFIRM_RM_USER_ADMIN


def change_user_admin(update: Update, context: CallbackContext):
    new_data = update.message.text

    if server.change_user(context.user_data, new_data):
        context.user_data.clear()
        return done_admin(update, context)

    return user_data_error_admin(update, context, CHG_ADMIN)


def error_admin(retval_level):
    @log_handler
    def error(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text('error_admin_text', language_code),
        )
        return retval_level

    return error


stop_admin_hdl = CommandHandler('stop_admin', stop_admin)


@log_handler
def to_disconnect_user_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    users = server.get_authorized()
    if len(users) == 0:
        return no_users_authorized_admin(update, context)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('disconnect_user_admin_text', language_code),
        reply_markup=keyboard.usernames_keyboard(users),
    )
    return DISCONNECT


@log_handler
def no_users_authorized_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('no_users_authorized_admin_text', language_code),
    )
    return ConversationHandler.END


@log_handler
def disconnect_callback_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    chat_id = update.effective_chat.id

    query.answer()

    if query.data == keyboard.CONFIRM_BUTTON:
        type_ = context.user_data['type']
        if type_ == 'one':
            user_chat_id = server.disconnect_user(context.user_data['username'])
            alert_disconnection(update, context, user_chat_id)
        elif type_ == 'all':
            for user in server.get_authorized():
                if server.valid_disconnection(user):
                    user_chat_id = server.disconnect_user(update)
                    alert_disconnection(update, context, user_chat_id)
        else:
            context.user_data.clear()
            context.bot.send_message(
                chat_id=chat_id,
                text=get_text('fatal_error_text', language_code),
            )
            return ConversationHandler.END
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.message_id,
        )
        context.user_data.clear()
        return done_admin(update, context)
    elif query.data == keyboard.CANCEL_BUTTON:
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.message_id,
        )
        return stop_admin(update, context)
    elif query.data in keyboard.keys_users:
        username = keyboard.keys_users[query.data]
        if not server.valid_disconnection(username):
            context.bot.send_message(
                chat_id=chat_id,
                text=get_text('bad_disconnect_user_admin_text', language_code),
            )
            return DISCONNECT

        context.user_data['username'] = username
        context.user_data['type'] = 'one'
        query.edit_message_text(
            text=get_text('confirm_disconnection_admin_text', language_code),
        )
        query.edit_message_reply_markup(
            reply_markup=keyboard.confirm_admin_keyboard(language_code),
        )
        return DISCONNECT
    else:
        return error_admin(DISCONNECT)(update, context)


@log_handler
def confirm_disconnection_all_admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.user_data['type'] = 'all'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('confirm_disconnection_admin_text', language_code),
        reply_markup=keyboard.confirm_admin_keyboard(language_code),
    )
    return DISCONNECT


@log_handler
def alert_disconnection(update: Update, context: CallbackContext, chat_id):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('disconnection_alert_admin_text', language_code),
    )


@log_handler
def alert_removal(update: Update, context: CallbackContext, chat_id):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('removal_alert_admin_text', language_code),
    )


handlers['main'] = ConversationHandler(
    entry_points=[
        CommandHandler('login', login, pass_user_data=True),
    ],
    states={
        LOGIN: [
            CallbackQueryHandler(callback=callback_auth, pass_user_data=True),
            stop_auth_hld,
            MessageHandler(Filters.all, echo_auth),
        ],
        PASSWORD: [
            stop_auth_hld,
            MessageHandler(Filters.all, password_handler),
        ],
        MAIN: [
            ConversationHandler(
                entry_points=[
                    CommandHandler('tick', to_tick),
                    CommandHandler('untick', to_untick),
                    CommandHandler('add', to_add),
                    CommandHandler('remove', to_remove),
                    CommandHandler('list_user', to_list_user),
                ],
                states={
                    CHANGING: [
                        CallbackQueryHandler(callback=callback_changing),
                        MessageHandler(Filters.all, need_to_complete),
                    ],
                    ADD: [
                        MessageHandler(Filters.all, add),
                    ],
                    LIST_USER: [
                        CallbackQueryHandler(callback=callback_list_user),
                        MessageHandler(Filters.all, enter_username)
                    ],
                },
                fallbacks=[],
            ),
            CommandHandler('help', help_),
            CommandHandler('log_out', log_out),
            CommandHandler('list', list_),
            CommandHandler('random', random),
            MessageHandler(Filters.all, echo),
        ]
    },
    fallbacks=[],
)

handlers['admin'] = ConversationHandler(
    entry_points=[
        CommandHandler('admin', admin),
    ],
    states={
        ADMIN_AUTH: [
            stop_auth_hld,
            MessageHandler(Filters.all, auth_admin),
        ],
        CONTROL: [
            ConversationHandler(
                entry_points=[
                    CommandHandler('add_user', to_add_user_admin),
                    CommandHandler('change_user', to_change_user_admin, pass_user_data=True),
                    CommandHandler('remove_user', to_rm_user_admin, pass_user_data=True),
                    CommandHandler('disconnect_user', to_disconnect_user_admin, pass_user_data=True),
                    CommandHandler('disconnect_all_users', confirm_disconnection_all_admin, pass_user_data=True),
                ],
                states={
                    ADD_USER_ADMIN: [
                        stop_admin_hdl,
                        MessageHandler(Filters.all, add_user_admin),
                    ],
                    CHG_CALLBACK_ADMIN: [
                        CallbackQueryHandler(callback=chg_admin_callback, pass_user_data=True),
                        stop_admin_hdl,
                        MessageHandler(Filters.all, error_admin(CHG_CALLBACK_ADMIN), pass_user_data=True),
                    ],
                    CHG_ADMIN: [
                        stop_admin_hdl,
                        MessageHandler(Filters.all, change_user_admin, pass_user_data=True),
                    ],
                    RM_USER_ADMIN: [
                        CallbackQueryHandler(callback=rm_callback_admin, pass_user_data=True),
                        stop_admin_hdl,
                        MessageHandler(Filters.all, error_admin(RM_USER_ADMIN), pass_user_data=True),
                    ],
                    CONFIRM_RM_USER_ADMIN: [
                        stop_admin_hdl,
                        MessageHandler(Filters.all, rm_user_admin, pass_user_data=True),
                    ],
                    DISCONNECT: [
                        CallbackQueryHandler(callback=disconnect_callback_admin, pass_chat_data=True),
                        stop_admin_hdl,
                        MessageHandler(Filters.all, error_admin(DISCONNECT), pass_user_data=True),
                    ],
                },
                fallbacks=[],
            ),
            CommandHandler('all_users', all_users_admin),
            CommandHandler('help_admin', help_admin),
            CommandHandler('exit', exit_admin),
            MessageHandler(Filters.all, echo_admin),
        ],
    },
    fallbacks=[],
)

handlers['start'] = CommandHandler('start', start)
handlers['unauthorized'] = MessageHandler(Filters.all, unauthorized)

# todo front:
#  system initial config,
#  disconnect in inner conversation handlers
#
# todo back:
#  everything
#
# todo test:
#  alert while in inner conversation handlers
