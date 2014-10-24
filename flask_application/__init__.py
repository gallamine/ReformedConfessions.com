from flask import Flask, session, render_template, request_started, abort
from werkzeug import SharedDataMiddleware
from json import load
import os

# create our application
app = Flask(__name__)

# Config
if app.config['DEBUG']:
    app.config.from_object('flask_application.config.DevelopmentConfig')
    app.logger.info("Config: Development")
else:
    app.config.from_object('flask_application.config.ProductionConfig')
    app.logger.info("Config: Production")


# Source: http://www.jeffff.com/serving-media-in-the-flask-local-dev-server:w
def serve_static(sender):
    if app.config['DEBUG']:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app,
                                            {'/': os.path.join(os.path.dirname(__file__), 'static')})

request_started.connect(serve_static, app)


@app.before_request
def before_request():
    session["debug"] = app.debug


@app.after_request
def after_request(response):
    return response


@app.context_processor
def inject_site_defaults():
        return dict(site_title="Reformed Confessions")


@app.route('/')
def page_home():
    wcf_chapters = get_wcf().keys()
    wcf_chapters.sort(key=int)
    documents = {
        ('wcf', "Westminster Confession of Faith"): wcf_chapters
    }
    return render_template('page_t_home.html',
                           page_title="Home",
                           documents=documents)


@app.route('/c/wcf/<chapter>/<section>')
def page_wcf_chapter_section(chapter, section):
    page_title = "Westminster Confession of Faith %s.%s" % (chapter, section)
    title, paragraphs = get_wcf(chapter, section)
    if paragraphs:
        return render_template('page_t_wcf.html',
                               page_title=page_title,
                               chapter_title=title,
                               paragraphs=paragraphs)
    else:
        abort(404)


@app.route('/c/wcf/<chapter>')
def page_wcf_chapter(chapter):
    page_title = "Westminster Confession of Faith %s" % (chapter)
    title, paragraphs = get_wcf(chapter)
    if paragraphs:
        return render_template('page_t_wcf.html',
                               page_title=page_title,
                               chapter_title=title,
                               paragraphs=paragraphs)
    else:
        abort(404)


def get_wcf(chapter=None, section=None):
    root_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(root_path, "static/data/wcf.json")
    with open(json_path, "r") as f:
        wcf = load(f)

    if chapter and section:
        chapter = str(chapter)
        section = int(section)
        try:
            return (wcf[chapter]["title"], [wcf[chapter]["body"][section - 1]])
        except:
            return None
    elif chapter:
        chapter = str(chapter)
        try:
            return (wcf[chapter]["title"], wcf[chapter]["body"])
        except:
            return ["asdf"]
    else:
        return wcf



class DoesNotExistException(Exception):
    pass
