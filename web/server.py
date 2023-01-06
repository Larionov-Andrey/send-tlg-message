import os
from datetime import datetime

from flask import Flask, render_template, request, Blueprint, url_for, redirect, session
from flask_paginate import Pagination

from tasks import add_task, tasks, active_tasks, del_task, send_message as send_tg_message
from utils import gen_unic_filename

# from main import app
main_page = Blueprint('', __name__, template_folder='templates')

PER_PAGE = 5


@main_page.route("/")
def index():
    from tasks import active_tasks
    items = []
    for item in active_tasks:
        items.append(
            {
                "id": item['id'],
                "main_img": item['images'][0] if len(item['images']) > 0 else None,
                "other_img": item['images'][1:] if len(item['images']) > 0 else None,
                "title": item['text'].split('\n')[0],
                "text": '\n'.join(item['text'].split('\n')[1:]),
                "date": item['date'].strftime("%d.%m.%Y, %H:%M:%S")
            }
        )

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    i = (page - 1) * PER_PAGE
    if len(items) >= PER_PAGE:
        items_pagination = items[i:i + PER_PAGE]
    else:
        items_pagination = items

    pagination = Pagination(page=page, per_page=PER_PAGE, total=len(items), record_name='items',
                            css_framework='bootstrap4')

    return render_template('message-queue.html', items=items_pagination, pagination=pagination)


@main_page.route("/del/<int:id>", )
def del_message(id):
    global active_tasks
    active_tasks = del_task(id)
    return redirect(url_for('index'))


@main_page.route("/edit/<int:id>", methods=('GET', 'POST'))
def edit_message(id):
    global active_tasks
    task = None
    for item in active_tasks:
        if item['id'] == id:
            task = {
                "id": item['id'],
                "title": item['text'].split('\n')[0],
                "text": '\n'.join(item['text'].split('\n')[1:]),
                "date": item['date'].strftime("%Y-%m-%dT%H:%M"),
                "channels": '\n'.join(item["channels"]),
                "images": item['images']
            }
            break

    if request.method == 'POST':
        filenames = []
        for f in request.files.getlist('images'):
            filename = gen_unic_filename(f.filename)
            if len(f.filename.split('.')) < 2:
                continue
            filenames.append('/uploads/' + filename)
        if len(filenames) == 0:
            session['images'] = task['images']

        active_tasks = del_task(task['id'])
        return redirect(url_for('send_message'), code=307)
    else:
        return render_template('send-messages.html', item=task, edit=True)


@main_page.route("/send-messages/", methods=('GET', 'POST'))
def send_message():
    if request.method == 'POST':
        try:
            force = int(request.args.get('force', 0))
        except ValueError:
            force = 0

        form = request.form
        task = {
            'title': form['title'],
            'text': form['text'],
            'channels': form['channels'].replace('\r', '').split('\n'),
            'date': datetime.strptime(form['date'], "%Y-%m-%dT%H:%M"),
            'period': form['period'] if form.get('repeat') else 'single',
            'additional_dates': []
        }
        c = 1
        while True:
            if form.get(f'date-{c}'):
                task['additional_dates'].append({
                    'date': datetime.strptime(form[f'date-{c}'], "%Y-%m-%dT%H:%M"),
                    'period': form.get(f'period-{c}', 'single') if form.get(f'repeat-{c}') else 'single'
                })
                c += 1
            else:
                break

        files = request.files.getlist('images')
        filenames = []
        from main import app

        for f in files:
            filename = gen_unic_filename(f.filename)
            if len(f.filename.split('.')) < 2:
                continue
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenames.append('/uploads/' + filename)

        if len(filenames) == 0:
            filenames = session['images']
            session['images'] = []

        text = f"{task['title']}\n{task['text']}"
        if force == 1:
            send_tg_message(text, filenames.copy(), task['channels'], force=True)

        add_task(len(tasks), text, filenames.copy(), task['channels'], task['date'], period=task['period'],
                 additional_dates=task['additional_dates'], save=True)

        return redirect(url_for('index'))
    else:
        return render_template('send-messages.html')
