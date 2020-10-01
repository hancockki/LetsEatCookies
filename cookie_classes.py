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


class Recipe(object):
    def __init__(self, name, base_ingredients, add_ins):
        self.name = name
        self.base_ingredients = base_ingredients
        self.add_ins = add_ins
