from telegram import Update, ParseMode
from telegram.ext import CallbackContext, Filters, MessageHandler, CallbackQueryHandler, ConversationHandler, \
    CommandHandler

import FilmsBot.data as data
import FilmsBot.keyboard as keyboard
import FilmsBot.message as message
from log import log_handler

handlers = {}

commands = {}

LOG_IN, MAIN, CHANGING, ADD, LIST_USER, ADMIN_AUTH, CONTROL, ADD_USER = range(8)


@log_handler
def unauthorized(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.unauthorized_text,
        parse_mode=ParseMode.HTML,
    )
    return LOG_IN


@log_handler
def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.start_text,
        parse_mode=ParseMode.HTML,
    )
    return LOG_IN


@log_handler
def log_in(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.log_in_text,
        reply_markup=keyboard.usernames_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    return LOG_IN


@log_handler
def echo(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.echo_text,
        parse_mode=ParseMode.HTML,
    )
    return MAIN


@log_handler
def help_(update: Update, context: CallbackContext):
    text = message.help_text.format(data.get_link())
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    return MAIN


@log_handler
def auth(update: Update, context: CallbackContext):
    query = update.callback_query
    username = keyboard.keys_users[query.data]

    query.answer()
    keyboard.clear_keys_users()

    if data.user_authorized(username):
        chat_id = update.effective_chat.id
        if username == data.get_username(chat_id):
            query.edit_message_text(
                text=message.logged_in_text,
                parse_mode=ParseMode.HTML,
            )
            return
        query.edit_message_text(
            text=message.error_text,
            parse_mode=ParseMode.HTML,
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=message.bad_auth_text,
            reply_markup=keyboard.usernames_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        return

    data.add_to_auth(username)
    data.add_user_chat_id(update.effective_chat.id, username)

    query.edit_message_text(
        text=message.auth_text.format(username),
        parse_mode=ParseMode.HTML,
    )
    return MAIN


def callback_auth(update: Update, context: CallbackContext):
    query_data = update.callback_query.data
    if query_data in keyboard.keys_users.keys():
        return auth(update, context)
    return echo(update, context)


@log_handler
def log_out(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    data.rm_from_auth(data.get_username(chat_id))
    data.rm_chat_id(chat_id)
    context.bot.send_message(
        chat_id=chat_id,
        text=message.log_out_text,
        parse_mode=ParseMode.HTML,
    )
    return ConversationHandler.END


@log_handler
def to_tick(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.tick_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard.tick_keyboard(),
    )
    return CHANGING


@log_handler
def to_untick(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.untick_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard.untick_keyboard(),
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
    query = update.callback_query
    query.edit_message_reply_markup(
        reply_markup=keyboard.tick_keyboard(query.data)
    )
    return CHANGING


@log_handler
def untick(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup(
        reply_markup=keyboard.untick_keyboard(query.data)
    )
    return CHANGING


@log_handler
def complete_query(update: Update, context: CallbackContext):
    keyboard.done_marked_buttons()
    update.callback_query.edit_message_text(
        text=message.complete_text,
        parse_mode=ParseMode.HTML,
    )
    return ConversationHandler.END


@log_handler
def complete(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.complete_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ConversationHandler.END


@log_handler
def need_to_complete(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.need_to_complete_text,
        parse_mode=ParseMode.HTML,
    )
    return CHANGING


@log_handler
def to_add(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.add_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ADD


def add(update: Update, context: CallbackContext):
    data.add_films(update.message.text.split('\n'))
    return complete(update, context)


@log_handler
def to_remove(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.remove_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard.remove_keyboard(),
    )
    return CHANGING


@log_handler
def remove(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup(
        reply_markup=keyboard.remove_keyboard(query.data)
    )
    return CHANGING


@log_handler
def list_(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    text = message.make_list(data.get_films(data.get_username(chat_id)), message.self_films_list_text)

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return MAIN


@log_handler
def to_list_user(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.enter_username_list_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard.usernames_keyboard(),
    )
    return LIST_USER


@log_handler
def callback_list_user(update: Update, context: CallbackContext):
    query = update.callback_query

    name = keyboard.keys_users[query.data]
    text = message.make_list(
        data.get_films(name),
        message.user_films_list_text,
    ).format(name)
    # todo fix key_users

    query.edit_message_text(
        text=text,
    )
    keyboard.clear_keys_users()
    return ConversationHandler.END


@log_handler
def enter_username(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.bad_username_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return LIST_USER


@log_handler
def admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.auth_admin_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ADMIN_AUTH


@log_handler
def auth_admin(update: Update, context: CallbackContext):
    text = update.message.text
    if text == '/cancel':
        return exit_admin(update, context)
    if data.auth_admin(text.split('\n')):
        return help_admin(update, context)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.auth_admin_error_text,
        parse_mode=ParseMode.HTML,
    )
    return ADMIN_AUTH


@log_handler
def exit_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.exit_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ConversationHandler.END


@log_handler
def help_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.auth_admin_welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return CONTROL


@log_handler
def echo_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.echo_admin,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return CONTROL


@log_handler
def all_users_admin(update: Update, context: CallbackContext):
    text = message.users_list
    for user in data.get_users():
        text += user \
                + (message.user_authorized if data.user_authorized(user) else message.user_unauthorized) \
                + '\n\n'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return CONTROL


@log_handler
def to_add_user_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.add_user_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ADD_USER


def add_user_admin(update: Update, context: CallbackContext):
    text = update.message.text.split('\n')
    if len(text) < 2:
        return add_user_error_admin(update, context)
    username = text[0]
    password = text[1]
    if data.add_user(username, password):
        return done_admin(update, context)
    return add_user_error_admin(update, context)


@log_handler
def add_user_error_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.add_user_error_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ADD_USER


@log_handler
def done_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.done_admin_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ConversationHandler.END


@log_handler
def stop_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message.stop_admin_text,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )
    return ConversationHandler.END


handlers['main'] = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('log_in', log_in),
    ],
    states={
        LOG_IN: [
            CallbackQueryHandler(callback=callback_auth),
            CommandHandler('log_in', log_in),
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
            ConversationHandler(
                entry_points=[
                    CommandHandler('admin', admin),
                ],
                states={
                    ADMIN_AUTH: [
                        MessageHandler(Filters.all, auth_admin),
                    ],
                    CONTROL: [
                        ConversationHandler(
                            entry_points=[
                                CommandHandler('add_user', to_add_user_admin),
                            ],
                            states={
                                ADD_USER: [
                                    CommandHandler('stop_admin', stop_admin),
                                    MessageHandler(Filters.all, add_user_admin),
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
            ),
            CommandHandler('help', help_),
            CommandHandler('log_out', log_out),
            CommandHandler('list', list_),
            MessageHandler(Filters.all, echo),
        ]
    },
    fallbacks=[],
)

handlers['unauthorized'] = MessageHandler(Filters.all, unauthorized)
