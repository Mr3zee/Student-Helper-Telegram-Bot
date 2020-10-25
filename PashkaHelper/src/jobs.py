import datetime
import time

import pytz

from telegram.ext import CallbackContext, JobQueue, Job

import src.common_functions as cf
import src.database as db
import src.handler as hdl
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
    jq = context.job_queue._queue
    with jq.mutex:
        job_tuples = jq.queue
        old_job = None
        for next_t, job in job_tuples:
            if job.name == name and job.context[0] == chat_id and job.context[1] == user_id:
                old_job = job
                break
        return old_job


def set_mailing_job(context: CallbackContext, chat_id, user_id, language_code):
    """set mailing job, remove previous if exists"""

    # check if there is such job
    old_job = find_job(context, user_id=user_id, chat_id=chat_id, name=consts.MAILING_JOB)
    # remove it if there is one
    if old_job is not None:
        rm_mailing_job(context, user_id, chat_id, old_job)

    notification_status = db.get_user_attr('notification_status', user_id=user_id)
    new_job = context.job_queue.run_daily(
        callback=mailing_job,
        time=db.get_user_mailing_time_with_offset(user_id),
        days=(0, 1, 2, 3, 4, 5),
        context=[chat_id, user_id, language_code, notification_status],
        name=consts.MAILING_JOB,
    )
    save_jobs_job(context)
    return new_job


def rm_mailing_job(context: CallbackContext, user_id, chat_id, old_job=None):
    """remove mailing job if where was one"""
    if old_job is None:
        old_job = find_job(context, user_id=user_id, chat_id=chat_id, name=consts.MAILING_JOB)
    if old_job is not None:
        old_job.schedule_removal()
        save_jobs_job(context)


def load_jobs(jq: JobQueue):
    """load jobs from the database"""
    dct = db.load_jobs()

    # check if there are jobs in the database
    if dct.get(consts.JOBS) is None:
        return

    # iterate over all jobs
    for next_t, data, state in dct.get(consts.JOBS):
        # restore job's callback function by __name__
        data[consts.CALLBACK_JOB] = globals()[data[consts.CALLBACK_JOB]]

        # restore interval for jobs
        time_td = datetime.datetime.strptime(data[consts.INTERVAL_JOB], '%d day, %H:%M:%S')
        data[consts.INTERVAL_JOB] = datetime.timedelta(
            days=time_td.day,
            hours=time_td.hour,
            minutes=time_td.minute,
            seconds=time_td.second,
        )

        # convert days list -> tuple
        data[consts.DAYS_JOB] = tuple(data[consts.DAYS_JOB])

        # convert tzinfo str -> timezone
        data[consts.TZINFO_JOB] = pytz.timezone(data[consts.TZINFO_JOB])

        # recreate JOb
        job = Job(**data)

        # Restore the state job had
        for var, val in zip(consts.JOB_STATE, state):
            attribute = getattr(job, var)
            getattr(attribute, 'set' if val else 'clear')()

        # set job_queue for job
        job.job_queue = jq

        # convert from absolute to relative time
        next_t -= time.time()

        # put job into job queue
        jq._put(job, next_t)


def save_jobs(jq: JobQueue):
    """save all jobs to the database"""
    with jq._queue.mutex:
        job_tuples = jq._queue.queue

        dct = {consts.JOBS: []}
        for next_t, job in job_tuples:

            # check if its job that saves jobs
            if job.name == 'util':
                continue

            # get all job's attrs
            data = {var: getattr(job, var) for var in consts.JOB_DATA}

            # convert callback function into str to store
            data[consts.CALLBACK_JOB] = data[consts.CALLBACK_JOB].__name__

            # get job's states
            state = [getattr(job, var).is_set() for var in consts.JOB_STATE]

            # _removed attr
            if not state[0]:
                dct[consts.JOBS].append((next_t, data, state))
        db.save_jobs(dct)


def save_jobs_job(context):
    """function for jobs auto update job"""
    save_jobs(context.job_queue)
