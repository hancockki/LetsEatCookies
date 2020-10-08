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
from flavorpairing import pairing
from webcrawl import getCookieRecipes
from itertools import product
import flavorpairing as fp
from operator import attrgetter


"""

"""
def buildNewRecipe(base_ingredients, add_ins, recipe_objects):
    base_ingredients_recipe = {}
    add_ins_recipe = {}

    # include one of every base ingredient, picking the quantities probabilistically from those in inspiring set
    for i in base_ingredients.values():
        base_ingredients_recipe[i.name]=i.getQuantity()
    
    # sort recipe objects by fitness 
    objects_sorted_order = sorted(recipe_objects, key=attrgetter("fitness"), reverse=True)
    for i in objects_sorted_order:
        print(i.fitness, i.name)

    # pick best 2 by fitness
    add_ins_recipe_1 = objects_sorted_order[0].add_ins
    add_ins_recipe_2 = objects_sorted_order[1].add_ins

    #this is the list of all possible pairs of add-ins from our best two recipes
    #product is a method that returns all the pairs
    output = list(product(add_ins_recipe_1.keys(), add_ins_recipe_2.keys()))
    #print("OUTPUT", output)

    best_fit = {"M&Ms": "chocolate", "pumpkin puree": "pumpkin", "molasses": "honey", "white chocolate morsels": "chocolate", "dried cranberries": "cranberry", \
            "almond extract": "almond", "semi-sweet chocolate": "chocolate", "pistachios":"pistachio", "chocolate chips": "chocolate", "Biscoff spread": "cinnamon", \
            "pumpkin pie spice": "allspice", "bittersweet chocolate":"chocolate", "raisins":"raisin", "pure maple syrup":"honey", "semi-sweet chocolate chips":"chocolate", \
            "white chocolate chips":"chocolate", "ground ginger":"ginger","ground cardamom":"cardamom", "Oreos":"chocolate"}
    
    #initialize values dictionary where we map our ingredient pairs to their similarity
    values = {}

    # loop through the add-ins in our best two recipes
    already_checked = []
    for combination in output:
        if combination[0] == combination[1]: # if both recipes share an add-in, ignore
            continue
        else:
            if combination[0] in best_fit: # if it's in our best fit dictionary
                ingredient1 = best_fit[combination[0]]
            else:
                ingredient1 = combination[0]
            if combination[1] in best_fit: #if ingredient 2 is in our best fit dictionary
                ingredient2 = best_fit[combination[1]]
            else:
                ingredient2 = combination[1]
            if ingredient1 == ingredient2: # again, if they are the same, ignore
                continue
            if (ingredient1, ingredient2) in already_checked:
                #print("ALREADY CHECKED the pair", ingredient1, " ", ingredient2)
                continue
            #print("now checking", ingredient1, " ", ingredient2)
            try:
                similarity = fp.similarity(ingredient1, ingredient2)
                already_checked.append((ingredient1, ingredient2))
                already_checked.append((ingredient2, ingredient1))
            except KeyError:
                print("whoops! key error: ", ingredient1, " and ", ingredient2, " were not able to be compared")
                continue
            values[combination] = similarity
    #print(values)

    #sort keys in our dictionary by their similarity, pick best ones based on random number
    # add_ins_recipe_1 is the number of add-ins from our first recipe, WE CAN CHANGE THIS
    new_ingredients =  list(sorted(values, key=values.get, reverse=True))[0:len(add_ins_recipe_1)]

    # WE NEED TO IMPROVE THIS maybe
    for ingredient in new_ingredients:
        if ingredient[0] not in add_ins_recipe.keys():
            quantity = add_ins[ingredient[0]].getQuantity()
            add_ins_recipe[ingredient[0]] = quantity
            add_ins[ingredient[0]].updateQuantity(quantity)
        if ingredient[1] not in add_ins_recipe.keys():
            quantity = add_ins[ingredient[1]].getQuantity()
            add_ins_recipe[ingredient[1]] = add_ins[ingredient[1]].getQuantity()
            add_ins[ingredient[1]].updateQuantity(quantity)

    # pick a name for our new recipe
    name = getName(add_ins_recipe)
    new_recipe = Recipe(name=name, base_ingredients=base_ingredients_recipe, add_ins=add_ins_recipe)

    # TODO::: CALL MUTATION FUNCTIONS with random probability
 
    return new_recipe

"""
 
"""
def generalize_mutation(add_ins_2):
    # dictionary mapping add in name to 'best fit' name 
    best_fit = {"M&Ms": "chocolate", "pumpkin puree": "pumpkin", "molasses": "honey", "white chocolate morsels": "chocolate", "dried cranberries": "cranberry", \
        "almond extract": "almond", "semi-sweet chocolate": "chocolate", "pistachios":"pistachio", "chocolate chips": "chocolate", "Biscoff spread": "cinnamon", \
            "pumpkin pie spice": "allspice", "bittersweet chocolate":"chocolate", "raisins":"raisin", "pure maple syrup":"honey", "semi-sweet chocolate chips":"chocolate", \
                "white chocolate chips":"chocolate", "ground ginger":"ginger","ground cardamom":"cardamom"}
    # randomly select if you mutate first or second list
    add_in_list_num = int1 = random.randint(0, 1)
    add_in_list = add_ins_2
    if add_in_list == 1:
        add_in_list = add_ins_2 #change to 1
    ingredient_pairings = {} 
    for add_in in add_in_list.keys():
        add_in_amount = add_in_list[add_in]   #.quantities
        try: # try to find similarity
            if add_in in best_fit: # if it's in our best fit dictionary
                ingredient = best_fit[add_in]
                #print("Add in: " + add_in + " Ingredient: " + ingredient)
                pairs = pairing(ingredient, .5)
                for key in pairs.keys():
                    #print("Keys: " + key)
                    ingredient_pairings[key] = add_in_amount
                    #print(ingredient_pairings)
        except KeyError: # we didn't find the ingredient in our database
            print("not found in database")
    dict_keys = list(ingredient_pairings.keys())
    rand_index = random.randint(0, len(dict_keys) - 1)
    rand_key = dict_keys[rand_index]
    add_in_list[rand_key] = ingredient_pairings[rand_key]
    #print(add_in_list)
    print(add_in_list[rand_key].name)
    return add_in_list[rand_key]

    # Find ingredients that are similar in the .npy files
    # Add ingredients that go well, add the same amount as the similar ingredient (Change this?)
    # Use the amount of the origional ingredient for the similar



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

    """
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
    """

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

"""
"""
def getName(add_ins):    
    if len(add_ins) > 1:
        int1 = random.randint(0, len(add_ins) - 1)
        int2 = random.randint(0, len(add_ins) - 1)
        if int1 == int2:
            int2 = random.randint(0, int1)
        
        name1 = ""
        name2 = ""
        # to make sure we aren't adding the same add in ingredient to the name
        while name1 != name2:
            name1 = list(add_ins.keys())[int1] #grab name attribute of the index of the addin from our master list
            name2 = list(add_ins.keys())[int2]

        name = name1.capitalize() + " " + name2.capitalize() + " Cookies"
    else:
        name = "name is boring"

    return name


"""
Main method, used to run the program. First, checks to see if our hard-coded json data for the webcrawl exists (since we don't want to
run the webcrawl more than needed as it's slow). If it exists, load the json file into the dictionary format we want.

Then, creates the inspiring set based on the json. The inspiring set method returns our base ingredients, add ins, and recipe objects.

Finally, uses the inspiring set to generate new recipes, updating the add_ins dictionary as needed.
"""
def main():
    # check to see if our data set is already hard-coded
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

    # generate our inspiring set
    base_ingredients, add_ins, recipe_objects = getInspiringSet(recipes)

    # loop through recipe objects and write to file
    for recipe in recipe_objects:
        writeToFile(recipe)
        recipe.fitnessFunction()

    # loop to generate cookies
    for i in range(10):
        new_recipe = buildNewRecipe(base_ingredients, add_ins, recipe_objects)
        print("NEWRECIPE")
        #print(new_recipe.add_ins, new_recipe.base_ingredients)
        new_recipe.fitnessFunction()
        recipe_objects.append(new_recipe)

        add_in = new_recipe.mutation(add_ins)
        if add_in is not None:
            #print("ADDED========", add_in)
            if add_in not in add_ins.keys(): # if we havent already created a add in object for this
                new_add_in = AddIns(name=add_in, quantities={})  #create new add_in object for this 
                new_add_in.updateQuantity(new_recipe.add_ins[add_in])
                add_ins[add_in] = new_add_in
            else:
                add_ins[add_in].updateQuantity(new_recipe.add_ins[add_in])

        new_recipe.name = getName(new_recipe.add_ins)
        writeToFile(new_recipe)

        #for ingredient in new_recipe.add_ins:
            #print("new recipe add in", ingredient)

        printInstructions(new_recipe)


"""
Prints out the recipe instructions to be called in main. Mostly hard-coded, but specifically includes the 
recipe add-ins, the correct quantity of eggs, and a narrowly-randomized bake-time.

@params:
    new_recipe --> the current recipe for which we want to print the instructions
"""
def printInstructions(new_recipe):
    print("1. Preheat your oven to 350 degrees Fahrenheit and line baking sheets with parchment paper.\n")
    print("2. Whisk the dry ingredients together in a large bowl.\n")
    for base in new_recipe.base_ingredients.keys():
        if base == "egg":
            egg_quantity = int(new_recipe.base_ingredients[base])

    if egg_quantity > 1:
        egg_string = str(egg_quantity) + " eggs "
    else:
        egg_string = "1 egg "

    print("3. In a separate bowl, cream the butter and both sugars together until smooth. Add " + egg_string + "and the rest of the wet ingredients.\n")
    print("4. Add your wet ingredients to the dry ingredients until combined.\n")

    add_ins_string = "" # string that will store the different add ins, formatted nicely
    for add_in in new_recipe.add_ins.keys():
        #print(add_in)
        add_ins_string += add_in + ", "
        last_add_in = add_in
        last_add_in_string = add_in + ", "
    
    add_ins_s = add_ins_string[:len(add_ins_string)-len(last_add_in_string)]
    add_ins_s += "and " + last_add_in

    print("5. Add the " + add_ins_s + " and mix until all combined, and a dough forms.\n")
    print("6. Roll the cookie dough into medium-sized scoops and place 3 inches apart on the baking sheet.\n")
        
    min_time = random.randint(7,10)
    max_time = random.randint(10, 15)

    print("7. Bake for " + str(min_time) + "-" + str(max_time) + " minutes or until edges appear set.\n")
    print("8. Remove from the oven and allow to cool on the baking sheet for 5 minutes then transfer to a wire rack to cool.\n")
    print("9. Enjoy!\n")

"""
Driver for the entire program
"""
if __name__ == "__main__":
    main()


