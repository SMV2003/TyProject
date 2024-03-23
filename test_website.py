from flask import Flask, redirect, url_for, render_template, request,session
from Foods.search_food import search_food,find_nutr_for_search,cross_mul,check_if_in_session,find_nutr_multiple_v2
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app = Flask(__name__)
app.secret_key = "mysecretkey"
#session["calories"] = 0

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:@localhost:5433/kaushal'

db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    calorie_goal = db.Column(db.Float)
    nutritions = db.relationship('Nutrition', backref='user', lazy=True)

    def __init__(self, username, password, calorie_goal):
        self.username = username
        self.password = password
        self.calorie_goal = calorie_goal


class Nutrition(db.Model):
    __tablename__ = 'nutritions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calories_eaten = db.Column(db.Float)
    protein = db.Column(db.Float)
    fats = db.Column(db.Float)
    carbs = db.Column(db.Float)
    calories_burned = db.Column(db.Float)

    def __init__(self, user_id, calories_eaten, protein, fats, carbs, calories_burned):
        self.user_id = user_id
        self.calories_eaten = calories_eaten
        self.protein = protein
        self.fats = fats
        self.carbs = carbs
        self.calories_burned = calories_burned

with app.app_context():
	db.create_all()


@app.route('/', methods =["GET", "POST"])
def gfg():
	check_if_in_session(session,"calories_burned",0,'h')
	check_if_in_session(session,"calories",0,'h')
	check_if_in_session(session,"protein",0,'h')
	check_if_in_session(session,"fats",0,'h')
	check_if_in_session(session,"carbs",0,'h')
	return render_template("HomePage.html",Calories=session["calories"],Protein=session["protein"],Fats=session["fats"],Carbs=session["carbs"],Burnt=session["calories_burned"])



@app.route('/food.html',methods =["GET", "POST"])
def food():
	if request.method == "POST":
		foodname = request.form.get("fname")
		size = int(request.form.get("serving_size"))
		

		foods_list=search_food(foodname)
		foods_list[0] = map(lambda x: cross_mul(x,size),foods_list[0])
		foods_list[1] = map(lambda x: cross_mul(x,size),foods_list[1])
		foods_list[2] = map(lambda x: cross_mul(x,size),foods_list[2])
		foods_list[3] = map(lambda x: cross_mul(x,size),foods_list[3])
		
		foods_list[0] = list(foods_list[0])
		foods_list[1] = list(foods_list[1])
		foods_list[2] = list(foods_list[2])
		foods_list[3] = list(foods_list[3])
		return render_template("SearchResults.html",food_s=size,name=foods_list[4],calories=foods_list[0],protein=foods_list[1],fats=foods_list[2],carbs=foods_list[3],num=len(foods_list[1]))
	return render_template("food.html")



@app.route('/home.html')
def home():
	return redirect(url_for("gfg"))


@app.route('/exercise.html',methods =["GET", "POST"])
def exercise():
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
			return render_template('exercise.html', result=calories_burned_data)
		else:
			return "Failed to retrieve data. Check your API key or parameters."
	return render_template('exercise.html',result=False)

def get_calories_burned(activity, weight=160, duration=60, api_key='6RQaVycULw0Bmr81aLkfsQ==oJUeFIWk901rnJVk'):
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

@app.route('/about.html')
def about():
	return render_template("about.html")

@app.route('/food.html/diary.html',methods =["GET", "POST"])
def diary():
	protein = carbs = fat = calories = 0.0
	if request.method == "POST":
		
		meal1 = request.form.get("diary_meal_1")
		msize1 = request.form.get("meal_size1")
		
		meal2 = request.form.get("diary_meal_2")
		msize2 = request.form.get("meal_size2")
		
		diary_flist = request.form.getlist("diary_meal_addn")
		diary_flist.append(meal1)
		diary_flist.append(meal2)
		#diary_flist = [i.replace(" ","_") for i in diary_flist ]
		
		meal_slist = request.form.getlist("meal_size_list")
		meal_slist.append(msize1)
		meal_slist.append(msize2)
		meal_slist = [int(i) for i in meal_slist ]

		#food_dict = {diary_flist[i]: meal_slist[i] for i in range(len(diary_flist))}
		#food_dict = {meal1:msize1,meal2:msize2}
		#pdb.set_trace()

		nutr_dict = find_nutr_multiple_v2(food_dict)
		for value in nutr_dict.values():
			protein+=value[0]
			carbs+=value[1]
			fat+=value[2]
			calories+=value[3]

		check_if_in_session(session,"calories",calories,'O')
		check_if_in_session(session,"protein",protein,'O')
		check_if_in_session(session,"fats",fat,'O')
		check_if_in_session(session,"carbs",carbs,'O')


	return render_template("diary.html",Calories=calories)

@app.route('/add_food',methods=["GET", "POST"])
def add_food():
	if request.method == "POST":
		protein = carbs = fat = calories = 0.0
		food_name = str(request.form.get("food_name"))
		calories = float(request.form.get("food_cal"))
		protein = float(request.form.get("food_protein"))
		fats = float(request.form.get("food_fats"))
		carbs = float(request.form.get("food_carbs"))
		#pdb.set_trace()
		check_if_in_session(session,"calories",calories,'O')
		check_if_in_session(session,"protein",protein,'O')
		check_if_in_session(session,"fats",fats,'O')
		check_if_in_session(session,"carbs",carbs,'O')
		
	return redirect(url_for("food"))


@app.route('/add_exercise', methods=["GET", "POST"])
def add_exercise():
    if request.method == "POST":
        cal_burned = float(request.form.get("cals_burned"))
        
        default_calories_eaten = 0.0
        default_protein = 0.0
        default_fats = 0.0
        default_carbs = 0.0
        
        # Create a new Nutrition object with the provided calories burned data
        nutrition_entry = Nutrition(
            user_id=session['user_id'],  # Assuming you have stored user_id in the session
            calories_burned=cal_burned,
            calories_eaten=default_calories_eaten,
            protein=default_protein,
            fats=default_fats,
            carbs=default_carbs
        )
        # Add the new Nutrition object to the session and commit to save it to the database
        db.session.add(nutrition_entry)
        db.session.commit()
        
        # Redirect to the exercise page
        return redirect(url_for("exercise"))

    return render_template('add_exercise.html')	


@app.route('/log_in.html' , methods=["POST","GET"])
def log_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                # Store the username in the session
                session['username'] = username
                session['user_id']=user.id
                session['protein']=0
                session['calories_eaten']=0
                session['carbs']=0
                session['fats']=0
                print(session['user_id'])
                return redirect('/profile.html')  # Redirect to profile page after successful login
            else:
                return "Incorrect password"  # Password does not match
        else:
            return "User not found"  # User with the provided username does not exist

    return render_template('login.html')

@app.route('/profile.html')
def profile():
	return render_template('profile.html')

@app.route('/signup.html',methods=["POST","GET"])
def sign_up():

	if request.method == "POST":
		user_name=request.form['username']
		password=request.form['password']
		new_user =User(username=user_name,password=password,calorie_goal=0)
		
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
	