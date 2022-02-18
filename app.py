from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from pyshorteners import Shortener

import requests
import json

def create_payload(url):
    return json.dumps({
        "url": url,
        "domain": "tiny.one",
        "alias": "",
        "tags": ""
    })

url_shortener = Shortener()

def shorten_url(url):
    url = "https://api.tinyurl.com/create?api_token=hSljEjSSLC58Lqzqs3uzLC5uPdKKPW1XtZz2xEMcB0C1TPmGTGUP8T6ftWv3"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = create_payload(url)
    print(payload)
    response = requests.request("POST", url, headers=headers, data=create_payload(url))
    return response.text

from datetime import datetime
import sys


app = Flask(__name__)
api_token = "hSljEjSSLC58Lqzqs3uzLC5uPdKKPW1XtZz2xEMcB0C1TPmGTGUP8T6ftWv3"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    #link = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods= ['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_title = request.form['title']
        task_content = request.form['content']
        # print(task_content)
        new_task = Todo(content=task_content, title=task_title)
        try:
            db.session.add(new_task)
            db.session.commit()
            print(new_task.id)
            local_url = "https://paste-bin-nage.herokuapp.com/fetchdata/"+str(new_task.id)
            # print(local_url)
            tiny_url = url_shortener.tinyurl.short(local_url)
            return render_template('index.html', tiny_url=tiny_url)
        except:
            return sys.exc_info()[0]
        
    else:
        return render_template('index.html')

@app.route('/PreviousData.html', methods= ['GET', 'POST'])
def PreviousData():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('PreviousData.html', tasks=tasks)

@app.route('/fetchdata/<int:id>')
def fetchdata(id):
    task_to_content = Todo.query.get(id)
    #print(task_to_content)
    try:
        return str(task_to_content.content)
    except:
        return 'There was a problem fetching that task'
       
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/PreviousData.html')
    except:
        return 'There was a problem deleting that task'

if __name__ == "__main__":
    app.run(debug=True)