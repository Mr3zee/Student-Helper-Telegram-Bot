from telegram.ext import CallbackContext

import keyboard
import user_parameters
from timetable import get_timetable_by_index, BOTH_ATTENDANCE
from time_management import get_weekday


def send_today_timetable(context: CallbackContext, chat_id, language_code):
    context.bot.send_message(
        chat_id=chat_id,
        text=get_timetable_by_index(
            day=get_weekday(),
            attendance=BOTH_ATTENDANCE,
            language_code=language_code,
        ),
        reply_markup=keyboard.timetable_keyboard(language_code=language_code),
    )


def send_morning_message(context: CallbackContext):
    job = context.job
    send_today_timetable(
        context=context,
        chat_id=job.context[0],
        language_code=job.context[1]
    )


def set_morning_message(context: CallbackContext, chat_id, user_id, language_code):
    job_name = 'job'
    if job_name not in context.chat_data:
        new_job = context.job_queue.run_daily(
            callback=send_morning_message,
            time=user_parameters.get_user_time(user_id),
            days=(0, 1, 2, 3, 4, 5),
            context=[chat_id, language_code],
            name=job_name,
        )
        context.chat_data[job_name] = new_job
        return new_job


def rm_morning_message(context: CallbackContext):
    old_job = context.chat_data['job']
    old_job.schedule_removal()
    del context.chat_data['job']
