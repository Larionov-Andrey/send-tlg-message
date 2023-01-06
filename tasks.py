import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from bot import TG
from rw import load_json, write_json

tasks = []
active_tasks = []
archive_path = './data/tasks.json'


def print_date_time():
    print('startr')
    time.sleep(60)
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def send_message(text, images=None, channels=[], auto_del=False, task_id=0, date=datetime.now(), day_period=1,
                 force=False):
    if (datetime.now() - date).days % day_period == 0 or force:

        bot = TG()

        for channel in channels:
            bot.send_message(text, channel, media=images)

        if auto_del:
            del_task(task_id)


def add_task(task_id, text, images, channels, date=datetime.now(), period='single', additional_dates=[], save=False,
             active=True):
    global tasks
    auto_del = False
    day_period = 1
    day_of_week = None

    if period == 'single':
        auto_del = True
    elif period == '2_day':
        day_period = 2
    elif period == '3_day':
        day_period = 3
    elif period == '4_day':
        day_period = 4
    elif period == '5_day':
        day_period = 5
    elif period == '6_day':
        day_period = 6
    elif period == '7_day':
        day_period = 7
    elif period == 'week':
        day_period = 8
    elif period == '7_day':
        day_of_week = 'mon'
    elif period == '7_day':
        day_of_week = 'tue'
    elif period == 'wed':
        day_of_week = 'wed'
    elif period == 'thu':
        day_of_week = 'thu'
    elif period == 'fri':
        day_of_week = 'fri'
    elif period == 'sat':
        day_of_week = 'sat'
    elif period == 'sun':
        day_of_week = 'sun'

    task = scheduler.add_job(func=send_message, trigger="cron", start_date=date.date(), hour=date.hour,
                             minute=date.minute, day_of_week=day_of_week, args=(text,),
                             kwargs={'images': images, 'channels': channels, 'auto_del': auto_del, 'task_id': task_id,
                                     'date': date, 'day_period': day_period})
    if len(additional_dates) != 0:
        for add_data in additional_dates:
            add_task(task_id, text, images, channels,
                     date=add_data.get('date', datetime.now()),
                     period=add_data.get('period', 'single'), active=False)

    if active:
        active_tasks.append(
            {
                'id': len(active_tasks),
                'text': text,
                'images': images,
                'channels': channels,
                'date': date,
                'period': period
            }
        )
    if save:
        archive = load_json(archive_path)
        archive.append({
            'id': len(archive),
            'text': text,
            'images': images,
            'channels': channels,
            'date': date.timestamp(),
            'period': period,
            'additional_dates': [{'date': i['date'].timestamp(), 'period': i.get('period', 'single')} for i in
                                 additional_dates]
        })
        write_json(archive_path, archive)
        tasks.append({'task': task, 'id': len(archive)})
    return task


def del_task(task_id):
    global tasks, active_tasks
    # print(active_tasks)
    archive_tasks = load_json(archive_path)
    archive_tasks_buff = []
    for i in archive_tasks:
        if i['id'] != task_id:
            archive_tasks_buff.append(i)
    write_json(archive_path, archive_tasks_buff)

    tasks_buff = []
    for i in tasks:
        if i['id'] != task_id:
            tasks_buff.append(i)
        else:
            i['task'].remove()

    tasks = tasks_buff
    tasks_buff = []
    for i in active_tasks:
        if i['id'] != task_id:
            tasks_buff.append(i)
    active_tasks = tasks_buff
    return active_tasks
    # print(active_tasks)


def load_archive_tasks():
    global tasks
    archive_tasks = load_json(archive_path)
    for task in archive_tasks:
        date = datetime.fromtimestamp(task['date'])
        tasks.append(
            {'task': add_task(
                task_id=task['id'],
                text=task['text'],
                images=task['images'],
                channels=task['channels'],
                date=date,
                period=task['period'],
                additional_dates=[
                    {'date': datetime.fromtimestamp(i['date']), 'period': i.get('period', 'single')} for i in
                    task['additional_dates']],
                save=False),
             'id': task['id']})

scheduler = BackgroundScheduler(timezone='Europe/Moscow')
# scheduler.add_job(print_date_time, "interval", seconds=10)
scheduler.start()
