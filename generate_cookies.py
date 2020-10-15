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
This method builds a new cookie recipe based on our base_ingredient, add_ins, and recipe_objects. It first picks two recipes probabilistically based
on their fitness (higher fitness=higher chance of being picked), then picks add-ins from these based on the flavor pairings between the recipes.

@params:
    base_ingredients --> dictionary mapping the name of the ingredinet (as a string) to the BaseIngredient object
    add_ins --> dictionary mapping the name of the add-in (as a string) to the addIn object
    recipe_objects --> list of Recipe objects made so far

@returns:
    new_recipe --> the new recipe object we've made
"""
def buildNewRecipe(base_ingredients, add_ins, recipe_objects):
    base_ingredients_new_recipe = {}

    # include one of every base ingredient, picking the quantities probabilistically from those in inspiring set
    for i in base_ingredients.values():
        base_ingredients_new_recipe[i.name]=i.getQuantity()
    
    # here, we get the fitness of each recipe and add to list, which we will use to pick the recipes
    weights = []
    for i in recipe_objects:
        weights.append(i.fitness)
    
    #pick two recipes with probability proportional to fitness
    choices = random.choices(recipe_objects, weights, k=2)
    add_ins_recipe_1 = choices[0].add_ins
    add_ins_recipe_2 = choices[1].add_ins
    best_fit = choices[0].best_fit

    add_ins_new_recipe = getAddInsNewRecipe(add_ins_recipe_1, add_ins_recipe_2, add_ins, best_fit)

    # pick a name for our new recipe
    name = getName(add_ins_new_recipe)
    new_recipe = Recipe(name=name, base_ingredients=base_ingredients_new_recipe, add_ins=add_ins_new_recipe)

    # TODO::: CALL MUTATION FUNCTIONS with random probability
 
    return new_recipe

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
def getAddInsNewRecipe(add_ins_recipe_1, add_ins_recipe_2, add_ins, best_fit):
    #this is the list of all possible pairs of add-ins from our best two recipes
    #product is a method that returns all the pairs
    output = list(product(add_ins_recipe_1.keys(), add_ins_recipe_2.keys()))
    
    #initialize ingredient pairs list and similarities list. Used later in the code to pick our add ins
    ingredient_pairs = []
    similarities = []
    # loop through the add-ins in our best two recipes
    already_checked = [] # we make this so we don't compute the exact same tuple twice (the thought here is that multiple
    #add-ins are the same best fit)
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
                #print("whoops! key error: ", ingredient1, " and ", ingredient2, " were not able to be compared")
                ingredient_pairs.append(combination)
                similarities.append(0.2) # set to low probability
                continue
            ingredient_pairs.append(combination)
            similarities.append(similarity)

    #pick random number of add-ins based on probability. Probability determined by similarities
    num_add_ins = random.randint(0, len(ingredient_pairs)-1) # get number of add-ins
    new_add_ins = random.choices(ingredient_pairs, similarities, k=num_add_ins) # ingredients we are addings 

    add_ins_new_recipe = {} # initialize dictionary for new add ins 

    # loop through new ingredients list
    for ingredient in new_add_ins:
        if ingredient[0] not in add_ins_new_recipe.keys(): # if we haven't added the ingredient already
            quantity = add_ins[ingredient[0]].getQuantity() # get a quantity
            add_ins_new_recipe[ingredient[0]] = quantity
            add_ins[ingredient[0]].updateQuantity(quantity)
        if ingredient[1] not in add_ins_new_recipe.keys():
            quantity = add_ins[ingredient[1]].getQuantity()
            add_ins_new_recipe[ingredient[1]] = add_ins[ingredient[1]].getQuantity()
            add_ins[ingredient[1]].updateQuantity(quantity)

    return add_ins_new_recipe

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
            gotBase = False
            for i in base_ingredients.keys():
                #if i in ingredient[0]:
                #print(SequenceMatcher(None, i, ingredient[0]).ratio())
                if SequenceMatcher(None, i, ingredient[0]).ratio() > 0.8 or i in ingredient[0]:
                    gotBase = updateBaseIngredDataSet(ingredient, next_recipe, base_ingredients, i)
            # this means it is an add-in
            if not gotBase:
                #q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]*(.[0-9]+))*(\s[a-zA-Z]+)*', ingredient[1])
                updateAddInDataSet(next_recipe, add_ins, ingredient)
        recipe_objects.append(next_recipe)

    return base_ingredients, add_ins, recipe_objects

"""
Here, we are updating our add ins dictionary. We call this method when we come across an add-in in a recipe. This method
is called if we loop through all the base ingredients in the base_ingredients dictionary and none matched the ingredient
we are on. We check a few edge cases (happens when the webcrawl isn't perfect) and then update
the quantity in the dictionary accordingly. If the ingredient isn't yet in the dicionary (we haven't come across it in any 
recipe yet), then we create a new key for it. For example, if we come across 'oreos' in our recipe for the first time, we call this
method. Then, it calls updateQuantity, which is a method of the AddIn class. If our dictionary currently
has the following -- {"chocolate chips":{"1 cup":2}} -- the method will add a new key reflecting that we have now seen 
oreos and it will become {"chocolate chips":{"1 cup":2}, "oreos", {"18":1}} (the choice of 18 oreos is of course arbitrary!)

@params:
    ingredient --> the current ingredient we are on in the recipe
    next_recipe --> the recipe we are looping through
    ingredient --> the add in ingredient we are updating
"""
def updateAddInDataSet(next_recipe, add_ins, ingredient):
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
        #quantity = q.group()
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
            add_ins[name].updateQuantity(quantity)
            next_recipe.add_ins[name]=quantity
        else: # create new add-in object
            new_add_in = AddIns(name=name, quantities={})
            new_add_in.updateQuantity(quantity)
            add_ins[name] = new_add_in
            next_recipe.add_ins[name]=quantity

"""
Here, we are updating our base ingredient dictionary. We call this method when we come across a base
ingredient in a recipe. We check a few edge cases (happens when the webcrawl isn't perfect) and then update
the quantity in the dictionary accordingly. For example, if we come across '2 eggs' in our recipe, we call this
method. Then, it calls updateQuantity, which is a method of the BaseIngredient class. If our dictionary currently
has the following for egg -- {"egg":{1:2}} -- the method will add a new key reflecting that we have now seen 
a quantity of two eggs and it will become {"egg":{1:2, 2:1}}

@params:
    ingredient --> the current ingredient we are on in the recipe
    next_recipe --> the recipe we are looping through
    base_ingredients --> our overall base ingredient dictionary
    i --> the base ingredient we are updating
"""
def updateBaseIngredDataSet(ingredient, next_recipe, base_ingredients, i):
    # match the ingredient quantity
    #q = re.search(r'^[0-9]+(.[0-9]+)*(\sand\s)*([0-9]+(.[0-9]+))*(\s[a-zA-Z]+)*', ingredient[1])
    quantity = ingredient[1].strip(' ')
    if quantity is not None: #if we got a match
        #quantity = q.group()
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
            # update ingredeint quantity
        base_ingredients[i].updateQuantity(quantity)
        next_recipe.base_ingredients[i]=quantity
        return True

"""
Write recipe to a file

@params:
    recipe --> recipe object
"""
def writeToFile(recipe):
    with open("recipes/" + recipe.name + ".txt", 'w') as new_recipe:
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
        add_ins_string = "" # string that will store the different add ins, formatted nicely
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

"""
Creates a name for the recipe by including two different add-in ingredients to the name.

@params:
    add-ins --> add ins for the new recipe

@returns:
    name --> the name for our new recipe!
"""
def getName(add_ins): 
    # if we have more than 1 add in ingredients to add
    if len(add_ins) > 1:
        int1 = 0
        int2 = 0
        # try to find unique add-ins
        while int1 == int2: # we want unique indeces for add-ins, so loop until we have different numbers
            int1 = random.randint(0, len(add_ins) - 1)
            int2 = random.randint(0, len(add_ins) - 1)
            if int1 == int2: # if random picked the same, try again!
                int2 = random.randint(0, max(int1,int2))
            name1 = list(add_ins.keys())[int1] #grab name attribute of the index of the addin from our master list
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
        if len(add_ins) == 1: # if we have a single add-in
            name = adj + list(add_ins.keys())[0] + " Cookies"
        else:
            name = adj + " Cookies"

    return name

"""
Decide what mutation to make
@params:
    new_recipe --> the recipe object we are mutating

@returns:
    new_ingredient --> the new ingredient we added/replaced

"""
def pickMutation(new_recipe):
    random_num = random.randint(0,100)
    new_ingredient = None
    if random_num < 80:
        new_ingredient = new_recipe.addIngredient()
    elif random_num < 60:
        new_ingredient = new_recipe.replaceIngredient()
    return new_ingredient

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
def printInfo(base_ingredients, add_ins, recipe_objects):
    #print base ingredients and their quantities one at a time
    for value in base_ingredients.values():
        print("Base Ingredient:", value.name)
        print("Quantities:", value.quantities,"\n")
    #print add ins and their quantities one at a time
    for value in add_ins.values():
        print("Add in:", value.name)
        print("Quantities: ", value.quantities, "\n")
    #print ingredients from each recipe object
    for recipe in recipe_objects:
        print(recipe.name)
        for ingredient, quantity in recipe.base_ingredients.items():
            print(quantity, ingredient)
        for ingredient, quantity in recipe.add_ins.items():
            print(quantity, ingredient)
        print("\n")

"""
Generate the desired number of new recipes, and prints the best one based on our fitness function.

@params:
    num_recipes --> number of recipes we would like to generate
    base_ingredients --> dictionary of base ingredients and their quantities
    add_ins --> dictionary of add ins and their quantities
    recioe_objects --> list of recipe objects
"""
def generateRecipes(num_recipes, base_ingredients, add_ins, recipe_objects):
    new_recipe_objects = [] #store our new recipe objects
    # loop to generate cookies
    for i in range(num_recipes):
        new_recipe = buildNewRecipe(base_ingredients, add_ins, recipe_objects)
        #print(new_recipe.add_ins, new_recipe.base_ingredients)
        recipe_objects.append(new_recipe)
        new_recipe_objects.append(new_recipe)
        new_ingredient = pickMutation(new_recipe)
        if new_ingredient is not None:
            if new_ingredient not in add_ins.keys(): # if we havent already created a add in object for this
                new_add_in = AddIns(name=new_ingredient, quantities={})  #create new add_in object for this 
                new_add_in.updateQuantity(new_recipe.add_ins[new_ingredient])
                add_ins[new_ingredient] = new_add_in
            else:
                add_ins[new_ingredient].updateQuantity(new_recipe.add_ins[new_ingredient])
        new_recipe.fitnessFunction()
        writeToFile(new_recipe)

    new_recipes_sorted = sorted(new_recipe_objects, key=attrgetter("fitness"),reverse=True)
    for i in new_recipes_sorted:
        print("\n", i.name)
        print("Fitness of the recipe:", round(i.fitness,2))
    print("\nBest recipe from this iteration:", new_recipes_sorted[0].name)
    

"""
Main method, used to run the program. First, checks to see if our hard-coded json data for the webcrawl exists (since we don't want to
run the webcrawl more than needed as it's slow). If it exists, load the json file into the dictionary format we want.

Then, creates the inspiring set based on the json. The inspiring set method returns our base ingredients, add ins, and recipe objects.

Finally, calls generateRecipes.
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
        recipes = getCookieRecipes(['https://sallysbakingaddiction.com/caramel-surprise-snickerdoodles/','https://sallysbakingaddiction.com/death-by-chocolate-peanut-butter-chip-cookies/','https://sallysbakingaddiction.com/sweet-salty-potato-chip-toffee-cookies-2/','https://sallysbakingaddiction.com/smores-chocolate-chip-cookies/','https://sallysbakingaddiction.com/white-chocolate-chai-snickerdoodles/','https://sallysbakingaddiction.com/biscoff-chocolate-chip-cookies/', \
            'https://sallysbakingaddiction.com/white-chocolate-cranberry-pistachio-cookies/','https://sallysbakingaddiction.com/pumpkin-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/peanut-butter-cookies/', 'https://sallysbakingaddiction.com/soft-chewy-oatmeal-raisin-cookies/', \
        'https://sallysbakingaddiction.com/crispy-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/bunny-sugar-cookies/','https://sallysbakingaddiction.com/dark-chocolate-cranberry-almond-cookies/', \
            'https://sallysbakingaddiction.com/zucchini-oatmeal-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/cookies-n-cream-cookies/', 'https://sallysbakingaddiction.com/oreo-cheesecake-cookies/', \
            'https://sallysbakingaddiction.com/chewy-oatmeal-mm-cookies/'])

    # generate our inspiring set
    base_ingredients, add_ins, recipe_objects = getInspiringSet(recipes)
    printInfo(base_ingredients, add_ins, recipe_objects)
    # loop through recipe objects and write to file
    for recipe in recipe_objects:
        writeToFile(recipe)
        recipe.fitnessFunction()

    generateRecipes(15, base_ingredients, add_ins, recipe_objects)



"""
Driver for the entire program
"""
if __name__ == "__main__":
    main()


