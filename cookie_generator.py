import selenium
import numpy
import random

from driver import getCookieRecipes

"""
Attributes:
    name --> the name of the ingredient

"""
class BaseIngredients(object):
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

        sum_quantity = 0 # the total quantity across the dictionary
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

    """
    def updateQuantity(self, quantity):
        self.quantities[quantity]+=1





class AddIns(object):
    def __init__(self, name, quantities):
        self.name = name
        self.quantities = quantities


class Recipe(object):
    def __init__(self, name, ingredients):
        self.name = name
        self.ingredients = ingredients

    

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
def processRecipes():
    recipes = getCookieRecipes('https://sallysbakingaddiction.com/category/desserts/cookies/')

    #need to distinguish the base ingredients from mix-ins
    


