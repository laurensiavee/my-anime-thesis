from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import pandas as pd 
import pickle
from os.path import relpath
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import os

from keras.models import load_model

from get_anime_details import *
from rec_knowledge_based import *
from rec_content_based import *
from rec_collaborative import *
from rec_hybrid import *

####################
# CONFIG
####################

# DATAFRAME
"""
params of csv file:
anime.csv param: anime_id,title,score,rating_count,ranked,popularity,members,type,studio,synopsis,episode_count,genre,url,img
anime_impl.csv param: anime_id,score,members,type,studio,episode_count,Action,Adult Cast,Adventure,Anthropomorphic,Avant Garde,Award Winning,Boys Love,CGDCT,Childcare,Combat Sports,Comedy,Crossdressing,Delinquents,Detective,Drama,Ecchi,Educational,Erotica,Fantasy,Gag Humor,Girls Love,Gore,Gourmet,Harem,Hentai,High Stakes Game,Historical,Horror,Idols (Female),Idols (Male),Isekai,Iyashikei,Josei,Kids,Love Polygon,Magical Sex Shift,Mahou Shoujo,Martial Arts,Mecha,Medical,Military,Music,Mystery,Mythology,Organized Crime,Otaku Culture,Parody,Performing Arts,Pets,Psychological,Racing,Reincarnation,Reverse Harem,Romance,Romantic Subtext,Samurai,School,Sci-Fi,Seinen,Shoujo,Shounen,Showbiz,Slice of Life,Space,Sports,Strategy Game,Super Power,Supernatural,Survival,Suspense,Team Sports,Time Travel,Vampire,Video Game,Visual Arts,Workplace,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,0.1,1.1,2.1,3.1,4.1,5.1,6.1,7.1,8.1,9.1,10.1,11.1,12.1,13.1,14.1,15.1,16.1,17.1,18.1,19.1,20.1,21.1,22.1,23.1,24.1,25.1,26.1,27.1,28.1,29.1,30.1,31.1,32.1,33.1,34.1,35.1,36.1,37.1,38.1,39.1,40.1,41.1,42.1,43.1,44.1,45.1,46.1,47.1,48.1,49.1,50.1,51.1,52.1,53.1,54.1,55.1,56.1,57.1,58.1,59.1,60.1,61.1,62.1,63.1,64.1,65.1,66.1,67.1,68.1,69.1,70.1,71.1,72.1,73.1,74.1,75.1,76.1,77.1,78.1,79.1,80.1,81.1,82.1,83.1,84.1,85.1,86.1,87.1,88.1,89.1,90.1,91.1,92.1,93.1,94.1,95.1,96.1,97.1,98.1,99.1
"""

# change path here
# path = "C:\my-anime-thesis" 
anime_subset = pd.read_csv(r'C:\my-anime-thesis\static\dataset\anime.csv')
# CBF
indices_id = pickle.load(open(r'C:\my-anime-thesis\static\dataset\indices_id.pickle', 'rb'))
cosine_sim_soup = pickle.load(open(r'C:\my-anime-thesis\static\dataset\cosine_sim_soup.pickle', 'rb'))
# CF
item_sim_df = pickle.load(open(r'C:\my-anime-thesis\static\dataset\item_sim_df.pickle', 'rb'))
user_sim_df = pickle.load(open(r'C:\my-anime-thesis\static\dataset\user_sim_df.pickle', 'rb'))
# HF
anime_impl = pd.read_csv(r'C:\my-anime-thesis\static\dataset\model\anime_impl.csv')
model = load_model(r'C:\my-anime-thesis\static\dataset\model\model_impl.h5')

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.secret_key = "secr"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ratings.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

####################
# CONST
####################
num_slider = 5
num_wide = 8
num_top= 10
list_genre = ['Action', 'Romance']
admin_username = 'admin'
dummy_user_id = 17000
top_anime_id = 5114 #FMAB

"""
--- session list: ---
session["user"]
"""

####################
# DATABASE
####################
db = SQLAlchemy(app)

# engine = db.create_engine("sqlite:///" + os.path.join(basedir, ':memory:'), echo=True)

class users(db.Model):
    __tablename__ = 'User'
    _id = db.Column("id", db.Integer, primary_key = True)
    password = db.Column("password", db.String(50))
    username = db.Column("username", db.String(50))
    rating = db.relationship('ratings', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class ratings(db.Model):
    __tablename__ = 'Rating'
    _id = db.Column("id", db.Integer, primary_key = True)
    user_id = db.Column("user_id", db.ForeignKey('User.id'))
    anime_id = db.Column("anime_id", db.Integer)
    rating = db.Column("rating", db.Integer)
    is_rated = db.Column("is_rated", db.Boolean)
    
    def __init__(self, anime_id, rating, user_id, is_rated):
        self.anime_id = anime_id
        self.rating = rating
        self.user_id = user_id
        self.is_rated = is_rated

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=users, Rating=ratings)

####################
# FILTERING METHOD
####################
def fetch_rating_to_df():
    if "user" in session:
        user = session["user"]
        found_user = users.query.filter_by(username = user).first()
        found_rating = ratings.query.filter_by(user_id = found_user._id, is_rated = True)

        list_user_id = []
        list_score = []
        list_anime_id = []

        for rate in found_rating:
            list_user_id.append(dummy_user_id)
            list_score.append(rate.rating)
            list_anime_id.append(rate.anime_id)

        list_tuples = list(zip(list_user_id, list_score, list_anime_id)) 
        extracted_user_df = pd.DataFrame(list_tuples, columns=['user_id', 'user_score', 'anime_id']) 
    else:
        list_tuples = [] 
        list_anime_id = []
        extracted_user_df = pd.DataFrame(list_tuples, columns=['user_id', 'user_score', 'anime_id']) 
    return extracted_user_df, list_anime_id

def pick_to_collab():
    picked_id = top_anime_id

    if "user" in session:
        user = session["user"]
        found_user = users.query.filter_by(username = user).first()
        found_rating = ratings.query.filter_by(user_id = found_user._id, is_rated = True)

        list_user_id = []
        list_score = []
        list_anime_id = []

        for rate in found_rating:
            list_user_id.append(dummy_user_id)
            list_score.append(rate.rating)
            list_anime_id.append(rate.anime_id)

        list_tuples = list(zip(list_user_id, list_score, list_anime_id)) 
        temp_df = pd.DataFrame(list_tuples, columns=['user_id', 'user_score', 'anime_id']) 

        if(len(temp_df.index) > 0):
            temp_df = temp_df.sort_values(by = ['user_score'], ascending = False)
            
            picked_id = int(temp_df['anime_id'].iloc[0])

    print(picked_id)

    return picked_id

####################
# AUTH
####################
def check_auth():
    is_login = False
    is_admin = False
    if "user" in session:
        is_login = True
        user = session["user"]
        if user == admin_username:
            is_admin = True
    return is_login, is_admin

####################
# PAGING
####################

# HOME
@app.route("/")
@app.route("/#")
def home():
    # SLIDER
    rec = get_top_ranked(anime_subset, num_slider)
    list = []
    list_img = []
    for a in rec:
        list.append(get_anime_title(anime_subset, a))
        list_img.append(get_anime_img_url(anime_subset, a))
    
    # TOP RANKED
    rec1 = get_top_ranked(anime_subset, num_wide)
    list1 = []
    list_img1 = []
    for a in rec1:
        list1.append(get_anime_title(anime_subset, a))
        list_img1.append(get_anime_img_url(anime_subset, a))
    
    # TOP POPULARITY
    rec2 = get_top_popularity(anime_subset, num_wide)
    list2 = []
    list_img2 = []
    for a in rec2:
        list2.append(get_anime_title(anime_subset, a))
        list_img2.append(get_anime_img_url(anime_subset, a))
    
    # FOR YOU 1 (HYBRID)
    extracted_user_df, list_anime_id = fetch_rating_to_df()
    rec3 = []
    num_fy = len(list_anime_id)
    if (num_fy > 0):
        rec3 = get_rec_hybrid(extracted_user_df, list_anime_id, anime_impl, model)
        num_fy = num_wide
    list3 = []
    list_img3 = []

    for a in rec3:
        list3.append(get_anime_title(anime_subset, a))
        list_img3.append(get_anime_img_url(anime_subset, a))

    # FOR YOU 2 (CF)
    collab_id = pick_to_collab()
    rec4 = get_rec_collaborative_anime(collab_id, item_sim_df)
    list4 = []
    list_img4 = []

    for a in rec4:
        list4.append(get_anime_title(anime_subset, a))
        list_img4.append(get_anime_img_url(anime_subset, a))

    # GENRE 1 
    rec5 = get_top_ranked(anime_subset, num_wide)
    list5 = []
    list_img5 = []

    for a in rec5:
        list5.append(get_anime_title(anime_subset, a))
        list_img5.append(get_anime_img_url(anime_subset, a))

    # GENRE 2
    rec6 = get_top_genre(anime_subset, num_wide, list_genre[1])
    list6 = []
    list_img6 = []
    
    for a in rec6:
        list6.append(get_anime_title(anime_subset, a))
        list_img6.append(get_anime_img_url(anime_subset, a))
        

    is_login, is_admin = check_auth()

    return render_template("blog/index.html", 
                           num=num_wide, num_carousel = num_slider, 
                           list=list, cnt=rec, list_img=list_img, 
                           list_genre=list_genre, 
                           list1=list1, cnt1=rec1, list_img1=list_img1,
                           list2=list2, cnt2=rec2, list_img2=list_img2,
                           list3=list3, cnt3=rec3, list_img3=list_img3,
                           list4=list4, cnt4=rec4, list_img4=list_img4,
                           list5=list5, cnt5=rec5, list_img5=list_img5,
                           list6=list6, cnt6=rec6, list_img6=list_img6,
                           is_login = is_login, is_admin = is_admin,
                           num_fy = num_fy
                           )

# PROFILE
@app.route('/profile', methods=["POST", "GET"])
def profile():
    if "user" in session:
        user = session["user"]
        
        list_anime_rate = []
        props_usr = []
        found_user = users.query.filter_by(username = user).first()
        num_usr = 0

        found_rating = ratings.query.filter_by(user_id = found_user._id, is_rated = True)

        anime_count = found_rating.count()

        for rate in found_rating:
            if(num_usr < num_top):
                list_anime_rate.append([rate.anime_id, rate.rating])
                props_usr.append(get_card_s_prop(anime_subset, rate.anime_id))
                num_usr = num_usr + 1
            else: 
                break

        # anime_id = 1
        # rec = get_rec_content_based(anime_id, anime_subset, indices_id, cosine_sim_soup)

        # FOR YOU 1 (HYBRID)
        extracted_user_df, list_anime_id = fetch_rating_to_df()
        rec3 = []
        if (len(list_anime_id) > 0):
            rec3 = get_rec_hybrid(extracted_user_df, list_anime_id, anime_impl, model)
        list3 = []
        list_img3 = []

        for a in rec3:
            list3.append(get_anime_title(anime_subset, a))
            list_img3.append(get_anime_img_url(anime_subset, a))

        # FOR YOU 2 (CF)
        collab_id = pick_to_collab()
        rec4 = get_rec_collaborative_anime(collab_id, item_sim_df)
        list4 = []
        list_img4 = []

        for a in rec4:
            list4.append(get_anime_title(anime_subset, a))
            list_img4.append(get_anime_img_url(anime_subset, a))

        props = []
        rec = []
        for a in rec3:
            props.append(get_card_s_prop(anime_subset, a))
            rec.append(a)
        for a in rec4:
            props.append(get_card_s_prop(anime_subset, a))
            rec.append(a)

        is_login, is_admin = check_auth()

        return render_template("blog/profile.html", username=user, 
                               props=props, num=len(rec), 
                               recs=rec, props_usr=props_usr, 
                               num_usr=num_usr, 
                               list_anime_rate=list_anime_rate, anime_count=anime_count,
                               is_login = is_login, is_admin = is_admin)
    else:
        return redirect(url_for("login"))
    
# ANIME DETAILS
@app.route('/anime/<anime_id>', methods=["POST", "GET"])
def anime_detail(anime_id):
    if request.method == "POST":
        if "user" in session:
            user = session["user"]

            rate = request.form["rating"]
            if rate.isdigit():
                if int(rate) > 0 and int(rate) <=10:

                    found_user = users.query.filter_by(username = user).first()
                
                    found_rating = ratings.query.filter_by(user_id = found_user._id, anime_id = anime_id, is_rated = True).first()

                    if(found_rating):
                        found_rating.rating = rate
                        db.session.commit()
                    else:
                        rating = ratings(anime_id=anime_id, rating=rate, user_id=found_user._id, is_rated=True)

                        db.session.add(rating)
                        db.session.commit()
        else:
            is_login, is_admin = check_auth()
            return render_template("blog/login.html", 
                                   is_login = is_login, is_admin = is_admin)
   
    if "user" in session:
        user = session["user"]
        found_user = users.query.filter_by(username = user).first()
        found_rating = ratings.query.filter_by(user_id = found_user._id, anime_id = anime_id, is_rated = True).first()

        if(found_rating):
            user_rate = found_rating.rating
        else:
            user_rate = "-"


    anime_title = get_anime_title(anime_subset, anime_id)
    rec = get_rec_content_based(anime_id, anime_subset, indices_id, cosine_sim_soup)
    # rec = get_rec_collaborative_anime_id(anime_id, item_sim_df)

    list = []
    for a in rec:
        list.append(get_anime_title(anime_subset, a))

    props = []
    for a in rec:
        props.append(get_card_s_prop(anime_subset, a))

    details = get_complete_anime_details(anime_subset, anime_id)

    is_login, is_admin = check_auth()

    return render_template("blog/anime_details.html", anime_id=anime_id, anime_title=anime_title, 
                           recs=rec, details=details, props=props, num=num_top, user_rate=user_rate,
                           is_login = is_login, is_admin = is_admin)


# LOGIN
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        found_user = users.query.filter_by(username = user).first()
        if found_user:
            pwd_true = found_user.password
            if pwd == pwd_true:
                session["user"] = user
            else:
                is_login, is_admin = check_auth()
                return render_template("blog/login.html", err_msg="incorrect password", 
                           is_login = is_login, is_admin = is_admin)
                                       
        else:
            is_login, is_admin = check_auth()
            return render_template("blog/login.html", err_msg="user not found",
                           is_login = is_login, is_admin = is_admin)

        return redirect(url_for("profile"))
    else:
        is_login, is_admin = check_auth()

        if "user" in session:
            return redirect(url_for("profile"))
        
        return render_template("blog/login.html", err_msg="",
                           is_login = is_login, is_admin = is_admin)
                               
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# REGISTER
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        found_user = users.query.filter_by(username = user).first()
        if found_user:
            is_login, is_admin = check_auth()
            return render_template("blog/register.html", err_msg="Username already exist!",
                           is_login = is_login, is_admin = is_admin)
        elif pwd == "":
            is_login, is_admin = check_auth()
            return render_template("blog/register.html", err_msg="Password cannot be empty!",
                           is_login = is_login, is_admin = is_admin)
        else:
            usr = users(user, pwd)
            db.session.add(usr)
            db.session.commit()

            session["user"] = user
        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("profile"))
        is_login, is_admin = check_auth()
        return render_template("blog/register.html", err_msg="",
                           is_login = is_login, is_admin = is_admin)

# SEARCH
@app.route('/search', methods=["POST", "GET"])
def search():
    if request.method == "POST":
        title = request.form["search_title"]

        contain_values = anime_subset[anime_subset['title'].str.contains("(?i)" + title, na=False)]

        result_count = len(contain_values)
        if result_count > num_top:
            result_count = num_top

        list_id = []
        for i, row in contain_values.iterrows():
            list_id.append(row['anime_id'])

        titles = []
        for a in list_id:
            titles.append(get_anime_title(anime_subset, a))
        
        props = []
        for a in list_id:
            props.append(get_card_s_prop(anime_subset, a))
        
        is_login, is_admin = check_auth()
        return render_template("blog/search_result.html", cnt=list_id, num=result_count, 
                               titles=titles, key=title, props=props,
                               is_login = is_login, is_admin = is_admin)

    else:
        is_login, is_admin = check_auth()
        return render_template("blog/search.html", is_login = is_login, is_admin = is_admin)
                               
# EDIT PROFILE
@app.route('/edit_profile', methods=["POST", "GET"])
def edit_profile():
    if "user" in session:
        if request.method == "POST":
            user = request.form["username"]
            pwd = request.form["password"]
            # bio = request.form["bio"]

            old_user = session["user"]
            found_user = users.query.filter_by(username = old_user).first()

            new_user = users.query.filter_by(username = user).first()

            if new_user:
                if found_user.username != new_user.username:
                    is_login, is_admin = check_auth()
                    return render_template("blog/edit_profile.html", err_msg="Username already exist!", username=user, password=pwd, is_login = is_login, is_admin = is_admin)

            if pwd == "":
                is_login, is_admin = check_auth()
                return render_template("blog/edit_profile.html", err_msg="Password cannot be empty!", username=user, password=pwd, is_login = is_login, is_admin = is_admin)
            
            else:
                found_user.username = user
                found_user.password = pwd
                # found_user.bio = bio
                
                db.session.commit()
                session["user"] = found_user.username

            is_login, is_admin = check_auth()
            return render_template("blog/edit_profile.html", err_msg="ok", username=user, password=pwd, is_login = is_login, is_admin = is_admin)

        else:
            user = session["user"]
            found_user = users.query.filter_by(username = user).first()

            username = found_user.username
            password = found_user.password

            is_login, is_admin = check_auth()
            return render_template("blog/edit_profile.html", err_msg="", username=username, password=password, is_login = is_login, is_admin = is_admin)

    else:
        return redirect(url_for("login"))


####################
# DEBUG PAGE (BY ADMIN)
####################
def create_admin():
    found_user = users.query.filter_by(username = "admin").first()
    if not found_user:
        usr = users("admin", "password")
        db.session.add(usr)
        db.session.commit()

@app.route('/debug_user')
def view_user_db():
    is_login, is_admin = check_auth()
    return render_template("blog/debug/view_user_db.html", values=users.query.all(), is_login = is_login, is_admin = is_admin)

@app.route('/debug_rating')
def view_rating_db():
    is_login, is_admin = check_auth()
    return render_template("blog/debug/view_rating_db.html", values=ratings.query.all(), is_login = is_login, is_admin = is_admin)

@app.route("/delete_db")
def del_all():
    db.drop_all()
    db.create_all()
    create_admin()
    is_login, is_admin = check_auth()
    return render_template("blog/debug/view_rating_db.html", values=ratings.query.all(), is_login = is_login, is_admin = is_admin)

####################
# LOAD
####################
if __name__ == "__main__":
    with app.app_context():
        # engine = create_engine('sqlite:///:memory:', echo=True)
        # Base.metadata.create_all(engine)
        # Session = sessionmaker(bind=engine)
        # session = Session()
        
        db.create_all()
        create_admin()

    app.run(debug=False)


