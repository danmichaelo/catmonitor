#!/usr/bin/python

import cgitb
cgitb.enable()
#print 'Content-type: text/html; charset=utf-8\n'

import sqlite3

import logging
import logging.handlers
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

fh = logging.FileHandler('main.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

import os, sys
sys.path.insert(0, '/data/project/catmonitor/env/lib/python2.7/site-packages')

from werkzeug.wrappers import Response
#from werkzeug.contrib.fixers import CGIRootFix
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.utils import redirect
from werkzeug.contrib.fixers import CGIRootFix
from wsgiref.handlers import CGIHandler

import urllib
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
template_path = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

def render_template(template_name, **context): 
    t = jinja_env.get_template(template_name)
    return Response(t.render(context), mimetype='text/html')

def get_index(args):
    logger.info('GET_INDEX')   

    projects = [ { 'host': 'no.wikipedia.org', 'db': 'catmonitor.no.db' }, { 'host': 'nn.wikipedia.org', 'db': 'catmonitor.nn.db' }]

    for i, proj in enumerate(projects):
        sql = sqlite3.connect('../' + proj['db'])
        cur = sql.cursor()
        cur.execute(u'SELECT category, COUNT(article) FROM articles GROUP BY category')
        projects[i]['cats'] = [[r[0], r[1]] for r in cur.fetchall()]
        cur.close()

    return render_template('main.html', projects=projects)

def error_404(): 
    response = render_template('404.html') 
    response.status_code = 404 
    return response 

url_map = Map([
    Rule('/', endpoint='get_index'),
    ], default_subdomain='tools')


def application(environ, start_response):
    #logger.info(environ)
    environ['SCRIPT_NAME'] = '/catmonitor'
    try:
        urls = url_map.bind_to_environ(environ, server_name='wmflabs.org', subdomain='tools')
        endpoint, args = urls.match()
        logger.info(args)
        response = globals()[endpoint](args)
        return response(environ, start_response)
    except NotFound, e:
        response = error_404()
        return response(environ, start_response)
    except RequestRedirect, e:
        logger.info('Redir to: %s' % e.new_url)
        response = redirect(e.new_url)
        return response(environ, start_response)


try:
    CGIHandler().run(application)
except Exception as e:
    logger.exception('Unhandled Exception')
