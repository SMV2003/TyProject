import noms
key = open("D:\\E Drive\\Local Disk\\USDA_API_key.txt" , mode='r').read()
client = noms.Client(key)

def get_foundation_only(query):
    y=[]
    result_1=client.search_query(query)
    for i in result_1.json['items']:
        if i['dataType'] == 'Foundation':
             y.append(i)
    return y

def get_fdcid(name):
    food_list_rough = get_foundation_only(name)
    fdcid = food_list_rough[0]['fdcId']
    return fdcid
    

def create_dict(key,value):
    food_dict=dict({})
    food_dict[key]= value
    return food_dict

def extract_nutrients(food_dictionary):
    food_object = client.get_foods(food_dictionary)
    a = food_object[0].nutrients
    for i in a:
        if i['name'] == 'Protein':
            protein = i['value']
        elif  i['name'] == 'Fat':
            fat = i['value']
        elif  i['name'] == 'Carbs':
            carbs = abs(i['value'])
        elif  i['name'] == 'Calories':
            calories = i['value']
    return [calories,protein,carbs,fat]

def runner_function(name,weight_in_g):
    fdcid = get_fdcid(name)
    food_diary=create_dict(str(fdcid),weight_in_g)
    calories,protein,carbs,fat = extract_nutrients(food_diary)
    if calories == 0.0:
        calories = round(4*protein+4*carbs+9*fat,3)
    print(f"Your food has {calories} calories\n{round(protein,3)}g of protein\n{round(carbs,3)}g of carbs\n{round(fat,3)}g of fats ")
    return f"Your food has {calories} calories\n{round(protein,3)}g of protein\n{round(carbs,3)}g of carbs\n{round(fat,3)}g of fats "

if __name__ == "__main__":
    name = input("Enter name = ")
    runner_function(name,100)
    