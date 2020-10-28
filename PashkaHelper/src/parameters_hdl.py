from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, CommandHandler

from src.text import get_text
from static import consts, buttons

from src import keyboard, database, common_functions as cf, jobs


def parameters(update: Update, context: CallbackContext):
    """start parameters conversation"""
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('main_parameters_text', language_code).text(database.get_user_parameters(user_id, language_code)),
        reply_markup=keyboard.parameters_keyboard(language_code),
    )
    return consts.PARAMETERS_MAIN_STATE


def __chg_parameters_page(update: Update, page_name, language_code, parameters_keyboard=None,
                          ret_lvl=consts.PARAMETERS_MAIN_STATE):
    """change parameters page for specified value"""
    user_id = update.effective_user.id
    text = get_text(f'{page_name}_parameters_text', language_code)
    user_info = database.get_user_parameters(user_id, language_code)
    text = text.text(user_info)
    cf.edit_message(
        update=update,
        text=text,
        reply_markup=(parameters_keyboard(language_code) if parameters_keyboard else None),
    )
    return ret_lvl


def parameters_callback(update: Update, context: CallbackContext):
    """manage all callbacks in parameters"""
    data, language_code = cf.manage_callback_query(update)
    if data == buttons.EXIT_PARAMETERS:
        cf.edit_message(
            update=update,
            text=get_text('exit_parameters_text', language_code).text(),
        )
        return consts.MAIN_STATE
    elif data in buttons.MAIN_SET:
        return __main_callback(update, context, data, language_code)
    elif data in buttons.COURSES_SET:
        return __chg_course(update, context, data, language_code)
    elif buttons.is_course_update(data):
        return __update_course(update, context, data, language_code)
    elif data in buttons.ATTENDANCE_SET:
        return __update_attendance(update, context, data, language_code)
    elif data in buttons.MAILING_SET:
        return __update_mailing_timetable(update, context, data, language_code)
    else:
        raise ValueError(f'invalid callback for parameters: {data}')


def __main_callback(update: Update, context: CallbackContext, data, language_code):
    """show specified page to change parameters"""
    if data == buttons.PARAMETERS_RETURN:
        return __return_callback(update, context, language_code)
    elif data == buttons.EVERYDAY_MESSAGE:
        return __mailing_callback(update, context, language_code)
    elif data == buttons.COURSES:
        return __chg_parameters_page(update, consts.COURSES, language_code, keyboard.courses_keyboard)
    elif data == buttons.NAME:
        return __chg_parameters_page(update, consts.ENTER_NAME, language_code=language_code,
                                     ret_lvl=consts.PARAMETERS_NAME_STATE)
    elif data == buttons.ATTENDANCE:
        return __chg_parameters_page(update, consts.ATTENDANCE, language_code, keyboard.attendance_keyboard)
    else:
        raise ValueError(f'invalid callback for main parameters page: {data}')


def __return_callback(update: Update, context: CallbackContext, language_code):
    """show main parameters page"""
    user_id = update.effective_user.id
    cf.edit_message(
        update=update,
        text=get_text('main_parameters_text', language_code).text(database.get_user_parameters(user_id, language_code)),
        reply_markup=keyboard.parameters_keyboard(language_code),
    )
    return consts.PARAMETERS_MAIN_STATE


def __get_mailing_page(update: Update, language_code):
    """get mailing page attrs"""
    user_id = update.effective_user.id
    attrs = database.get_user_attrs(
        [consts.MAILING_STATUS, consts.NOTIFICATION_STATUS],
        user_id=user_id,
    )
    text = get_text('mailing_parameters_text', language_code).text(
        database.get_user_parameters(user_id, language_code)
    )
    reply_markup = keyboard.mailing_keyboard(attrs[consts.MAILING_STATUS], attrs[consts.NOTIFICATION_STATUS],
                                             language_code)
    return text, reply_markup


def __mailing_callback(update: Update, context: CallbackContext, language_code):
    """show mailing menu"""
    text, reply_markup = __get_mailing_page(update, language_code)
    cf.edit_message(
        update=update,
        text=text,
        reply_markup=reply_markup,
    )
    return consts.PARAMETERS_MAIN_STATE


def __get_button_vars(data: str):
    """get parameters from button callback"""
    data = data.split('_')[:-1]
    return data[0], '_'.join(data[1:])


def __update_course(update: Update, context: CallbackContext, data, language_code):
    """update courses info or change eng page"""
    if data == buttons.ENG_NEXT:
        return __chg_parameters_page(update, consts.ENG, language_code, keyboard.eng2_keyboard)
    elif data == buttons.ENG_PREV:
        return __chg_parameters_page(update, consts.ENG, language_code, keyboard.eng1_keyboard)

    user_id = update.effective_user.id
    subject, subtype = __get_button_vars(data)
    database.set_user_attrs(user_id=user_id, attrs={subject: subtype})

    # show courses parameters page
    return __chg_parameters_page(update, consts.COURSES, language_code, keyboard.courses_keyboard)


def __chg_course(update: Update, context: CallbackContext, data, language_code):
    """select courses page"""
    if data == buttons.OS_TYPE:
        return __chg_parameters_page(update, consts.OS, language_code, keyboard.os_keyboard)
    elif data == buttons.SP_TYPE:
        return __chg_parameters_page(update, consts.SP, language_code, keyboard.sp_keyboard)
    elif data == buttons.HISTORY_GROUP:
        return __chg_parameters_page(update, consts.HISTORY, language_code, keyboard.history_keyboard)
    elif data == buttons.ENG_GROUP:
        return __chg_parameters_page(update, consts.ENG, language_code, keyboard.eng1_keyboard)
    elif data == buttons.COURSES_RETURN:
        return __chg_parameters_page(update, consts.COURSES, language_code, keyboard.courses_keyboard)
    else:
        raise ValueError(f'invalid callback for courses parameters page: {data}')


def __update_attendance(update: Update, context: CallbackContext, data, language_code):
    """update attendance"""
    user_id = update.effective_user.id
    new_attendance, _ = __get_button_vars(data)
    database.set_user_attrs(user_id=user_id, attrs={consts.ATTENDANCE: new_attendance})
    # show main parameters page
    return __return_callback(update, context, language_code)


def set_new_name_parameters(update: Update, context: CallbackContext):
    """update name"""
    user_id = update.effective_user.id
    new_name = update.message.text
    database.set_user_attrs(user_id=user_id, attrs={consts.USERNAME: new_name})
    # send main parameters page
    return parameters(update, context)


def __update_mailing_timetable(update: Update, context: CallbackContext, data, language_code):
    """changing mailing parameters"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # request user input
    if data == buttons.TZINFO:
        return __chg_parameters_page(update, consts.ENTER_TZINFO, language_code=language_code,
                                     ret_lvl=consts.PARAMETERS_TZINFO_STATE)
    elif data == buttons.MESSAGE_TIME:
        return __chg_parameters_page(update, consts.ENTER_TIME, language_code=language_code,
                                     ret_lvl=consts.PARAMETERS_TIME_STATE)

    #
    if data in {buttons.ALLOW_MAILING, buttons.FORBID_MAILING}:
        attr = consts.MAILING_STATUS
        new_status = (
            consts.MAILING_ALLOWED
            if data == buttons.ALLOW_MAILING
            else consts.MAILING_FORBIDDEN
        )
    elif data in {buttons.DISABLE_MAILING_NOTIFICATIONS, buttons.ENABLE_MAILING_NOTIFICATIONS}:
        attr = consts.NOTIFICATION_STATUS
        new_status = (
            consts.NOTIFICATION_ENABLED
            if data == buttons.ENABLE_MAILING_NOTIFICATIONS
            else consts.NOTIFICATION_DISABLED
        )
    else:
        raise ValueError(f'Invalid data in mailing set: {data}')
    database.set_user_attrs(user_id=user_id, attrs={attr: new_status})
    jobs.reset_mailing_job(context, user_id, chat_id, language_code)

    # update mailing page
    return __mailing_callback(update, context, language_code)


def __user_time_input_chg(update: Update, context: CallbackContext, validation, attr_name, error_state):
    """change mailing parameters with validation"""

    language_code = update.effective_user.language_code
    new_info = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # validate new_info. if False send error message and try again
    if validation(new_info):
        # update database
        database.set_user_attrs(user_id=user_id, attrs={attr_name: new_info})

        # reset mailing job
        jobs.reset_mailing_job(context, user_id, chat_id, language_code)

        # get and send mailing page
        text, reply_markup = __get_mailing_page(update, language_code)
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )
        return consts.PARAMETERS_MAIN_STATE
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('format_error_parameters_text', language_code).text(),
    )
    return error_state


def tzinfo_parameters(update: Update, context: CallbackContext):
    """set new tzinfo"""
    return __user_time_input_chg(
        update=update,
        context=context,
        validation=database.valid_utcoffset,
        attr_name=consts.UTCOFFSET,
        error_state=consts.PARAMETERS_TZINFO_STATE,
    )


def time_message_parameters(update: Update, context: CallbackContext):
    """set new mailing time"""
    return __user_time_input_chg(
        update=update,
        context=context,
        validation=database.valid_time,
        attr_name=consts.MAILING_TIME,
        error_state=consts.PARAMETERS_TIME_STATE,
    )


def parameters_error(name):
    """template for error handlers in the parameters"""

    def error(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(f'{name}_parameters_error_text', language_code).text(),
        )

    return MessageHandler(callback=error, filters=Filters.all)


# exit parameters
exit_parameters = cf.simple_handler(
    name='exit_parameters',
    command='exit',
    type=consts.COMMAND,
    ret_state=consts.MAIN_STATE,
)

# cancel operation and return to menu
cancel_parameters = CommandHandler(command='cancel', callback=parameters)
