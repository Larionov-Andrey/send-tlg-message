from bot import TG
from tasks import load_archive_tasks, add_task, del_task
from flask import Flask
from web import *
import os

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='templates', static_folder="static")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
app.register_blueprint(main_page)

def start():

    bot = TG()
    bot.create_session()

    load_archive_tasks()
    # del_task(1)
    # add_task('text2', images=[], channels=[], save=True)
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    start()
