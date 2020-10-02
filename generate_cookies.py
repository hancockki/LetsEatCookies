import selenium
import numpy
import random
import re
from cookie_classes import Recipe
from cookie_classes import BaseIngredient
from cookie_classes import AddIns

from webscrape import getCookieRecipes

# WHERE TO GO...

"""

"""
def buildNewRecipe(base_ingredients, add_ins, recipe_objects, name):
    base_ingredients_recipe = []
    add_ins_recipe = []

    for i in base_ingredients.values():
        base_ingredients_recipe.append({i.name: i.getQuantity()})
    
    #genetic algorithm for add-ins

    num1 = random.randint(0,len(recipe_objects)-1)
    num2 = random.randint(0,len(recipe_objects)-1)

    add_ins_recipe_1 = recipe_objects[num1].add_ins
    add_ins_recipe_2 = recipe_objects[num2].add_ins

    size_addins_1 = len(add_ins_recipe_1)
    size_addins_2 = len(add_ins_recipe_2)

    pivot1 = random.randint(0,size_addins_1)
    pivot2 = random.randint(0,size_addins_2)

    for i in range(0,pivot1):
        print("KEYS" , list(add_ins_recipe_1[i].keys())[0])

        add_ins_recipe.append({list(add_ins_recipe_1[i].keys())[0] : add_ins[list(add_ins_recipe_1[i].keys())[0]].getQuantity()})
    for i in range(pivot2, size_addins_2):
        #add_ins_recipe.append({add_ins_recipe_2[i].keys() : add_ins[add_ins_recipe_2[i].keys()].getQuantity()})
        #add_ins_recipe.append({add_ins_recipe_2[i].name : add_ins_recipe_2[i].getQuantity()})
        print("NEW QUANTITY", add_ins[list(add_ins_recipe_2[i].keys())[0]].getQuantity())
        add_ins_recipe.append({list(add_ins_recipe_2[i].keys())[0] : add_ins[list(add_ins_recipe_2[i].keys())[0]].getQuantity()})



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
        next_recipe = Recipe(recipe, base_ingredients=[], add_ins=[])
        for ingredient in recipes[recipe]: #loop through ingredients of this recipe
            for i in base_ingredients.keys():
                done = False # use this boolean to break the loop once we have matched from base ingredients
                if i in ingredient[0]:
                    # match the ingredient quantity
                    q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]+(.[0-9]+))*\s[a-zA-Z]+', ingredient[1])
                    if q is not None: #if we got a match
                        quantity = q.group()
                        # edge cases
                        if 'egg' in quantity:
                            quantity = quantity.replace('egg','')
                        if 'all' in quantity:
                            quantity = quantity.replace('all', 'cup')
                        # update ingredeint quantity
                        base_ingredients[i].updateQuantity(quantity)
                        done = True
                        next_recipe.base_ingredients.append({i:quantity})
                        break
            # this means it is an add-in
            if not done:
                q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]*(.[0-9]+))*\s[a-zA-Z]+', ingredient[1])
                if 'cornstarch' in ingredient[1]:
                    name = 'cornstarch'
                else:
                    name = ingredient[0]
                    #name = ingredient.split(" ")
                    #name = " ".join(name[2:]).strip("*")
                print(name)
                # if we got a match
                if q is not None:
                    quantity = q.group()
                    if 'cornstarch' in quantity:
                        quantity = quantity.replace('cornstarch', 'teaspoon')
                    # if we already have this add-in
                    if name in add_ins.keys():
                        add_ins[name].updateQuantity(quantity)
                        next_recipe.add_ins.append({name:quantity})
                    else: # create new add-in object
                        new_add_in = AddIns(name=name, quantities={})
                        new_add_in.updateQuantity(quantity)
                        add_ins[name] = new_add_in
                        next_recipe.add_ins.append({name:quantity})
        recipe_objects.append(next_recipe)

    for value in base_ingredients.values():
        print(value.name)
        print(value.quantities)

    for value in add_ins.values():
        print(value.name)
        print(value.quantities)

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
        for ingredient in recipe.base_ingredients:
            for key, value in ingredient.items():
                new_recipe.write(key + " " + str(value) + "\n")
        for ingredient in recipe.add_ins:
            for key, value in ingredient.items():
                new_recipe.write(key + " " + str(value) + "\n")
    new_recipe.close()




def main():
    recipes = getCookieRecipes(['https://sallysbakingaddiction.com/pumpkin-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/peanut-butter-cookies/', 'https://sallysbakingaddiction.com/soft-chewy-oatmeal-raisin-cookies/', \
    'https://sallysbakingaddiction.com/crispy-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/bunny-sugar-cookies/','https://sallysbakingaddiction.com/dark-chocolate-cranberry-almond-cookies/', \
        'https://sallysbakingaddiction.com/zucchini-oatmeal-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/cookies-n-cream-cookies/', 'https://sallysbakingaddiction.com/oreo-cheesecake-cookies/'])
    base_ingredients, add_ins, recipe_objects = getInspiringSet(recipes)
    for recipe in recipe_objects:
        writeToFile(recipe)
    for i in range(5):
        new_recipe = buildNewRecipe(base_ingredients, add_ins, recipe_objects, "new_recipe" + str(i))
        print("NEWRECIPE")
        print(new_recipe.add_ins, new_recipe.base_ingredients)
        writeToFile(new_recipe)





"""
Driver for the entire program
"""
if __name__ == "__main__":
    main()


