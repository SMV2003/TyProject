from flask import Flask, redirect, url_for, render_template, request,session
from Foods.search_food import search_food,find_nutr_for_search,cross_mul,check_if_in_session
import requests
import pdb
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.secret_key = "mysecretkey"
ekey = open("C:\\Users\\kaushal\\Desktop\\ExerciseApi.txt" , mode='r').read()


# Database Stuff

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:@localhost:5433/kaushal01'

db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    nutritions = db.relationship('Nutrition', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        


class Nutrition(db.Model):
    __tablename__ = 'nutritions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calorie_goal = db.Column(db.Float)
    calories_eaten = db.Column(db.Float)
    protein = db.Column(db.Float)
    fats = db.Column(db.Float)
    carbs = db.Column(db.Float)
    calories_burned = db.Column(db.Float)
    datentime=db.Column(db.String,nullable=False)

    def __init__(self, user_id, calories_eaten, protein, fats, carbs, calories_burned,datentime,calorie_goal):
        self.user_id = user_id
        self.calories_eaten = calories_eaten
        self.protein = protein
        self.fats = fats
        self.carbs = carbs
        self.calories_burned = calories_burned
        self.datentime = datentime
        self.calorie_goal = calorie_goal

with app.app_context():
	db.create_all()


@app.route('/', methods =["GET", "POST"])
def gfg():
	check_if_in_session(session,"caloriereq",0,'h')
	if request.method == "POST":
		cal_intake = int(request.form.get("calorie_intake"))
		session["caloriereq"] = cal_intake
	check_if_in_session(session,"cal_burned",0,'h')
	check_if_in_session(session,"calories",0,'h')
	check_if_in_session(session,"protein",0,'h')
	check_if_in_session(session,"fats",0,'h')
	check_if_in_session(session,"carbs",0,'h')
	
	if "username" not in session:
		return render_template('about.html')
	return render_template("HomePage.html",Calorie_intake=session["caloriereq"],Calories=int(session["calories"]),Protein=session["protein"],Fats=session["fats"],Carbs=session["carbs"],Burnt=session["cal_burned"],username=session["username"])



@app.route('/food.html',methods =["GET", "POST"])
def food():
	if "username" not in session:
		return render_template('about.html')
	if request.method == "POST":
		foodname = request.form.get("fname")
		size = int(request.form.get("serving_size"))
		

		foods_list=search_food(foodname)
		if foods_list == 0:
			return render_template("food.html",flag=0)
		foods_list[0] = map(lambda x: cross_mul(x,size),foods_list[0])
		foods_list[1] = map(lambda x: cross_mul(x,size),foods_list[1])
		foods_list[2] = map(lambda x: cross_mul(x,size),foods_list[2])
		foods_list[3] = map(lambda x: cross_mul(x,size),foods_list[3])
		
		foods_list[0] = list(foods_list[0])
		foods_list[1] = list(foods_list[1])
		foods_list[2] = list(foods_list[2])
		foods_list[3] = list(foods_list[3])
		return render_template("SearchResults.html",food_s=size,name=foods_list[4],calories=foods_list[0],protein=foods_list[1],fats=foods_list[2],carbs=foods_list[3],num=len(foods_list[1]))
	return render_template("food.html",flag=1)



@app.route('/home.html')
def home():
    datentime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session['datentime']=datentime
    return redirect(url_for("gfg"))


@app.route('/exercise.html',methods =["GET", "POST"])
def exercise():
	if "username" not in session:
		return render_template('about.html')
	if request.method == 'POST':
		activity = request.form.get('activity')
		weight = request.form.get('weight')
		duration = request.form.get('duration')
		try:
			weight = int(weight)
			weight *= 2.20462
			duration = int(duration)
		except ValueError:
			return "Weight and duration must be integers."
		calories_burned_data = get_calories_burned(activity, weight, duration)
		if calories_burned_data:
			return render_template('exercise.html', result=calories_burned_data,flag=1)
		else:
			return render_template('exercise.html',result=False,flag=0)
	return render_template('exercise.html',result=False,flag=1)

def get_calories_burned(activity, weight=160, duration=60, api_key=ekey):
    """
    Get calories burned for a specific activity.

    :param activity: Name of the activity (partial name is accepted).
    :param weight: Weight of the user in pounds (default is 160).
    :param duration: Duration of the activity in minutes (default is 60).
    :param api_key: Your API key (required).
    :return: Dictionary containing details of calories burned for the specified activity.
    """
    url = 'https://api.api-ninjas.com/v1/caloriesburned'
    headers = {'X-Api-Key': api_key}
    params = {'activity': activity, 'weight': weight, 'duration': duration}
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == requests.codes.ok:
        data = response.json()
        if data:
            return data  # Return only the first record
        else:
            return None
    else:
        return None

@app.route('/about.html',methods =["GET", "POST"])
def about():
	#if request.method == "POST":
	#	meal1 = request.form.get("diary_meal_1")
	return render_template("about.html")



@app.route('/add_food',methods=["GET", "POST"])
def add_food():
	if request.method == "POST":
		protein = carbs = fat = calories = 0.0
		food_name = str(request.form.get("food_name"))
		calories = float(request.form.get("food_cal"))
		protein = float(request.form.get("food_protein"))
		fats = float(request.form.get("food_fats"))
		carbs = float(request.form.get("food_carbs"))
		
		check_if_in_session(session,"calories",calories,'O')
		check_if_in_session(session,"protein",protein,'O')
		check_if_in_session(session,"fats",fats,'O')
		check_if_in_session(session,"carbs",carbs,'O')
	return redirect(url_for("food"))


@app.route('/add_exercise', methods=["GET", "POST"])
def add_exercise():
	if request.method == "POST":
		cal_burned = float(request.form.get("cals_burned"))
        # session['cal_burned']+=cal_burned
		check_if_in_session(session,"cal_burned",cal_burned,'O')
        # Redirect to the exercise page
		return redirect(url_for("exercise"))
	return render_template('add_exercise.html')	


@app.route('/log_in.html' , methods=["POST","GET"])
def log_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        nutridata=Nutrition.query.filter_by(user_id=user.id).order_by(Nutrition.datentime.desc()).first()
        if user:
            if user.password == password:
                # Store the username in the session
                session['username'] = username
                session['user_id']=user.id
                if nutridata is not None:
                    session['cal_burned']=nutridata.calories_burned
                    session['calories']=nutridata.calories_eaten
                    session['protein']=nutridata.protein
                    session['fats']=nutridata.fats
                    session['carbs']=nutridata.carbs
                    session['caloriereq']=nutridata.calorie_goal
                    datentime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    session['datentime']=datentime
                    return redirect('/home.html')  # Redirect to profile page after successful login
                else:
                     return redirect('/home.html')
            else:
                return render_template('login.html',flag=1) # Password does not match
        else:
            return render_template('login.html',flag=2)  # User with the provided username does not exist

    return render_template('login.html',flag=0)

@app.route('/logout')
def log_out():
	nutrition_entry = Nutrition(
            user_id=session['user_id'],
            calories_burned=session['cal_burned'],
            calories_eaten=session['calories'],
            protein=session['protein'],
            fats=session['fats'],
            carbs=session['carbs'],
			datentime=str(session['datentime']),
			calorie_goal=session['caloriereq']
        )
	db.session.add(nutrition_entry)
	db.session.commit()
	session.clear()
	# flash("You have been Logged Out!!!")
	return render_template('about.html')

@app.route('/profile.html')
def profile():
	return render_template('profile.html')

@app.route('/signup.html',methods=["POST","GET"])
def sign_up():
	
	if request.method == "POST":
		user_name=request.form['username']
		password=request.form['password']
		new_user =User(username=user_name,password=password)
		
		try:
			db.session.add(new_user)
			db.session.commit()
			return redirect("/log_in.html")
		except:
			return "There was an error signing up"
	else:
		return render_template("signup.html")
	

if __name__ == "__main__":
	app.run(debug = True)
	