import selenium
import numpy
import random
import re

from webscrape import getCookieRecipes

class BaseIngredient(object):
    def __init__(self, name, quantities):
        self.name = name
        self.quantities = quantities
    
    """
    Returns a quantity that should correspond with a certain ingredient.
    Chosen probabilistically based on the number of times this quantity appears in the inspiring set of recipes.
        
    @params:
        quantities --> the dictionary holding certain quantities of an ingredient mapped to the number of times this quantity of the ingredient is present
    @returns:
        returns the quantity
    """
    def getQuantity(self):
        new_quantity = 0 # the quantity will be assigned to this variable

        sum_quantity = 0 
        for q in self.quantities:
            sum_quantity += self.quantities[q]
        num = random.randint(0,sum_quantity) # random integer between 0 and the total sum

        sum = 0 
        for q in self.quantities:
            if num < self.quantities[q] + sum: 
                new_quantity = q 
                break
            else:
                sum += self.quantities[q]

        return new_quantity
    
    """
    Given the quantity of an ingredient, updates the quantities dictionary to maintain a count of the quantity's appearance in the inspiring set
    
    
    """
    def updateQuantity(self, quantity):
        if quantity in self.quantities:
            self.quantities[quantity]+=1
        else:
            self.quantities.setdefault(quantity, 1)




class AddIns(object):
    def __init__(self, name, quantities):
        self.name = name
        self.quantities = quantities

    """
    Given the quantity of an ingredient, updates the quantities dictionary to maintain a count of the quantity's appearance in the inspiring set
    
    
    """
    def updateQuantity(self, quantity):
        if quantity in self.quantities:
            self.quantities[quantity]+=1
        else:
            self.quantities.setdefault(quantity, 1)


class Recipe(object):
    def __init__(self, name, base_ingredients, add_ins):
        self.name = name
        self.base_ingredients = base_ingredients
        self.add_ins = add_ins

    

# WHERE TO GO...

"""

"""
def buildNewRecipe(base_ingredients, mix_ins):
    ingredients = {}

    for i in base_ingredients:
        ingredients.update({i.name,i.getQuantity()})

    #adding in mix-ins ???? discuss later
 
    return ingredients


"""
"""
def inspiringSet():
    recipes = getCookieRecipes(['https://sallysbakingaddiction.com/pumpkin-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/peanut-butter-cookies/', 'https://sallysbakingaddiction.com/soft-chewy-oatmeal-raisin-cookies/', \
    'https://sallysbakingaddiction.com/crispy-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/soft-molasses-cookies/','https://sallysbakingaddiction.com/dark-chocolate-cranberry-almond-cookies/', \
        'https://sallysbakingaddiction.com/zucchini-oatmeal-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/cookies-n-cream-cookies/'])



    #need to extract the quantities dictionary for each 

    # BASE INGREDIENTS #
    base_ingredients = {}
    add_ins = {}
    base_ingredients["flour"] = BaseIngredient(name="flour",quantities={})
    base_ingredients["egg"] = BaseIngredient(name="egg", quantities={})
    base_ingredients["granulated sugar"] = BaseIngredient(name="granulated sugar", quantities={})
    base_ingredients["brown sugar"] = BaseIngredient(name="brown sugar", quantities={})
    base_ingredients["butter"] = BaseIngredient(name="butter", quantities={})
    base_ingredients["salt"] = BaseIngredient(name="salt", quantities={})
    base_ingredients["all-purpose flout"] = BaseIngredient(name="all-purpose flour", quantities={})
    base_ingredients["baking soda"] = BaseIngredient(name="baking soda", quantities={})
    base_ingredients["baking powder"] = BaseIngredient(name="baking powder", quantities={})

    # update quantities dictionary for each of the base ingredients
    for recipe in recipes:
        for ingredient in recipes[recipe]:
            for i in base_ingredients.keys():
                done = False
                if i in ingredient:
                    q = re.search(r'^[0-9]+(\/[0-9]+)*(\sand\s)*([0-9]+(\/[0-9]+))*\s[a-zA-Z]+', ingredient)
                    if q is not None:
                        quantity = q.group()
                        base_ingredients[i].updateQuantity(quantity)
                        done = True
                        break
            if not done:
                if ingredient in add_ins.keys():
                    q = re.search(r'^[0-9]+(\/[0-9]+)*(\sand\s)*([0-9]+(\/[0-9]+))*\s[a-zA-Z]+', ingredient)
                    if q is not None:
                        quantity = q.group()
                        add_ins[ingredient].updateQuantity(quantity)
                    else:
                        new_add_in = AddIns(name=ingredient, quantities={})
                        new_add_in.updateQuantity(quantity)
                        add_ins[ingredient] = new_add_in

    for value in base_ingredients.values():
        print(value.name)
        print(value.quantities)

    for value in add_ins.values():
        print(value.name)
        print(value.quantities)

    


"""

"""
def processRecipes():
    recipes = getCookieRecipes('https://sallysbakingaddiction.com/category/desserts/cookies/')

    #need to extract the quantities dictionary for each 

inspiringSet()


