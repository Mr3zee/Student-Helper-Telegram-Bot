import datetime

from telegram.ext import CallbackContext, JobQueue, Job

import src.common_functions as cf
import src.database as db
import src.handler as hdl
import src.time_management as tm
from static import consts


def nullify_conversations(user_id, chat_id):
    """set all conversation states to MAIN_STATE"""
    key = (user_id, chat_id)
    hdl.handlers['main'].update_state(consts.MAIN_STATE, key)


def mailing_job(context: CallbackContext):
    """
    Sends everyday mailing with timetable
    job.context:
     - [0]: chat_id
     - [1]: user_id
     - [2]: language_code
     - [3]: notification_status
    """
    job = context.job
    # get parameters
    chat_id = job.context[0]
    user_id = job.context[1]
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
    )


def find_job(context: CallbackContext, name, chat_id, user_id):
    """find user's job by name"""
    jq: JobQueue = context.job_queue
    job_tuples = jq.get_jobs_by_name(consts.MAILING_JOB)
    old_job = None
    for job in job_tuples:
        print(job.name, job.enabled, job.removed, job.next_t)
        if job.name == name and job.context[0] == chat_id and job.context[1] == user_id:
            old_job = job
            break
    return old_job


def add_mailing_job(jq: JobQueue, user_id, mailing_time, utcoffset, notification_status, chat_id, language_code):
    """adds new mailing job to JobQueue"""
    return
    # todo fix
    # get job time
    job_time = tm.to_utc_converter(
        input_date=datetime.datetime.strptime(mailing_time, '%H:%M'),
        utcoffset=datetime.timedelta(hours=utcoffset),
    ).time()
    # add job
    new_job = jq.run_daily(
        callback=mailing_job,
        time=job_time,
        days=(0, 1, 2, 3, 4, 5),
        context=[chat_id, user_id, language_code, notification_status],
        name=consts.MAILING_JOB,
    )
    return new_job


def set_mailing_job(context: CallbackContext, chat_id, user_id, language_code):
    """set mailing job, remove previous if exists"""
    return
    # todo fix
    # check if there is such job
    old_job = find_job(context, user_id=user_id, chat_id=chat_id, name=consts.MAILING_JOB)
    # remove it if there is one
    if old_job is not None:
        rm_mailing_job(context, user_id, chat_id, old_job)

    mailing_time, utcoffset, notification_status = db.get_user_attrs(
        attrs_names=[consts.MAILING_TIME, consts.UTCOFFSET, consts.NOTIFICATION_STATUS],
        user_id=user_id,
    ).values()

    return add_mailing_job(
        jq=context.job_queue,
        user_id=user_id, chat_id=chat_id,
        mailing_time=mailing_time, utcoffset=utcoffset,
        notification_status=notification_status,
        language_code=language_code,
    )


def rm_mailing_job(context: CallbackContext, user_id, chat_id, old_job: Job = None):
    """remove mailing job if where was one"""
    return
    # todo fix
    if old_job is None:
        old_job = find_job(context, user_id=user_id, chat_id=chat_id, name=consts.MAILING_JOB)
    if old_job is not None:
        old_job.schedule_removal()


def load_jobs(jq: JobQueue):
    """load jobs from the database"""
    return
    # todo fix
    dct = db.get_jobs_info()

    for user_id, params in dct.items():
        add_mailing_job(
            jq=jq,
            user_id=user_id, chat_id=params[3],
            mailing_time=params[0],
            utcoffset=params[1],
            notification_status=params[2],
            language_code='ru',
        )
