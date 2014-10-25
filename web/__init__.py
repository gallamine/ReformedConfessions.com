from flask import Flask, session, render_template, request_started, abort
from werkzeug import SharedDataMiddleware
from werkzeug.routing import BaseConverter
from json import load
import itertools
import os

# create our application
app = Flask(__name__)

# Config
if app.config['DEBUG']:
    app.config.from_object('web.config.DevelopmentConfig')
    app.logger.info("Config: Development")
else:
    app.config.from_object('web.config.ProductionConfig')
    app.logger.info("Config: Production")


# Source: http://www.jeffff.com/serving-media-in-the-flask-local-dev-server:w
def serve_static(sender):
    if app.config['DEBUG']:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app,
                                            {'/': os.path.join(os.path.dirname(__file__), 'static')})

request_started.connect(serve_static, app)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


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
    documents = [
        ('wcf', "Westminster Confession of Faith"),
        ('wsc', "Westminster Shorter Catechsim"),
        ('wlc', "Westminster Larger Catechsim"),
    ]
    docs = list(itertools.izip(itertools.cycle(["link_a", "link_b", "link_c"]), documents))
    return render_template('page_t_home.html',
                           page_title="",
                           documents=docs)


@app.route('/about')
def page_about():
    return render_template('page_t_about.html',
                           page_title="About")


@app.route('/<regex("(wlc|wsc|wcf)"):doc_name>')
def page_document_index(doc_name):
    page_title = catechisms[doc_name]
    if doc_name == "wcf":
        chapters = sort_num_string(get_wcf().keys())
    elif doc_name in ["wsc", "wlc"]:
        chapters = sort_num_string(get_catechism(doc_name).keys())
    if chapters:
        return render_template('page_t_doc_index.html',
                               page_title=page_title,
                               abbr=doc_name,
                               chapters=chapters)
    else:
        abort(404)


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
    page_title = "Westminster Confession of Faith"
    title, paragraphs = get_wcf(chapter)
    if paragraphs:
        return render_template('page_t_wcf.html',
                               page_title=page_title,
                               chapter_title=title,
                               paragraphs=paragraphs)
    else:
        abort(404)


@app.route('/c/<regex("(wlc|wsc)"):catechism>/<question>')
def page_wlc_qa(catechism, question):

    page_title = catechisms[catechism]
    qas = get_catechism(catechism, num=question)
    if qas:
        return render_template('page_t_catechism.html',
                               page_title=page_title,
                               qas=qas)
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
            title = "Chapter %s: %s" % (chapter, wcf[chapter]["title"])
            section = [(section, wcf[chapter]["body"][section - 1])]
            return (title, section)
        except:
            return None
    elif chapter:
        chapter = str(chapter)
        try:
            title = "Chapter %s: %s" % (chapter, wcf[chapter]["title"])
            return (title, list(enumerate(wcf[chapter]["body"], 1)))
        except:
            return None
    else:
        return wcf


catechisms = {
    "wcf": "Westminster Confession of Faith",
    "wlc": "Westminster Larger Catechsim",
    "wsc": "Westminster Shorter Catechsim",
}


def get_catechism(name, num=None):
    root_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(root_path, "static/data/{}.json".format(name))
    with open(json_path, "r") as f:
        wlc = load(f)
    if num:
        num = str(num)
        try:
            return [(num, wlc[num][0], wlc[num][1])]
        except:
            return None
    else:
        return wlc


def sort_num_string(l):
    l = list(l)[:]
    l.sort(key=int)
    return l


class DoesNotExistException(Exception):
    pass
