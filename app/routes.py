from flask import render_template, request, redirect, url_for
from app import app
from app.forms import InputLeadersForm
from leader import Leader
from BookSystem import BookSystem
from scraper import Scraper
from book import Book

@app.route('/',methods = ['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    form = InputLeadersForm()
    if request.method == 'POST':
        return redirect(url_for('results', leaders = form.leaders.data))
    return render_template('index.html', form = form)

@app.route('/results/<leaders>', methods=['GET', 'POST'])
def results(leaders):
    form = InputLeadersForm()
    if request.method == 'POST':
        return redirect(url_for('index'))
    else:
        if leaders:
            names = leaders.split(";")
            leaders = []
            for name in names:
                if name: 
                    name = name.lower().strip()
                    leaders.append(name)
            bookUrlsWithFreq = Scraper.bookUrlsWithFreq(leaders)
            bookurls = list(bookUrlsWithFreq.keys())[:5]
            books = [Scraper.bookFromUrl(bookurl) for bookurl in bookurls if bookurl]
            return render_template('results.html', form = form, books = books)
    return render_template('results.html', form=form, leaders=None)
