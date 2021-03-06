"""
Authors: Kim H, Kayla S, Lydia P
CSCI 3725 - Computational Creativity
Party Quest 2: Smart Cookies
Last Modified: Oct 16, 2020

The purpose of this program is to use cookie recipes from the internet to generate new recipes 
with creative ingredients! We are using recipes from Sally's Baking as the recipes on this site
are really fun and lots of them have unique add-ins that we can use! We hace named our system
GECCO - Genetically Exploring Creative Cookie Options.

This file includes the main fuction for our program and utilizes cookie_classes, flavorpairing.py, 
ingred_categories.npy, and ingred_word_emb.npy and recipes.json. We first check to see if our 
hard-coded json datafor the webcrawl exists (since we don't want to run the webcrawl more than 
needed as it's slow). If it exists, load the json file into the dictionary format we want. After
building our inspiring set, we call call generate_recipes.

Known bugs:
Currently, Bunny Sugar Cookies in our inspiring set does not have quantities for butter or salt. 
We explain the reason for this in the docstring of webcrawl.py
This is not really a bug, but isn't really great for our inspiring set!
"""


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
from webcrawl import get_cookie_recipes
from itertools import product
import flavorpairing as fp
from operator import attrgetter


def build_new_recipe(base_ingredients, add_ins, recipe_objects):
    """This method builds a new cookie recipe based on our base_ingredient, add_ins, and recipe_objects. It first picks two recipes probabilistically based
    on their fitness (higher fitness=higher chance of being picked), then picks add-ins from these based on the flavor pairings between the recipes.

    @params:
        base_ingredients --> dictionary mapping the name of the ingredinet (as a string) to the BaseIngredient object
        add_ins --> dictionary mapping the name of the add-in (as a string) to the addIn object
        recipe_objects --> list of Recipe objects made so far

    @returns:
        new_recipe --> the new recipe object we've made
    """
    #dictionary to store the base ingredients of our new recipe
    base_ingredients_new_recipe = {} 

    # include one of every base ingredient, picking the quantities probabilistically from those in inspiring set
    for i in base_ingredients.values():
        base_ingredients_new_recipe[i.name]=i.get_quantity()

    # here, we get the fitness of each recipe and add to list, which we will use to pick the recipes
    weights = []
    for i in recipe_objects:
        weights.append(i.fitness)

    #pick two recipes with probability proportional to fitness
    choices = random.choices(recipe_objects, weights, k=2)
    add_ins_recipe_1 = choices[0].add_ins
    add_ins_recipe_2 = choices[1].add_ins
    best_fit = choices[0].best_fit
    add_ins_new_recipe = get_add_ins_new_recipe(add_ins_recipe_1, add_ins_recipe_2, add_ins, best_fit)
    
    # pick a name for our new recipe
    name = create_recipe_name(add_ins_new_recipe)
    new_recipe = Recipe(name=name, base_ingredients=base_ingredients_new_recipe, add_ins=add_ins_new_recipe)
    return new_recipe


def get_add_ins_new_recipe(add_ins_recipe_1, add_ins_recipe_2, add_ins, best_fit):
    """
    This method picks the add-ins for our new recipe. It does so by computing the similarity between all combinations of two add-ins across our recipe objects. So,
    if one recipe has "chocolate chips, vanilla" and another has "craisins, cream cheese", then it will compute the flavor similarities of (chocolate chips, vanilla), (chocolate chips, craisins),
    (chocolate chips, cream cheese), etc, until all pairs are considered.

    Then, a random number between 0 and the number of add-ins total is chosen, and that number of add-ins is picked probabilistically based on their similarities.

    @params:
        add_ins_recipe_1 --> add ins from our first parent recipe
        add_ins_recipe_2 --> add ins from our second parent recipe
        add_ins --> OVERALL add_ins data structure across all recipes, storing quantities

    @ returns:
        add_ins_new_recipe --> add ins for our new recipe
    """
    #this is the list of all possible pairs of add-ins from our best two recipes. product is a method that returns all the pairs
    output = list(product(add_ins_recipe_1.keys(), add_ins_recipe_2.keys()))
    #initialize ingredient pairs list and similarities list. Used later in the code to pick our add ins
    ingredient_pairs = []
    similarities = []
    # we make this so we don't compute the exact same tuple twice (the thought here is that multiple add-ins are the same best fit)
    already_checked = [] 
    
    # loop through the add-ins in our best two recipes
    for combination in output:
        # if both recipes share an add-in, ignore
        if combination[0] == combination[1]: 
            continue
        else:
            # if it's in our best fit dictionary
            if combination[0] in best_fit: 
                ingredient1 = best_fit[combination[0]]
            else:
                ingredient1 = combination[0]
            #if ingredient 2 is in our best fit dictionary    
            if combination[1] in best_fit: 
                ingredient2 = best_fit[combination[1]]
            else:
                ingredient2 = combination[1]
            # again, if they are the same, ignore
            if ingredient1 == ingredient2: 
                continue
            if (ingredient1, ingredient2) in already_checked:
                #print("ALREADY CHECKED the pair", ingredient1, " ", ingredient2)
                continue
            try:
                similarity = fp.similarity(ingredient1, ingredient2)
                already_checked.append((ingredient1, ingredient2))
                already_checked.append((ingredient2, ingredient1))
            except KeyError:
                #print("whoops! key error: ", ingredient1, " and ", ingredient2, " were not able to be compared")
                ingredient_pairs.append(combination)
                # set to low probability
                similarities.append(0.2) 
                continue
            ingredient_pairs.append(combination)
            similarities.append(similarity)

    #pick random number of add-ins based on probability. Probability determined by similarities
    # get number of add-ins
    num_add_ins = random.randint(0, len(ingredient_pairs)-1) 
    # ingredients we are addings 
    new_add_ins = random.choices(ingredient_pairs, similarities, k=num_add_ins) 
    # initialize dictionary for new add ins 
    add_ins_new_recipe = {} 

    # loop through new ingredients list
    for ingredient in new_add_ins:
         # if we haven't added the ingredient already
        if ingredient[0] not in add_ins_new_recipe.keys():
            # get a quantity
            quantity = add_ins[ingredient[0]].get_quantity() 
            add_ins_new_recipe[ingredient[0]] = quantity
            add_ins[ingredient[0]].update_quantity(quantity)
        if ingredient[1] not in add_ins_new_recipe.keys():
            quantity = add_ins[ingredient[1]].get_quantity()
            add_ins_new_recipe[ingredient[1]] = add_ins[ingredient[1]].get_quantity()
            add_ins[ingredient[1]].update_quantity(quantity)

    return add_ins_new_recipe


def get_inspiring_set(recipes):
    """
    In this method, we are building our inspiring set

    @params:
        recipes --> list of recipes from webcrawl, with the name mapped to the ingredients

    @returns:

    """
    recipe_objects = []
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
            got_base = False
            for i in base_ingredients.keys():
                if SequenceMatcher(None, i, ingredient[0]).ratio() > 0.8 or i in ingredient[0]:
                    got_base = update_base_ingred_data_set(ingredient, next_recipe, base_ingredients, i)
            # this means it is an add-in
            if not got_base:
                # the following regex can be used to match the name of the ingredient from the webcrawl. Uncomment out if naming errors arise
                #q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]*(.[0-9]+))*(\s[a-zA-Z]+)*', ingredient[1])
                update_add_in_data_set(next_recipe, add_ins, ingredient)
        recipe_objects.append(next_recipe)

    return base_ingredients, add_ins, recipe_objects


def update_add_in_data_set(next_recipe, add_ins, ingredient):
    """
    Here, we are updating our add ins dictionary. We call this method when we come across an add-in in a recipe. This method
    is called if we loop through all the base ingredients in the base_ingredients dictionary and none matched the ingredient
    we are on. We check a few edge cases (happens when the webcrawl isn't perfect) and then update
    the quantity in the dictionary accordingly. If the ingredient isn't yet in the dicionary (we haven't come across it in any 
    recipe yet), then we create a new key for it. For example, if we come across 'oreos' in our recipe for the first time, we call this
    method. Then, it calls _quantity, which is a method of the AddIn class. If our dictionary currently
    has the following -- {"chocolate chips":{"1 cup":2}} -- the method will add a new key reflecting that we have now seen 
    oreos and it will become {"chocolate chips":{"1 cup":2}, "oreos", {"18":1}} (the choice of 18 oreos is of course arbitrary!)

    @params:
        ingredient --> the current ingredient we are on in the recipe
        next_recipe --> the recipe we are looping through
        ingredient --> the add in ingredient we are updating
    """
    quantity = ingredient[1].strip(' ')
    # edge cases
    if 'cornstarch' in ingredient[1]:
        name = 'cornstarch'
    if 'cream cheese' in ingredient[0]:
        name = "cream cheese"
    else:
        name = ingredient[0].replace('*','').replace(',','')

    # if we got a match
    if quantity is not None:
        # edge cases -->when the webcrawl doesn't work perfectly
        if "semi-sweet" in name:
            name = "chocolate chips"
        if "M&M" in name or "chocolate chips" in name or "cream cheese" in name:
            if len(quantity) < 3:
                quantity += " cup"
        elif "cinnamon" in name or "cornstarch" in name:
            if len(quantity) < 3:
                quantity += " teaspoon"
        if "optional:" in name:
            return
        # if we already have this add-in
        if name in add_ins.keys():
            add_ins[name].update_quantity(quantity)
            next_recipe.add_ins[name]=quantity
        else: # create new add-in object
            new_add_in = AddIns(name=name, quantities={})
            new_add_in.update_quantity(quantity)
            add_ins[name] = new_add_in
            next_recipe.add_ins[name]=quantity


def update_base_ingred_data_set(ingredient, next_recipe, base_ingredients, i):
    """
    Here, we are updating our base ingredient dictionary. We call this method when we come across a base
    ingredient in a recipe. We check a few edge cases (happens when the webcrawl isn't perfect) and then update
    the quantity in the dictionary accordingly. For example, if we come across '2 eggs' in our recipe, we call this
    method. Then, it calls update_quantity, which is a method of the BaseIngredient class. If our dictionary currently
    has the following for egg -- {"egg":{1:2}} -- the method will add a new key reflecting that we have now seen 
    a quantity of two eggs and it will become {"egg":{1:2, 2:1}}

    @params:
        ingredient --> the current ingredient we are on in the recipe
        next_recipe --> the recipe we are looping through
        base_ingredients --> our overall base ingredient dictionary
        i --> the base ingredient we are updating
    """
    # match the ingredient quantity
    # the following regex can be used to match the name of the ingredient from the webcrawl. Uncomment out if naming errors arise
    #q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]+(.[0-9]+))*(\s[a-zA-Z]+)*', ingredient[1])
    quantity = ingredient[1].strip(' ')
    if quantity is not None: #if we correctly got the ingredient
        #quantity = q.group() --> Uncomment out with line 263
        # edge cases
        if 'flour' in i or 'brown' in i:
            if 'cup' not in quantity:
                quantity += " cup"
        if 'egg' in quantity:
            quantity = quantity.replace('egg','')
        if 'all' in quantity:
            quantity = quantity.replace('all', 'cup')
        if 'salt' in i:
            if 'cup' in quantity:
                quantity = quantity.replace('cup', 'teaspoon')
        # update ingredient quantity
        base_ingredients[i].update_quantity(quantity)
        next_recipe.base_ingredients[i]=quantity
    return True


def write_to_file(recipe):
    """
    Write recipe to a file, including instructions.

    @params:
        recipe --> recipe object
    """
    name = recipe.name.split()
    str_name = ""
    for word in name:
        str_name += (word.lower() + "_")
        
    with open("recipes/" + str_name[:-1] + ".txt", 'w') as new_recipe:
        egg_quantity = 0
        new_recipe.write(recipe.name + "\n")
        for key, value in recipe.base_ingredients.items():
            new_recipe.write(str(value) + " " + key + "\n")
            if key == "egg":
                egg_quantity = int(recipe.base_ingredients[key])
        for key, value in recipe.add_ins.items():
            new_recipe.write(str(value) + " " + key + "\n")

        new_recipe.write("\nInstructions:\n")
        new_recipe.write("1. Preheat your oven to 350 degrees Fahrenheit and line baking sheets with parchment paper.\n")
        new_recipe.write("2. Whisk the dry ingredients together in a large bowl.\n")

        if egg_quantity > 1:
            egg_string = str(egg_quantity) + " eggs "
        else:
            egg_string = "1 egg "

        new_recipe.write("3. In a separate bowl, cream the butter and both sugars together until smooth. Add " + egg_string + "and the rest of the wet ingredients.\n")
        new_recipe.write("4. Add your wet ingredients to the dry ingredients until combined.\n")
        # string that will store the different add ins, formatted nicely
        add_ins_string = "" 
        last_add_in_string = ""
        last_add_in = ""
        for add_in in recipe.add_ins.keys():
            add_ins_string += add_in + ", "
            last_add_in = add_in
            last_add_in_string = add_in + ", "
        add_ins_s = add_ins_string[:len(add_ins_string)-len(last_add_in_string)]
        if last_add_in != "":
            add_ins_s += "and " + last_add_in
            new_recipe.write("5. Add the " + add_ins_s + " and mix until all combined, and a dough forms.\n")
        else:
            new_recipe.write("5. Make sure you mix until a dough forms.\n")
        new_recipe.write("6. Roll the cookie dough into medium-sized scoops and place 3 inches apart on the baking sheet.\n")
        min_time = random.randint(7,10)
        max_time = random.randint(10, 15)
        new_recipe.write("7. Bake for " + str(min_time) + "-" + str(max_time) + " minutes or until edges appear set.\n")
        new_recipe.write("8. Remove from the oven and allow to cool on the baking sheet for 5 minutes then transfer to a wire rack to cool.\n")
        new_recipe.write("9. Enjoy!\n")
    new_recipe.close()


def create_recipe_name(add_ins): 
    """
    Creates a name for the recipe by including two different add-in ingredients to the name.

    @params:
        add-ins --> add ins for the new recipe

    @returns:
        name --> the name for our new recipe!
    """
    # if we have more than 1 add in ingredients to add
    if len(add_ins) > 1:
        int1 = 0
        int2 = 0
        # we want unique indices for add-ins (unique add-ins), so loop until we have different numbers
        while int1 == int2: 
            int1 = random.randint(0, len(add_ins) - 1)
            int2 = random.randint(0, len(add_ins) - 1)
            # if random picked the same, try again!
            if int1 == int2: 
                int2 = random.randint(0, max(int1,int2))
            #grab name attribute of the index of the addin from our master list
            name1 = list(add_ins.keys())[int1] 
            name2 = list(add_ins.keys())[int2]
            # we dont want these to be part of the name....gross......
            if name1 == 'cornstarch' or name1 == 'cream of tartar':
                int1 = int2
            if name2 == 'cornstarch' or name2 == 'cream of tartar':
                int2 = int1

        name = name1.title() + " " + name2.title() + " Cookies"
    # 0 or 1 add-ins
    else:
        adjectives = ["Delicious", "Yummy", "Special", "World's Best", "Wonderful", "Mouth-Watering"]
        adj = adjectives[random.randint(0,len(adjectives)-1)]
        # if we have a single add-in
        if len(add_ins) == 1: 
            name = adj + list(add_ins.keys())[0] + " Cookies"
        else:
            name = adj + " Cookies"

    return name


def pick_mutation(new_recipe):
    """
    Decide what mutation to make
    @params:
        new_recipe --> the recipe object we are mutating

    @returns:
        new_ingredient --> the new ingredient we added/replaced

    """
    random_num = random.randint(0,100)
    new_ingredient = None
    if random_num < 80:
        new_ingredient = new_recipe.add_ingredient()
    elif random_num < 60:
        new_ingredient = new_recipe.replace_ingredient()
    return new_ingredient


def print_info(base_ingredients, add_ins, recipe_objects):
    """
    This method prints all the info related to our overall data sets. Can be called before or after generating
    new recipes. With each new recipe, we add it to the recipe_objects list. We also update the base ingredients
    dictionary with the new recipe's base ingredients quantities and the add in dictionary with the add in quantities.

    @params:
        base_ingredients --> dictionary mapping the string of the base ingredient to a dictionary mapping the quantity of 
        that ingredient to the # of times it occurs
        add_ins --> dictionary mapping the string of the add in to a dictionary mapping the quantity of 
        that ingredient to the # of times it occurs
        recipe_objects --> list of recipe objects, with base ingredients and add ins as attributes
    """
    #print base ingredients and their quantities one at a time
    print("\nNow printing all of our base ingredients and their quantities:\n")
    for value in base_ingredients.values():
        print("Base Ingredient:", value.name)
        print("Quantities:", value.quantities,"\n")
    #print add ins and their quantities one at a time
    print("\nNow printing add-ins and their quantities:\n")
    for value in add_ins.values():
        print("Add in:", value.name)
        print("Quantities: ", value.quantities, "\n")
    #print ingredients from each recipe object
    print("\nNow printing inspiring set recipes and their ingredients:\n")
    for recipe in recipe_objects:
        print(recipe.name)
        for ingredient, quantity in recipe.base_ingredients.items():
            print(quantity, ingredient)
        for ingredient, quantity in recipe.add_ins.items():
            print(quantity, ingredient)
        print("\n")


def generate_recipes(num_recipes, base_ingredients, add_ins, recipe_objects):
    """
    Generate the desired number of new recipes, and prints the best one based on our fitness function.

    @params:
        num_recipes --> number of recipes we would like to generate
        base_ingredients --> dictionary of base ingredients and their quantities
        add_ins --> dictionary of add ins and their quantities
        recioe_objects --> list of recipe objects
    """
    new_recipe_objects = [] #store our new recipe objects
    # loop to generate cookies
    for i in range(num_recipes):
        new_recipe = build_new_recipe(base_ingredients, add_ins, recipe_objects)
        #print(new_recipe.add_ins, new_recipe.base_ingredients)
        recipe_objects.append(new_recipe)
        new_recipe_objects.append(new_recipe)
        new_ingredient = pick_mutation(new_recipe)
        if new_ingredient is not None:
            # if we havent already created a add in object for this
            if new_ingredient not in add_ins.keys(): 
                #create new add_in object for this 
                new_add_in = AddIns(name=new_ingredient, quantities={})  
                new_add_in.update_quantity(new_recipe.add_ins[new_ingredient])
                add_ins[new_ingredient] = new_add_in
            else:
                add_ins[new_ingredient].update_quantity(new_recipe.add_ins[new_ingredient])
        new_recipe.fitness_function()
        write_to_file(new_recipe)

    new_recipes_sorted = sorted(new_recipe_objects, key=attrgetter("fitness"),reverse=True)
    print("\nNow printing all of the newly generated recipes and their fitness. Check the recipes folder to see text files of each one containing ingredients and instructions!")
    for i in new_recipes_sorted:
        print("\n", i.name)
        print("Fitness of the recipe:", round(i.fitness,2))
    #print the best recipe from all the ones generated
    print("\nBest recipe from this iteration:", new_recipes_sorted[0].name)    

def get_user_info():
    """
    Prints a welcome message and asks how many recipes the user would like to generate in the current generation. Also asks user if they want information about the
    inspiring set printed
    """

    print("Welcome to GECCO--Genetically Exploring Creative Cookie Options! \nRunning this program will output unique cookie recipes based on", \
    "recipes from Sally's Baking Addiction! The program will create a number of recipes and then compute the fitness (how good the recipe is)", \
    "of each one.")
    num_recipes = input("How many recipes would you like to generate? Please enter a number:\n")
    try:
        num_recipes = int(num_recipes.strip())
        print_info = input("\nWould you like to print information about all of the base ingredients, add ins, and inspiring set recipes?\nEnter 'yes' or 'no' below:\n")
        if print_info == 'yes':
            print_info = True
        else:
            print_info = False
        return num_recipes, print_info
    except:
        print("Please enter one number. Try again!")
        get_user_info()


def main():
    # get information from user
    num_recipes, print_recipe_info = get_user_info()
    print("Checking to see if inspiring set json already exists")
    # check to see if our data set is already hard-coded
    try:
        # if we already did the webcrawl in a previous run of the program, we don't need to do it again! This saves lots of time
        if os.path.getsize('recipes.json') > 0:
            print("File already exists!")
            with open('recipes.json') as json_file: 
                recipes = json.load(json_file)
    except:
        # if we do not have the json for the webcrawl, run the webcrawl script to scrape the following webpages
        print("json file is empty or does not exist")
        # this is the list of recipes we are crawling. Can be changed to suit the user--any recipe from sally's baking addiction should work!
        recipes = get_cookie_recipes(['https://sallysbakingaddiction.com/caramel-surprise-snickerdoodles/','https://sallysbakingaddiction.com/death-by-chocolate-peanut-butter-chip-cookies/',\
            'https://sallysbakingaddiction.com/sweet-salty-potato-chip-toffee-cookies-2/','https://sallysbakingaddiction.com/smores-chocolate-chip-cookies/',\
            'https://sallysbakingaddiction.com/biscoff-white-chocolate-oatmeal-cookies/#tasty-recipes-76093', 'https://sallysbakingaddiction.com/white-chocolate-cranberry-pistachio-cookies/', \
            'https://sallysbakingaddiction.com/peanut-butter-cookies/', 'https://sallysbakingaddiction.com/soft-chewy-oatmeal-raisin-cookies/', 'https://sallysbakingaddiction.com/pumpkin-chocolate-chip-cookies/', \
            'https://sallysbakingaddiction.com/crispy-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/bunny-sugar-cookies/','https://sallysbakingaddiction.com/dark-chocolate-cranberry-almond-cookies/', \
            'https://sallysbakingaddiction.com/zucchini-oatmeal-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/cookies-n-cream-cookies/', 'https://sallysbakingaddiction.com/oreo-cheesecake-cookies/', \
            'https://sallysbakingaddiction.com/chewy-oatmeal-mm-cookies/', 'https://sallysbakingaddiction.com/white-chocolate-chai-snickerdoodles/'])

    # generate our inspiring set
    base_ingredients, add_ins, recipe_objects = get_inspiring_set(recipes)
    #print all the info if specified
    if print_recipe_info:
        print_info(base_ingredients, add_ins, recipe_objects)
    # loop through recipe objects and write to file
    for recipe in recipe_objects:
        write_to_file(recipe)
        recipe.fitness_function()

    generate_recipes(num_recipes, base_ingredients, add_ins, recipe_objects)


"""
Driver for the entire program
"""
if __name__ == "__main__":
    main()


