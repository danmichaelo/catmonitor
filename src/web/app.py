from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from time import time
import re
import sqlite3

import simplejson as json
from flask import Flask
from flask import render_template

app = Flask(__name__)

HOME = '/data/project/catmonitor/'

def error_404():
    return '404'
    response = render_template('404.html')
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

    return render_template('main.html', projects=projects)


if __name__ == "__main__":
    app.run()
