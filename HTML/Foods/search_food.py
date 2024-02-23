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
    print(f"Your food has {calories} calories\n{round(protein,3)}g of protein\n{round(carbs,3)}g of carbs\n{round(fat,3)}g of fats ")
    return f"Your food has {calories} calories\n{round(protein,3)}g of protein\n{round(carbs,3)}g of carbs\n{round(fat,3)}g of fats "


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

if __name__ == "__main__":
    name = input("Enter name = ")
    num = int(input("Enter serving size in grams"))
    runner_function(name,num)
    