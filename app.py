import re
from logging.config import dictConfig
from flask import Flask
from flask import render_template # Flask templates

import content # All Contentstack content


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

@app.context_processor
def injectHeaderFooter():
    '''
    Used in base.html - Variables available all through the application
    '''
    app.logger.debug('in injectHeaderFooter()')
    header = content.getEntries('header')[0]
    title = header['title']
    menu = None
    if header['menu'] is not None:
        menu = content.constructHeaderMenu(header['menu'])
    return dict(label=title, menu=menu)

def return404(url=''):
    '''
    Returning 404
    '''
    app.logger.info('Returning 404 for ' + str(url))
    return render_template('404.html', title='404'), 404


@app.route('/<string:blogPath>/<string:year>/<string:month>/<string:day>/<string:slug>')
def blogEntry(blogPath, year, month, day, slug):
    '''
    Only to construct the blog entry for links in blog.html...  Not much else.
    '''
    return None

# Landing pages and blog entries
@app.route('/', defaults={'url': ''})
@app.route('/<path:url>')
def pages(url):
    app.logger.debug('in pages(): ' + str(url))
    if re.match("([blog\./]*/[0-9\./]*[\s]?)", url): # Matches specific blog path
        post = content.search('blog', 'url', '/' + url)
        if post: # Returns the blog entry if it is found
            return render_template('blogentry.html', title=post['title'], entry=post)
    elif url == 'blog': # Blog landing page is different since it lists up all the blogs
        blogEntries = content.getEntries('blog')
        if blogEntries: # Returns all blogs if they exist
            return render_template('blog.html', title='Blog', blogs=blogEntries, len=len(blogEntries))
    else: # All regular landing pages
        entry = content.getLandingPage(url)
        if entry: # Returns landing page if the path for it exists
            references = content.findLPReferences(entry) # landing_page has possible references
            return render_template('index.html', title=entry['title'], entry=entry, ref=references)
    return return404(url)

@app.errorhandler(404)
def page_not_found(error):
    '''
    ...
    '''
    app.logger.debug('Returning 404', error)
    return return404()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
