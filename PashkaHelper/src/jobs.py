import datetime
import time
import pytz

from telegram.ext import CallbackContext, JobQueue, Job

from src.text import get_text
import src.common_functions as cf
import src.database as db

JOB_DATA = ('callback', 'interval', 'repeat', 'context', 'days', 'name', 'tzinfo')
JOB_STATE = ('_remove', '_enabled')


def mailing_job_callback(context: CallbackContext):
    job = context.job
    chat_id = job.context[0]
    user_id = job.context[1]
    language_code = job.context[2]
    notification_status = job.context[3]
    disable_notification = notification_status == 'disabled'
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('timetable_mailing_greeting_text', language_code).text(),
        disable_notification=disable_notification,
    )
    cf.send_today_timetable(
        context=context,
        chat_id=chat_id,
        user_id=user_id,
        language_code=language_code,
        disable_notification=disable_notification,
    )


def set_mailing_job(context: CallbackContext, chat_id, user_id, language_code):
    notification_status = db.get_user_attr('notification_status', user_id=user_id)
    job_name = 'job'
    if job_name not in context.chat_data:
        new_job = context.job_queue.run_daily(
            callback=mailing_job_callback,
            time=db.get_user_mailing_time_with_offset(user_id),
            days=(0, 1, 2, 3, 4, 5),
            context=[chat_id, user_id, language_code, notification_status],
            name=job_name,
        )
        context.chat_data[job_name] = new_job
        save_jobs_job(context)
        return new_job


def rm_mailing_job(context: CallbackContext):
    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        old_job.schedule_removal()
        del context.chat_data['job']
        save_jobs_job(context)


def reset_mailing(context: CallbackContext, chat_id, user_id, language_code):
    rm_mailing_job(context)
    set_mailing_job(context, chat_id, user_id, language_code)


def load_jobs(jq: JobQueue):
    dct = db.load_jobs()
    if dct.get('jobs') is None:
        return
    for next_t, data, state in dct.get('jobs'):
        # New object with the same data
        data['callback'] = globals()[data['callback']]
        time_td = datetime.datetime.strptime(data['interval'], '%d day, %H:%M:%S')
        data['interval'] = datetime.timedelta(
            days=time_td.day,
            hours=time_td.hour,
            minutes=time_td.minute,
            seconds=time_td.second,
        )
        data['days'] = tuple(data['days'])
        data['tzinfo'] = pytz.timezone(data['tzinfo'])

        job = Job(**data)

        # Restore the state it had
        for var, val in zip(JOB_STATE, state):
            attribute = getattr(job, var)
            getattr(attribute, 'set' if val else 'clear')()

        job.job_queue = jq

        next_t -= time.time()  # convert from absolute to relative time

        jq._put(job, next_t)


def save_jobs(jq: JobQueue):
    with jq._queue.mutex:  # in case job_queue makes a change

        if jq:
            job_tuples = jq._queue.queue
        else:
            job_tuples = []

        dct = {'jobs': []}
        for next_t, job in job_tuples:

            if job.name == 'util':
                continue

            # Threading primitives are not pickleable
            data = {var: getattr(job, var) for var in JOB_DATA}
            data['callback'] = data['callback'].__name__
            state = [getattr(job, var).is_set() for var in JOB_STATE]

            # Pickle the job
            dct['jobs'].append((next_t, data, state))

        db.save_jobs(dct)


def save_jobs_job(context):
    save_jobs(context.job_queue)
