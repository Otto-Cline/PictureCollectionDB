from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    main_heading = db.Column(db.String)
    see_alsos = db.Column(db.String)
    year = db.Column(db.String)

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form.get('query', '')
        results = Subject.query.filter(Subject.main_heading.ilike(f"%{query}%")).all()
    return render_template('search.html', results=results)