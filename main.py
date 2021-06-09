import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect
import json

with open('config.json', 'r') as c:
    params = json.load(c)['params']

app = Flask(__name__)
app.secret_key = 'test'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(params['prod_uri'], params['local_uri'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(80), nullable=False)
    msg = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    by = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(80), nullable=False)
    img_file = db.Column(db.String(80), nullable=False)


# # Remove when uploading to servers
@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def home():
    post_all = Posts.query.all()

    return render_template('index.html', postall=post_all)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contacts', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # '''Add entry in db'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contacts(
            name=name,
            phone_num=phone,
            msg=msg,
            date=datetime.date.today(),
            email=email
        )

        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    single_post = Posts.query.filter_by(slug=post_slug).first()

    return render_template('post.html', post=single_post)


@app.route('/dashboard', methods=['GET', 'POST'])
def Dashboard():
    if 'user' in session and session['user'] == 'ayush@gmail.com':
        posts = Posts.query.all()

        return render_template('dashboard.html', posts=posts)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email.lower().strip() == 'ayush@gmail.com':
            if password.strip() == 'admin':
                session['user'] = email

                posts = Posts.query.all()

                return render_template('dashboard.html', posts=posts)

        return render_template('login.html')

    return render_template('login.html')


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == 'ayush@gmail.com':
        if request.method == 'POST':
            box_title = request.form.get('title')
            by = request.form.get('by')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')

            if sno == '0':

                post = Posts(
                    title=box_title,
                    by=by,
                    slug=slug,
                    content=content,
                    date=datetime.date.today(),
                    img_file=img_file
                )
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.by = by
                post.slug = slug
                post.content = content
                post.img_file = img_file

                db.session.add(post)
                db.session.commit()

                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', post=post)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
