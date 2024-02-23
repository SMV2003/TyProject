from flask import Flask, redirect, url_for, render_template, request,sessions
from Foods.search_food import find_nutr_multiple_v2,find_nutr_single 
import pdb

app = Flask(__name__)

@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       foodname = request.form.get("fname")
       #print("food name: ",foodname)
       return find_nutr_single(foodname,100)
    return render_template("HomePage.html")

@app.route('/food.html',methods =["GET", "POST"])
def food():
	if request.method == "POST":
		foodname = request.form.get("fname")
		size = int(request.form.get("serving_size"))
		#food_nutrients = runner_function(foodname,100)
		return find_nutr_single(foodname,size)
	return render_template("food.html")


@app.route('/home.html')
def home():
	return redirect(url_for("gfg"))


@app.route('/exercise.html')
def exercise():
	return render_template("exercise.html")


@app.route('/about.html')
def about():
	return render_template("about.html")

@app.route('/food.html/diary.html',methods =["GET", "POST"])
def diary():
	protein = carbs = fat = calories = 0
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

		food_dict = {diary_flist[i]: meal_slist[i] for i in range(len(diary_flist))}
		#food_dict = {meal1:msize1,meal2:msize2}
		#pdb.set_trace()

		nutr_dict = find_nutr_multiple_v2(food_dict)
		for value in nutr_dict.values():
			protein+=value[0]
			carbs+=value[1]
			fat+=value[2]
			calories+=value[3]
		#return f"Total Calories{calories}"


	return render_template("diary.html",Calories=calories)




if __name__ == "__main__":
	app.run(debug = True)
	