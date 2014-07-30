from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from time import time
import re
import sqlite3

import simplejson as json
import flask

app = flask.Flask(__name__)

HOME = '/data/project/catmonitor/'

def error_404():
    return '404'
    response = flask.render_template('404.html')
    response.status_code = 404
    return response


@app.route('/')
def show_index():

    configs = ['config.no.json', 'config.nn.json']
    projects = []

    for configfile in configs:
        config = json.load(open(HOME + configfile, 'r'))
        sql = sqlite3.connect(HOME + config['local_db'])
        cur = sql.cursor()
        cur.execute(u'SELECT category, COUNT(article) FROM articles GROUP BY category')
        p = {
            'host': config['host'],
            'template': config['template'],
            'cats': [[r[0], r[1]] for r in cur.fetchall()]
        }
        projects.append(p)
        cur.close()

    return flask.render_template('main.html', projects=projects)


@app.route('/api')
def show_api():

    configs = ['config.no.json', 'config.nn.json']
    projects = []

    for configfile in configs:
        config = json.load(open(HOME + configfile, 'r'))
        sql = sqlite3.connect(HOME + config['local_db'])
        cur = sql.cursor()
        cur2 = sql.cursor()
        cur.execute(u'SELECT category, COUNT(article) FROM articles GROUP BY category')
        cats = []
        for cat in cur.fetchall():
            cur2.execute(u'SELECT membercount, ts FROM stats WHERE category=? ORDER BY ts DESC LIMIT 20', [cat[0]])
            stats = cur2.fetchall()
            cats.append({'name': cat[0], 'membercount': stats})
        p = {
            'host': config['host'],
            'template': config['template'],
            'categories': cats
        }
        projects.append(p)
        cur.close()
        cur2.close()

    return flask.jsonify(projects=projects)


if __name__ == "__main__":
    app.run()
