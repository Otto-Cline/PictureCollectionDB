from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
import ast
import os
from collections import defaultdict

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    main_heading = db.Column(db.String)
    see_alsos = db.Column(db.String)
    year = db.Column(db.String)

    @property
    def see_alsos_list(self):
        try:
            return ast.literal_eval(self.see_alsos)
        except:
            return []

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form.get('query', '').strip().lower()
        if not query:
            return render_template('search.html', results=[])

        all_rows = Subject.query.all()
        grouped = defaultdict(lambda: {"subheadings": set(), "see_alsos": set()})

        for row in all_rows:
            try:
                see_alsos = ast.literal_eval(row.see_alsos)
            except:
                see_alsos = []

            heading_match = query == row.main_heading.lower()
            see_also_match = any(query == term.lower() for term in see_alsos)

            if heading_match or see_also_match:
                g = grouped[row.main_heading]
                g["see_alsos"].update(see_alsos)

        # Now go through all rows again to collect subheadings for matched headings
        for row in all_rows:
            try:
                see_alsos = ast.literal_eval(row.see_alsos)
            except:
                continue

            for main_heading in grouped.keys():
                for term in see_alsos:
                    if term.startswith(f"{main_heading} -- "):
                        grouped[main_heading]["subheadings"].add(term)

        results = [
            {
                "main_heading": heading,
                "subheadings": sorted(list(data["subheadings"])),
                "see_alsos": sorted(list(data["see_alsos"]))
            }
            for heading, data in grouped.items()
        ]

    return render_template('search.html', results=results)