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


def extract_nutrients_v2(food_dictionary):
    food_object = client.get_foods(food_dictionary)
    dictio = dict({})
    for food in food_object:
        a = food.nutrients
        
        for i in a:
            #if i['name'] in ['Protein','Carbs','Fat','Calories']:
            if i['name'] == 'Protein':
                protein = i['value']
            elif  i['name'] == 'Fat':
                fat = i['value']
            elif  i['name'] == 'Carbs':
                carbs = abs(i['value'])
            elif  i['name'] == 'Calories':
                calories = i['value']
                
        dictio[food.data['description']] = [protein,carbs,fat,calories]
    return dictio



def find_nutr_single(name,weight_in_g):
    fdcid = get_fdcid(name)
    food_diary=create_dict(str(fdcid),weight_in_g)
    calories,protein,carbs,fat = extract_nutrients(food_diary)
    if calories == 0.0:
        calories = round(4*protein+4*carbs+9*fat,3)
    #print(f"Your food has {calories} calories\n{round(protein,3)}g of protein\n{round(carbs,3)}g of carbs\n{round(fat,3)}g of fats ")
    #return f"Your food has {calories} calories\n{round(protein,3)}g of protein\n{round(carbs,3)}g of carbs\n{round(fat,3)}g of fats "
    protein,carbs,fat = round(protein,3),round(carbs,3),round(fat,3)
    return [calories,protein,carbs,fat]


def find_nutr_multiple(**kwargs):
    req_dict = dict({})
    food_diary = dict({})
    dict_empty = True
    nkeys = []
    for key in kwargs.keys():
        if '_' in key:
            nkeys.append(key)
    nkeys= [i.replace('_',' ') for i in nkeys]
    
    for i in nkeys:
        kwargs[i] = kwargs.pop(i.replace(' ','_'))
   
    for key,value in kwargs.items():
        fdcid = get_fdcid(key)
        #food_diary={str(fdcid):value}
        food_diary[str(fdcid)]=value
   
    nutrient_dict = extract_nutrients_v2(food_diary)
    for key,value in nutrient_dict.items():
            #[protein,carbs,fat,calories] = value
        if value[3] == 0.0:
            value[3] = round(4*value[0]+4*value[1]+9*value[2],3)
        value = [round(i,3) for i in (value[3],value[0],value[1],value[2])]
    req_dict[key] = value
    
    return nutrient_dict


def find_nutr_multiple_v2(mydict):
    req_dict = dict({})
    food_diary = dict({})
    dict_empty = True

    for key,value in mydict.items():
        fdcid = get_fdcid(key)
        food_diary[str(fdcid)]=value

    nutrient_dict = extract_nutrients_v2(food_diary)

    for key,value in nutrient_dict.items():
            #[protein,carbs,fat,calories] = value
        if value[3] == 0.0:
            value[3] = round(4*value[0]+4*value[1]+9*value[2],3)
        value = [round(i,3) for i in (value[3],value[0],value[1],value[2])]
    req_dict[key] = value
    return nutrient_dict

def find_calories_for_search(results):
    calories = []
    for j in results.json['items']:
        for i in j['foodNutrients']:
            if i['nutrientId']== 1008:
                calories.append(i['value'])
    return calories

def search_food(foodname):
    """
    Searches for nutritional information of a given food using the USDA API with noms.

    Parameters:
    - foodname (str): The name of the food to search for.

    Returns:
    - list: A list containing the following elements:
        - calories (list): List of calorie values for each food item found.
        - protein (list): List of protein values for each food item found.
        - fats (list): List of fat values for each food item found.
        - carbs (list): List of carbohydrate values for each food item found.
        - description_of_foods (list): List of descriptions for each food item found.

    Note:
    - This function utilizes the noms to search for food items in USDA API and retrieve their nutritional information.
    - The 'client' object used to make API requests should be instantiated beforehand.
    - The 'find_nutr_for_search' function is expected to be defined elsewhere and should return lists of nutritional values.
    """
    results = client.search_query(foodname)
    if results.json == None:
        return 0
    description_of_foods = [i['description'] for i in results.json['items']]
    #fdcid_of_foods = [i['fdcId'] for i in results.json['items']]   
    calories,protein,fats,carbs = find_nutr_for_search(results)
    #if len(description_of_foods)==len(fdcid_of_foods)==len(calories):
        #count = len(calories)
        #for name,cals in zip(description_of_foods,calories):
            #print(name,cals,'Calories') 
    return [calories,protein,fats,carbs,description_of_foods]

def cross_mul(for_100,req_wt):
    req_nutr = (req_wt*for_100)/100
    return round(req_nutr,2)

def find_nutr_for_search(results):
    """
    Extracts nutritional information from the search results obtained from the noms.

    Parameters:
    - results (object): The search results obtained from the Nutritionix API.

    Returns:
    - tuple: A tuple containing the following lists:
        - calories (list): List of calorie values for each food item found.
        - protein (list): List of protein values for each food item found.
        - fats (list): List of fat values for each food item found.
        - carbs (list): List of carbohydrate values for each food item found.

    Note:
    - This function iterates through the search results obtained and extracts nutritional information
      such as calories, protein, fats, and carbohydrates for each food item.
    - The 'results' parameter is expected to contain the JSON response obtained from the Nutritionix API search query.
    - Each food item in the search results may have multiple nutritional values, which are extracted based on the 'nutrientId' 
      provided in the JSON response.
    - Nutrient IDs used:
        - 1003: Protein
        - 1004: Fats
        - 1005: Carbohydrates
        - 1008: Calories
    """
    calories = []
    carbs = []
    fats = []
    protein = []
    
    
    for j in results.json['items']:
        for i in j['foodNutrients']:
            if i['nutrientId']== 1003:
                protein.append(i['value'])
            if i['nutrientId']== 1004:
                fats.append(i['value'])
            if i['nutrientId']== 1005:
                carbs.append(i['value'])
            if i['nutrientId']== 1008:
                calories.append(i['value'])
            
    return calories,protein,fats,carbs

def check_if_in_session(session,string_to_check,value,page):
    """
    Checks if a specific string exists in the session dictionary. If not, it adds it with a default value or a specified value.
    If the string already exists, it updates its value by adding the provided value.

    Parameters:
    - session (dict): The session dictionary where the string and its value will be stored or updated.
    - string_to_check (str): The string to check for in the session dictionary.
    - value (float): The value to add to or update the string's value in the session dictionary.
    - page (str): A flag indicating the type of page ('h' for home page, any other value for other pages).

    Returns:
    - None: The function directly updates the session dictionary.

    Note:
    - This function is useful for maintaining session data in web applications.
    - It checks if a specific string exists in the session dictionary. If not, it adds the string with a default value
      (0.0) for the home page or with the specified value for other pages.
    - If the string already exists in the session dictionary, it updates its value by adding the provided value.
    - The 'session' parameter is expected to be a dictionary where session data is stored.
    - The 'string_to_check' parameter is the key to check in the session dictionary.
    - The 'value' parameter is the value to add to or update the string's value in the session dictionary.
    - The 'page' parameter is a flag indicating the type of page. If 'h', it represents the home page; otherwise, it 
      indicates other pages.
    """

    if string_to_check not in session:
        if page == 'h':
            session[string_to_check] = 0.0
        else:
            session[string_to_check] = value
    else:
        session[string_to_check] += value

if __name__ == "__main__":
    name = input("Enter name = ")
    num = int(input("Enter serving size in grams"))
    runner_function(name,num)
    