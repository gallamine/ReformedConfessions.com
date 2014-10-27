import simplejson as json
import os
from collections import namedtuple, OrderedDict


catechisms = {
    "wcf": "Westminster Confession of Faith",
    "wlc": "Westminster Larger Catechsim",
    "wsc": "Westminster Shorter Catechsim",
}


Excerpt = namedtuple("Excerpt", "abbv doc_title data")


def get_wcf(chapter=None, sections=None):
    root_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(root_path, "static/data/{}.json".format("wcf"))
    with open(json_path, "r") as f:
        wcf = json.load(f, object_pairs_hook=OrderedDict)

    if chapter and sections:
        if isinstance(sections, basestring) or isinstance(sections, int):
            sections = [str(sections)]
        try:
            wcf[chapter]["body"] = {section: wcf[chapter]["body"][section] for section in sections}
            d = {chapter: wcf[chapter]}

        except Exception as e:
            print e
    elif chapter:
        chapter = str(chapter)
        d = {chapter: wcf[chapter]}
    else:
        d = wcf
    return Excerpt("wcf", "Westminster Confession of Faith", d)


def get_catechism(name, questions=None):
    root_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(root_path, "static/data/{}.json".format(name))
    with open(json_path, "r") as f:
        # catechism = json.load(f, object_pairs_hook=lambda x: OrderedDict(x, key=lambda y: int(y[0])))
        catechism = json.load(f, object_pairs_hook=OrderedDict)
    if questions:
        if isinstance(questions, basestring) or isinstance(questions, int):
            questions = [questions]
        questions = map(str, questions)
        try:
            catechism = {question: catechism[question] for question in questions}
        except Exception as e:
            print e
    return Excerpt(name, catechisms[name], catechism)
