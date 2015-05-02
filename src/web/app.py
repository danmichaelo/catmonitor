from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from time import time
import re
import os
import oursql

import json
import flask
from flask import request

app = flask.Flask(__name__)

HOME = '/data/project/catmonitor/'

@app.errorhandler(404)
def error_404(e):
    response = flask.jsonify(error='invalid route', route=request.path)
    response.status_code = 404
    return response

@app.route('/catmonitor/api')
def show_api():

    configs = ['config.no.json', 'config.nn.json']
    projects = []

    for configfile in configs:
        config = json.load(open(HOME + configfile, 'r'))
        sql = oursql.connect(host=config['local_db']['host'],
                             db=config['local_db']['db'],
                             charset='utf8',
                             use_unicode=True,
                             read_default_file=os.path.expanduser('~/replica.my.cnf'))
        cur = sql.cursor()
        cur2 = sql.cursor()
        cur.execute(u'SELECT category, COUNT(article) FROM articles GROUP BY category')
        cats = []
        for cat in cur.fetchall():
            cur2.execute(u'SELECT membercount, ts FROM stats WHERE category=? ORDER BY ts DESC LIMIT 20', [cat[0]])
            stats = []
            for s in cur2.fetchall():
                stats.append({'value': s[0], 'timestamp': s[1]})
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
