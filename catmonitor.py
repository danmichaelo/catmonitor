#!/usr/bin/env python
# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- vim:fenc=utf-8:ft=python:et:sw=4:ts=4:sts=4

import mwclient
import os, oursql, sqlite3, re
import time
from progressbar import ProgressBar, Percentage, Bar, ETA, SimpleProgress, Counter
from datetime import datetime
from danmicholoparser import TemplateEditor
from wp_private import botlogin, mailfrom, mailto
import logging
import logging.handlers

template_name = u'Bruker:DanmicholoBot/Kategoriovervåkning'
edit_summary = 'Oppdaterer liste over nye artikler'
host = 'no.wikipedia.org'
mysql_host = 'nowiki-p.rrdb.toolserver.org'
mysql_db = 'nowiki_p'
maxcats = 10000

sql = sqlite3.connect('catmonitor.db')
no = mwclient.Site(host)
no.login(*botlogin)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

smtp_handler = logging.handlers.SMTPHandler( mailhost = ('localhost', 25),
                fromaddr = mailfrom, toaddrs = mailto, 
                subject=u"[toolserver] CatMonitor crashed!")
smtp_handler.setLevel(logging.ERROR)
logger.addHandler(smtp_handler)

file_handler = logging.handlers.RotatingFileHandler('catmonitor.log', maxBytes=100000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#console_handler = logging.StreamHandler()
#console_handler.setLevel(logging.INFO)
#console_handler.setFormatter(formatter)
#logger.addHandler(console_handler)

def get_date_created(article):
    o = no.api('query', prop='revisions', rvlimit=1, rvdir='newer', titles=article)['query']['pages'].itervalues().next()
    if not 'revisions' in o:
        logger.error(u"Could not find first revision for article %s", article)
        return False
    
    ts = o['revisions'][0]['timestamp']
    #page = no.pages[article]
    #rev = page.revisions(limit=1, dir='newer').next()
    ts = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
    #ts = datetime.fromtimestamp(time.mktime(ts))
    return ts

def get_cached(catname):
    cur = sql.cursor()
    articles = []
    cur.execute(u'SELECT article FROM articles WHERE category=?', [catname])
    articles = [r[0] for r in cur.fetchall()]
    cur.close()
    return articles

def get_live(catname, exceptions):
    # The text in the DB is UTF-8, but identified as latin1, so we need to be careful
    db = oursql.connect(host=mysql_host, db=mysql_db, charset=None, use_unicode=False,
            read_default_file=os.path.expanduser('~/.my.cnf'))   
    cur = db.cursor()

    #pbar = ProgressBar(maxval=maxcats, widgets=['Categories: ', Counter()])
    #pbar.start()

    cats = [catname];
    articles = [];
    for catname in cats:
        cur.execute('SELECT page.page_title, categorylinks.cl_type FROM categorylinks,page WHERE categorylinks.cl_to=? AND categorylinks.cl_from=page.page_id AND (page.page_namespace=0 OR page.page_namespace=14)', [catname.encode('utf-8')])
        for row in cur.fetchall():
            if row[1] == 'subcat':
                cat = row[0].decode('utf-8')
                if cat not in exceptions and cat not in cats:
                    cats.append(cat)
                    #print cat
            elif row[1] == 'page':
                pg = row[0].decode('utf-8')
                #if pg not in articles: expensive!
                articles.append(pg)
        if len(cats) > maxcats:
            raise StandardError("Too many categories. We should probably add exclusions")
        #    pbar.maxval = len(cats)
        #pbar.update(len(cats))
    #pbar.maxval = len(cats)
    #pbar.finish()

    articles = list(set(articles))
    logger.info(" -> Found %d cats, %d articles", len(cats), len(articles))
    #logger.info("of which %d unique articles", len(articles))
    cur.close()
    db.close()
    return articles

def update_cache(cached, live):
    now = datetime.now().strftime('%F %T')

    cached_set = set(cached)
    live_set = set(live)

    added = list(live_set.difference(cached_set))
    removed = list(cached_set.difference(live_set))

    logger.info(" -> %d articles in cache, %d articles live", len(cached), len(live))
    logger.info(" -> %d articles added, %d articles removed", len(added), len(removed))
    
    cur = sql.cursor()
    for article in removed:
        cur.execute(u'DELETE FROM articles WHERE category=? AND article=?', [catname, article])
    
    for article in added:
        #created = get_date_created(article)
        #if created != False:
        cur.execute(u'INSERT INTO articles (category, article, date_added) VALUES (?,?,?)', [catname, article, now])

    sql.commit()
    cur.close()

def update(catname, exceptions):

    if type(catname) != unicode:
        raise StandardError("catname must be unicode object")
    
    logger.info("Making list for %s", catname)
    
    cached = get_cached(catname)
    live = get_live(catname, exceptions)
    update_cache(cached, live)

    #ntxt = '\n<div class="prosjekt-header">[[:Kategori:%s|Kategori:%s]] inneholder %d artikler</div>' % (catname, catname, len(live))
    
    #mindate = cur.execute(u'SELECT MIN(date_added) FROM articles WHERE category=?', [catname]).fetchall()[0][0]
    #mindate = datetime.strptime(mindate, '%Y-%m-%d %H:%M:%S')
    #logger.info("Min date is %s", mindate)

    return len(live)

def makelist(catname, txt, maxitems, header, articlecount):
    
    maxitems = int(maxitems)
    if maxitems <= 0:
        raise StandardError("maxitems: invalid value")

    tagstart = u'<!--DB-NyeArtiklerStart-->'
    tagend = u'<!--DB-NyeArtiklerSlutt-->'
    posstart = txt.find(tagstart)
    if posstart == -1:
        raise StandardError("Fant ikke tagstart")
    posstart += len(tagstart)
    posend = txt.find(tagend)
    if posend == -1:
        raise StandardError("Fant ikke tagend")

    ntxt = ''
    if header != '':
        ntxt = '\n' + header % { 'category': catname, 'articlecount': articlecount }
    cur = sql.cursor()
    cur.execute(u'SELECT article, date_created FROM articles WHERE category=? ORDER BY date_created DESC LIMIT %s' % maxitems, [catname])
    cdate = ''
    for r in cur.fetchall():
        #if r[1] != mindate:
        #logger.info("article date is %s", r[1])
        d = datetime.strptime(r[1], '%Y-%m-%d %H:%M:%S')
        d = d.strftime('%d.%m')
        if d != cdate:
            ntxt += '\n<small>%s</small>: ' % d
            cdate = d
        else:
            ntxt += '{{,}} '
        ntxt += '[[%s]] ' % r[0].replace('_', ' ')
    cur.close()

    ntxt += '\n'
    txt = txt[:posstart] + ntxt + txt[posend:]
    return txt

def total_seconds(td):
    # for backwards compability. td is a timedelta object
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6




runstart = datetime.now()
import platform
pv = platform.python_version()
logger.info('running Python %s' % (pv))
template = no.pages[template_name]
for page in template.embeddedin():
    logger.info("Checking: %s", page.page_title)
    #if page.page_title != u'DanmicholoBot/Sandkasse2':
    #    continue
    txt = page.edit()
    te = TemplateEditor(txt)
    template = te.templates[template_name.lower()][0]
    
    if 'kategori' in template.parameters:
        catname = template.parameters['kategori']
    else:
        catname = template.parameters[1]
    
    antall = 10
    if 'antall' in template.parameters:
        antall = template.parameters['antall']
    
    utelat = []
    if 'utelat' in template.parameters:
        utelat = [u.strip().replace(' ','_') for u in template.parameters['utelat'].split(',')]

    overskrift = '<div class="prosjekt-header">[[:Kategori:%(category)s|Kategori:%(category)s]] inneholder %(articlecount)s artikler</div>'
    if 'overskrift' in template.parameters:
        overskrift = template.parameters['overskrift']
    
    cat = no.categories[catname]
    if cat.exists:

        catname = catname.replace(' ', '_')

        articlecount = update(catname, exceptions = utelat)

        cur = sql.cursor()
        cur.execute(u'SELECT article FROM articles WHERE category=? AND date_created IS NULL', [catname])
        articles = [r[0] for r in cur.fetchall()]
        if len(articles) > 0:
            logger.info("Backfillling creation dates for %d articles (this may take a long while)", len(articles))
            for article in articles:
                #logger.info(article)
                try:
                    created = get_date_created(article)
                    if created:
                        cur.execute(u'UPDATE articles set date_created=? WHERE article=?', [created, article])
                        sql.commit()
                except ValueError:
                    logger.error(u"Could not fetch date for %s", article)
        cur.close()
        txt = makelist(catname, txt, maxitems = antall, header=overskrift, articlecount=articlecount)
        page.save(txt, edit_summary)

runend = datetime.now()
runtime = total_seconds(runend - runstart)
logger.info('Complete, runtime was %.f seconds.' % (runtime))
