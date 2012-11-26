#!/usr/bin/env python
# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- vim:fenc=utf-8:ft=python:et:sw=4:ts=4:sts=4

import mwclient
import os, oursql, sqlite3, re
from progressbar import ProgressBar, Percentage, Bar, ETA, SimpleProgress, Counter
from datetime import datetime
from danmicholoparser import TemplateEditor
from wp_private import botlogin

template_name = u'Bruker:DanmicholoBot/Kategoriovervåkning'
edit_summary = 'Oppdaterer liste over nye artikler'
host = 'no.wikipedia.org'
mysql_host = 'nowiki-p.rrdb.toolserver.org'
mysql_db = 'nowiki_p'

sql = sqlite3.connect('catmonitor.db')
no = mwclient.Site(host)
no.login(*botlogin)

def get_cached(catname):
    cur = sql.cursor()
    articles = []
    cur.execute(u'SELECT article FROM articles WHERE category=?', [catname])
    articles = [r[0] for r in cur.fetchall()]
    cur.close()
    return articles

def get_live(catname):
    # The text in the DB is UTF-8, but identified as latin1, so we need to be careful
    db = oursql.connect(host=mysql_host, db=mysql_db, charset=None, use_unicode=False,
            read_default_file=os.path.expanduser('~/.my.cnf'))   
    cur = db.cursor()

    maxcats = 10000
    pbar = ProgressBar(maxval=maxcats, widgets=['Categories: ', Counter()])
    pbar.start()

    cats = [catname];
    articles = [];
    for catname in cats:
        cur.execute('SELECT page.page_title, categorylinks.cl_type FROM categorylinks,page WHERE categorylinks.cl_to=? AND categorylinks.cl_from=page.page_id', [catname.encode('utf-8')])
        for row in cur.fetchall():
            if row[1] == 'subcat':
                cat = row[0].decode('utf-8')
                if cat not in cats:
                    cats.append(cat)
            elif row[1] == 'page':
                pg = row[0].decode('utf-8')
                #if pg not in articles: expensive!
                articles.append(pg)
        pbar.update(len(cats))
    pbar.maxval = len(cats)
    pbar.finish()

    print "Found %d cats, %d articles" % (len(cats), len(articles))
    articles = list(set(articles))
    print "of which %d unique articles" % (len(articles))
    cur.close()
    db.close()
    return articles

def update_cache(cached, live):
    now = datetime.now().strftime('%F %T')

    cached_set = set(cached)
    live_set = set(live)

    added = list(live_set.difference(cached_set))
    removed = list(cached_set.difference(live_set))

    print "%d articles added, %d articles removed" % (len(added), len(removed))
    
    cur = sql.cursor()
    for article in removed:
        cur.execute(u'DELETE FROM articles WHERE category=? AND article=? LIMIT 1', [catname, article])
    
    for article in added:
        cur.execute(u'INSERT INTO articles (category, article, date_added) VALUES (?,?,?)', [catname, article, now])

    sql.commit()
    cur.close()

def makelist(catname, txt, maxitems):
    if type(catname) != unicode:
        raise StandardError("catname must be unicode object")

    maxitems = int(maxitems)
    if maxitems <= 0:
        raise StandardError("maxitems: invalid value")
    
    cached = get_cached(catname)
    live = get_live(catname)
    update_cache(cached, live)

    end = u'</noinclude>'
    m = txt.find(end)
    if m == -1:
        raise StandardError("Fant ikke includeonly")
    m += len(end)
    txt = txt[:m]

    txt += '\n<div class="prosjekt-header">[[:Kategori:%s|Kategori:%s]] inneholder %d artikler</div>' % (catname, catname, len(live))
    
    cur = sql.cursor()
    cur.execute(u'SELECT article, date_added FROM articles WHERE category=? ORDER BY date_added DESC LIMIT %s' % maxitems, [catname])
    cdate = ''
    for r in cur.fetchall():
        d = datetime.strptime(r[1], '%Y-%m-%d %H:%M:%S').strftime('%d.%m')
        if d != cdate:
            txt += '\n<small>%s</small>: ' % d
            cdate = d
        else:
            txt += '{{,}} '
        txt += '[[%s]] ' % r[0].replace('_', ' ')
    txt += u'<div><small>Listen reflekterer artikler nylig kategorisert, ikke nødvendig nyopprettede artikler. Inntil et visst antall nye artikler er registrert, vil listen vise et «tilfeldig» sett artikler registrert den første dagen boten kjørte.</small></div>'
    return txt


template = no.pages[template_name]
for page in template.embeddedin():
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
    
    cat = no.categories[catname]
    if cat.exists:
        txt = makelist(catname, txt, maxitems = antall)
        page.save(txt, edit_summary)


