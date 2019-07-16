import sys
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from time import time
from flask import render_template, flash, redirect, g, url_for, session, request, jsonify
from flask_login import login_user, current_user, login_required, logout_user

from app import app, lm, oid, db
from app.forms import LoginForm, EditForm, PostForm,SouForm
from app.models import User, Post
from config import POSTS_PER_PAGE, ALLOWED_EXTENSIONS, UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SouForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('index.html',
                           title='Home',
                           form=form,
                           now=int(time())
                           )

@app.route('/login',methods=['GET','POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        #flash('Login requested for OpenID="' + form.openid.data + '",remember_me='+ str(form.remember_me.data))
        #return redirect('/index')
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
        title = "Sign In",
        form = form,
        providers=app.config['OPENID_PROVIDERS']
        )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
@app.route('/user/<nickname>', methods=['GET', 'POST'])
@app.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User '+nickname + ' not found')
        return redirect(url_for('index'))
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = user.nickname+'.'+file.filename.rsplit('.', 1)[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('user',nickname=nickname, filename=filename))
    oldfile = UPLOAD_FOLDER + user.nickname + '.xlsx'
    import pandas as pd
    xlsx = pd.ExcelFile(oldfile)
    df = pd.read_excel(xlsx, 'Sheet1')
    return render_template('user.html',
                           user=user,
                           now=int(time()),
                           tables=[df.to_html(classes='data')],
                           titles=df.columns.values
                           )

@app.route('/edit', methods=['GET','POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('已经更新了哦')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname,email=resp.email)
        db.session.add(user)
        db.session.commit()
        #make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/sousou', methods=['GET', 'POST'])
@login_required
def sousou():
    form = SouForm()
    soudata = []
    if form.validate_on_submit():

        word = form.sou.data
        from .spider.SouSpider import HandleSou
        spider = HandleSou()
        soudata = spider.return_result(g.user.nickname, word)

    return render_template('index.html',
                           title='Home',
                           form=form,
                           souo=soudata,
                           now=int(time())
                           )

@app.route('/souall', methods=['GET','POST'])
@login_required
def souall():
    recv_data = request.args.get('w')
    from .spider.SouSpider import HandleSou
    spider = HandleSou()
    soudata = spider.return_result(g.user.nickname,None)

    return jsonify(soudata)

