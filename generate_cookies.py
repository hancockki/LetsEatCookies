import selenium
import numpy
import random
import re
from cookie_classes import Recipe
from cookie_classes import BaseIngredient
from cookie_classes import AddIns
import os
import json
from difflib import SequenceMatcher

from driver import getCookieRecipes

# WHERE TO GO...

"""

"""
def buildNewRecipe(base_ingredients, add_ins, recipe_objects):
    base_ingredients_recipe = {}
    add_ins_recipe = {}

    for i in base_ingredients.values():
        base_ingredients_recipe[i.name]=i.getQuantity()
    
    #genetic algorithm for add-ins

    num1 = random.randint(0,len(recipe_objects)-1)
    num2 = random.randint(0,len(recipe_objects)-1)

    add_ins_recipe_1 = recipe_objects[num1].add_ins
    add_ins_recipe_2 = recipe_objects[num2].add_ins

    size_addins_1 = len(add_ins_recipe_1)
    size_addins_2 = len(add_ins_recipe_2)

    pivot1 = random.randint(0,size_addins_1)
    pivot2 = random.randint(0,size_addins_2)

    """
    Here we could add some sort of similarity check, to see if the ingredients we are adding go together!

    """
    for i in range(0,pivot1):
        print("KEYS" , list(add_ins_recipe_1.keys())[i])

        add_ins_recipe[list(add_ins_recipe_1.keys())[i]] = add_ins[list(add_ins_recipe_1.keys())[i]].getQuantity()
    for i in range(pivot2, size_addins_2):
        #add_ins_recipe.append({add_ins_recipe_2[i].keys() : add_ins[add_ins_recipe_2[i].keys()].getQuantity()})
        #add_ins_recipe.append({add_ins_recipe_2[i].name : add_ins_recipe_2[i].getQuantity()})
        #print("NEW QUANTITY", add_ins[list(add_ins_recipe_2[i].keys())[0]].getQuantity())
        add_ins_recipe[list(add_ins_recipe_2.keys())[i]] = add_ins[list(add_ins_recipe_2.keys())[i]].getQuantity()

    name = getName(add_ins_recipe)
    new_recipe = Recipe(name=name, base_ingredients=base_ingredients_recipe, add_ins=add_ins_recipe)
    #adding in mix-ins ???? discuss later
 
    return new_recipe


"""
In this method, we are building our inspiring set

@params:
    recipes --> list of recipes from webcrawl, with the name mapped to the ingredients

@returns:

"""
def getInspiringSet(recipes):
    recipe_objects = []

    #need to extract the quantities dictionary for each 

    # BASE INGREDIENTS #
    base_ingredients = {}
    add_ins = {}
    base_ingredients["all-purpose flour"] = BaseIngredient(name="all-purpose flour",quantities={})
    base_ingredients["egg"] = BaseIngredient(name="egg", quantities={})
    base_ingredients["granulated sugar"] = BaseIngredient(name="granulated sugar", quantities={})
    base_ingredients["brown sugar"] = BaseIngredient(name="brown sugar", quantities={})
    base_ingredients["butter"] = BaseIngredient(name="butter", quantities={})
    base_ingredients["salt"] = BaseIngredient(name="salt", quantities={})
    base_ingredients["baking soda"] = BaseIngredient(name="baking soda", quantities={})
    base_ingredients["baking powder"] = BaseIngredient(name="baking powder", quantities={})

    # update quantities dictionary for each of the base ingredients
    for recipe in recipes:
        #initialize next Recipe object
        next_recipe = Recipe(recipe, base_ingredients={}, add_ins={})
        for ingredient in recipes[recipe]: #loop through ingredients of this recipe
            done = False # use this boolean to break the loop once we have matched from base ingredients
            for i in base_ingredients.keys():
                #if i in ingredient[0]:
                #print(SequenceMatcher(None, i, ingredient[0]).ratio())
                if SequenceMatcher(None, i, ingredient[0]).ratio() > 0.8 or i in ingredient[0]:
                    done = True
                    # match the ingredient quantity
                    q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]+(.[0-9]+))*(\s[a-zA-Z]+)*', ingredient[1])
                    if q is not None: #if we got a match
                        quantity = q.group()
                        # edge cases
                        if 'flour' in i:
                            if 'cup' not in quantity:
                                print("NO CUPSSSSSS", i, quantity)
                                quantity += " cup"
                        if 'brown' in i:
                            if 'cup' not in quantity:
                                print("NO CUPSSSSSS", i, quantity)
                                quantity += " cup"

                        if 'egg' in quantity:
                            quantity = quantity.replace('egg','')
                        if 'all' in quantity:
                            quantity = quantity.replace('all', 'cup')
                        if 'salt' in i:
                            if 'cup' in quantity:
                                quantity = quantity.replace('cup', 'teaspoon')
                        # update ingredeint quantity
                        base_ingredients[i].updateQuantity(quantity)
                        next_recipe.base_ingredients[i]=quantity
            # this means it is an add-in
            if not done:
                q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]*(.[0-9]+))*(\s[a-zA-Z]+)*', ingredient[1])
                # edge cases
                if 'cornstarch' in ingredient[1]:
                    name = 'cornstarch'
                if 'cream cheese' in ingredient[0]:
                    name = "cream cheese"
                else:
                    name = ingredient[0].strip('*')

                # if we got a match
                if q is not None:
                    quantity = q.group()
                    # edge cases
                    if 'almonds' in name:
                        name = 'almond'
                    if 'vanilla extract' in name:
                        name = "vanilla"
                    if 'cinnamon' in name:
                        name = 'cinnamon'
                    if 'allspice' in name:
                        name = "allspice"
                    if 'cornstarch' in quantity:
                        quantity = quantity.replace('cornstarch', 'teaspoon')
                        if "teaspoon" not in quantity:
                            quantity += " teaspoon"
                    if 'cream cheese' in name:
                        if 'cup' not in quantity:
                            quantity += " cup"
                    # if we already have this add-in
                    if name in add_ins.keys():
                        add_ins[name].updateQuantity(quantity)
                        next_recipe.add_ins[name]=quantity
                    else: # create new add-in object
                        new_add_in = AddIns(name=name, quantities={})
                        new_add_in.updateQuantity(quantity)
                        add_ins[name] = new_add_in
                        next_recipe.add_ins[name]=quantity
        recipe_objects.append(next_recipe)

    for value in base_ingredients.values():
        print("Base Ingredient:", value.name)
        print("Quantities:", value.quantities)

    for value in add_ins.values():
        print("Add in:", value.name)
        print("Quantities: ", value.quantities)

    for recipe in recipe_objects:
        print(recipe.name)
        print(recipe.base_ingredients)
        print(recipe.add_ins)

    return base_ingredients, add_ins, recipe_objects

"""
Write recipe to a file

@params:
    recipe --> recipe object
"""
def writeToFile(recipe):
    with open("recipes/" + recipe.name + ".txt", 'w') as new_recipe:
        new_recipe.write(recipe.name + "\n")
        for key, value in recipe.base_ingredients.items():
            new_recipe.write(str(value) + " " + key + "\n")
        for key, value in recipe.add_ins.items():
            new_recipe.write(str(value) + " " + key + "\n")
    new_recipe.close()

def getName(add_ins):
    if len(add_ins) > 1:
        int1 = random.randint(0, len(add_ins) - 1)
        int2 = random.randint(0, len(add_ins) - 1)
        
        name1 = list(add_ins.keys())[int1] #grab name attribute of the index of the addin from our master list
        name2 = list(add_ins.keys())[int2]

        name = name1.capitalize() + " " + name2.capitalize() + " Cookies"
    else:
        name = "name is boring"

    return name




def main():
    print("Checking to see if inspiring set json already exists")
    try:
        if os.path.getsize('recipes.json') > 0:
            print("File already exists!")
            with open('recipes.json') as json_file: 
                recipes = json.load(json_file)
    except:
        print("json file is empty or does not exist")
        recipes = getCookieRecipes(['https://sallysbakingaddiction.com/white-chocolate-chai-snickerdoodles/','https://sallysbakingaddiction.com/biscoff-chocolate-chip-cookies/', \
            'https://sallysbakingaddiction.com/white-chocolate-cranberry-pistachio-cookies/','https://sallysbakingaddiction.com/pumpkin-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/peanut-butter-cookies/', 'https://sallysbakingaddiction.com/soft-chewy-oatmeal-raisin-cookies/', \
        'https://sallysbakingaddiction.com/crispy-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/bunny-sugar-cookies/','https://sallysbakingaddiction.com/dark-chocolate-cranberry-almond-cookies/', \
            'https://sallysbakingaddiction.com/zucchini-oatmeal-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/cookies-n-cream-cookies/', 'https://sallysbakingaddiction.com/oreo-cheesecake-cookies/', \
            'https://sallysbakingaddiction.com/chewy-oatmeal-mm-cookies/'])
    base_ingredients, add_ins, recipe_objects = getInspiringSet(recipes)
    for recipe in recipe_objects:
        writeToFile(recipe)


    # loop to generate cookies
    for i in range(5):
        new_recipe = buildNewRecipe(base_ingredients, add_ins, recipe_objects)
        new_recipe.name = getName(new_recipe.add_ins)
        print("NEWRECIPE")
        #print(new_recipe.add_ins, new_recipe.base_ingredients)
        writeToFile(new_recipe)
        new_recipe.fitnessFunction()



"""
Driver for the entire program
"""
if __name__ == "__main__":
    main()


