import datetime

from telegram.ext import CallbackContext, JobQueue, Job

import src.common_functions as cf
import src.database as db
import src.handler as hdl
import src.time_management as tm
from static import consts
from src.quote import random_quote


def nullify_conversations(user_id, chat_id):
    """set all conversation states to MAIN_STATE"""
    key = (user_id, chat_id)
    hdl.handlers['main'].update_state(consts.MAIN_STATE, key)


def mailing_job(context: CallbackContext):
    """
    Sends everyday mailing with timetable
    job.context:
     - [0]: user_id
     - [1]: chat_id
     - [2]: language_code
     - [3]: notification_status
    """

    job = context.job

    # check notification status
    user_id = job.context[0]
    if db.get_user_attr(consts.MAILING_STATUS, user_id=user_id) != consts.MAILING_ALLOWED:
        return

    # get other parameters
    chat_id = job.context[1]
    language_code = job.context[2]
    notification_status = job.context[3]
    disable_notifications = notification_status == consts.NOTIFICATION_DISABLED

    # exit all conversations to avoid collisions
    nullify_conversations(user_id, chat_id)

    cf.send_today_timetable(
        context=context,
        chat_id=chat_id,
        user_id=user_id,
        language_code=language_code,
        disable_notifications=disable_notifications,
        footer=f'\n{random_quote(language_code)}',
    )


def get_job_attrs(user_id):
    """get job_time and notification status for user"""
    mailing_time, utcoffset, notification_status = db.get_user_attrs(
        attrs_names=[consts.MAILING_TIME, consts.UTCOFFSET, consts.NOTIFICATION_STATUS],
        user_id=user_id,
    ).values()

    job_time = tm.to_utc_converter(
        input_date=datetime.datetime.strptime(mailing_time, '%H:%M'),
        utcoffset=datetime.timedelta(hours=utcoffset),
    ).time()

    return job_time, notification_status


def set_mailing_job(job_queue: JobQueue, user_id, chat_id, language_code):
    """set new mailing job"""

    job_time, notification_status = get_job_attrs(user_id)

    job_queue.run_daily(
        callback=mailing_job,
        time=job_time,
        days=(0, 1, 2, 3, 4, 5),
        context=[user_id, chat_id, language_code, notification_status],
        name=consts.MAILING_JOB,
    )


def rm_mailing_jobs(job_queue: JobQueue, user_id, chat_id):
    """remove all mailing jobs if where were such"""
    for job in job_queue.get_jobs_by_name(name=consts.MAILING_JOB):  # type: Job
        if job.context[0] == chat_id and job.context[1] == user_id:
            job.schedule_removal()


def reset_mailing_job(context: CallbackContext, user_id, chat_id, language_code):
    """delete all deprecated jobs, set new if needed"""
    jq = context.job_queue
    rm_mailing_jobs(jq, user_id, chat_id)
    if db.get_user_attr('mailing_status', user_id=user_id) == consts.MAILING_ALLOWED:
        set_mailing_job(jq, user_id, chat_id, language_code)


def load_jobs(jq: JobQueue):
    """load jobs from the database"""
    users = db.get_all_users()
    for user in users:
        user_id = user[0]
        chat_id = user[2]
        language_code = user[3]
        set_mailing_job(jq, user_id, chat_id, language_code)
