from flask import (Flask, session, render_template,
                   request_started, abort, jsonify)
from werkzeug import SharedDataMiddleware
from werkzeug.routing import BaseConverter
import itertools
import os
import data

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
        return dict(site_title="ReformedConfessions.com")


@app.route('/')
def page_home():
    documents = list(data.catechisms.iteritems())
    docs = list(itertools.izip(itertools.cycle(["link_a", "link_b", "link_c"]), documents))
    return render_template('page_t_home.html',
                           page_title="ReformedConfessions.com",
                           documents=docs)


@app.route('/about')
def page_about():
    return render_template('page_t_about.html',
                           page_title="About")


@app.route('/<regex("(wlc|wsc|wcf)"):doc_name>')
def page_document_index(doc_name):
    page_title = data.catechisms[doc_name]
    if doc_name == "wcf":
        chapters = sort_num_string(data.get_wcf().data.keys())
    elif doc_name in ["wsc", "wlc"]:
        chapters = sort_num_string(data.get_catechism(doc_name).data.keys())
    if chapters:
        return render_template('page_t_doc_index.html',
                               page_title=page_title,
                               abbr=doc_name,
                               chapters=chapters)
    else:
        abort(404)


@app.route('/<regex("(json|c)"):request_type>/<regex("(wlc|wsc|wcf)"):catechism>/<question>')
@app.route('/<regex("(json|c)"):request_type>/<regex("(wlc|wsc|wcf)"):catechism>')
def json_doc_display(request_type, catechism, question=None):
    if catechism == "wcf":
        excerpt = data.get_wcf(question)
    elif catechism in ["wsc", "wlc"]:
        excerpt = data.get_catechism(catechism, question)
    if excerpt:
        if request_type == "json":
            return jsonify({excerpt.abbv: [excerpt]})
        else:
            return render_template('page_t_excerpts.html',
                                   excerpts=[excerpt])
    abort(404)


def sort_num_string(l):
    l = list(l)[:]
    l.sort(key=int)
    return l


class DoesNotExistException(Exception):
    pass
