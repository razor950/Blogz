from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


#if user hits page that requires login, redirect user to that login page
@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login') 

def length(x):
    if len(x) >= 3 and len(x) <= 20:
        return True

def no_space(x):
    if x.count(" ") == 0:
        return True

def confirmation(x, y):
    if x == y:
        return True

#index route
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST','GET'])
def login():
    username_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html', password_error=password_error, username=username)
        elif not user: 
            username_error = "The user doesn't exist. Please create a new account."
            return render_template('login.html', username_error=username_error)

    return render_template('login.html')      

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypass = request.form['verify']

rrra        user = User.query.filter_by(username=username).first()

        if length(username) and no_space(username) and not user:
            username_error = ""
        elif user:
            username_error: "Username already exists. Choose a different name."
        else:
            username_error = "Username is not valid."

        if length(password) and no_space(password) and confirmation(password, verifypass):
            password_error = ""
        elif not confirmation(password, verifypass):
            password_error = "Passwords do not match"
        else:
            password_error = "Password is not valid."

        
        if username_error == "" and password_error == "":
            add_user = User(username, password)
            db.session.add(add_user)
            db.session.commit()
            session['username']=username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, username=username)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    posts = Blog.query.all()

    if blog_id:
        posts = Blog.query.filter_by(id=blog_id).first()
        return render_template('entry.html', title=posts.title, body=posts.body, user=posts.owner.username, user_id=posts.owner_id)
    if user_id:
        post = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', post=post)
    
    return render_template('blog.html', posts=posts)

# New post route. Redirects to post page.
@app.route('/newpost')
def post():
    return render_template('newpost.html', title="New Post")

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        owner = User.query.filter_by(username=session['session']).first()
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "You forgot to enter a blog title."
        if not blog_body:
            body_error = "You forgot to enter a blog entry."

        if not body_error and not title_error:
            new_blog_entry = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog_entry)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog_entry.id))
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()
