from flask import render_template, request
from app import app
from app.forms import InputLeadersForm
from leader import Leader

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = InputLeadersForm(request.form)
    if request.method == 'POST':
            leaders = request.form['leaders']
            print(leaders)
           # scraper = Scraper(leaders)
    return render_template('index.html', form=form)

@app.route('/results', methods=['GET', 'POST'])
def results():
    form = InputLeadersForm(request.form)
    if request.method == 'POST':
            userInput = request.form['leaders']
            # split input by semicolon
            names = userInput.split(";")
            leaders = []
            for name in names:
                if name:
                    name = name.lower().strip()
                    leaders.append(Leader(name))
    return render_template('results.html', form=form)
