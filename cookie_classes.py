"""
Authors: Kim H, Kayla S, Lydia P
CSCI 3725 - Computational Creativity
Party Quest 2: Smart Cookies
Last Modified: Oct 16, 2020

The purpose of this program is to use cookie recipes from the internet to generate new recipes 
with creative ingredients! We are using recipes from Sally's Baking as the recipes on this site
are really fun and lots of them have unique add-ins that we can use! We hace named our system
GECCO - Genetically Exploring Creative Cookie Options.

This file holds all of our classes used to organize and build cookie recipes, as well as the 
appropriate functions. It is also includes fuctions for the genetic aspect of our code -- such
as the fitness function and mutation fuctions. This file is utilized in generate_cookies.py
"""

import numpy
import random
import re
import flavorpairing as fp
from itertools import combinations
from webcrawl import getCookieRecipes


"""
Attributes:
    name --> str of the name
    quantities --> dictionary where keys are the quantity and value is the number of times that quantity is seen across all recipes.
    For instance, if self.name = "butter and self.quantities = {"1 cup": 5, "0.5 cup": 6}, this indicates that butter
    is found in 11 recipes, 5 times with 1 cup and 6 times with 0.5 cup

"""
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
        new_quantity = 0
        for key in self.quantities.keys():
            new_quantity = key # the quantity will be assigned to this variable
            break

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
    
    @params:
        quantity --> the quantity whose value in the quantities dict we need to update
    """
    def updateQuantity(self, quantity):
        if quantity in self.quantities:
            self.quantities[quantity]+=1
        else:
            self.quantities.setdefault(quantity, 1)


"""
Add in objects are a single add-in used in recipes

Attributes:
    name --> str of the name
    quantities --> dictionary where keys are the quantity and values are the number of times that quantity occurs across all recipes.
    For instance, if self.name = "chocolate" and self.quantities= {"1 cup": 3, "2 cups": 2}, this indicates that chocolate
    is found in 5 recipes, 3 times with 1 cup and twice with 2 cups

"""
class AddIns(object):
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
        new_quantity = 0
        for key in self.quantities.keys():
            new_quantity = key # the quantity will be assigned to this variable
            break

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

"""
The recipe class creates recipe Objects, which we add to our list of recipes as we create them in generate_cookies.py

Attributes:
    name --> name of the recipe, str
    base_ingredients --> dictionary mapping name of base ingredient to quantity
    add_ins --> dictionary mapping add in to quantity
    best_fit --> dictionary used for flavor pairing. IF the ingredient does not exist in the flavor pairing database, use an 
    ingredient that is similar to it
    fitness --> fitness of the recipe, based off of flavor similarities across add-ins
"""
class Recipe(object):
    def __init__(self, name, base_ingredients, add_ins):
        self.name = name
        self.base_ingredients = base_ingredients
        self.add_ins = add_ins
        self.best_fit = {"M&Ms": "chocolate", "pumpkin puree": "pumpkin", "molasses": "honey", "white chocolate morsels": "chocolate", "dried cranberries": "cranberry", \
            "almond extract": "almond", "semi-sweet chocolate": "chocolate", "pistachios":"pistachio", "chocolate chips": "chocolate", "Biscoff spread": "cinnamon", \
                "pumpkin pie spice": "allspice", "bittersweet chocolate":"chocolate", "raisins":"raisin", "pure maple syrup":"honey", "semi-sweet chocolate chips":"chocolate", \
                "white chocolate chips":"chocolate", "ground ginger":"ginger","ground cardamom":"cardamom", "Oreos":"chocolate", "chopped Oreos":"chocolate", \
                "heath bars":"hazelnut", "graham cracker crumbs":"cocoa", 'almonds':'almond', "pure vanilla extract":'vanilla', "ground cinnamon":'cinnamon', "ground allspice":"allspice"}
        self.fitness = 0

    """
    Returns the fitness of our recipe, based on the similarity between our ingredients

    We have the best_fit data structure to account for names of add ins that are unusual, and are not in the data base. In this case, we pair
    the ingredient to something close to it. In some cases, the ingredient is weird (like cornstarch) and so we ignore those cases

    To calculate fitness, we first use combinations to get all the combinations of two add-ins. Then, we compute the similarity between them, if possible,
    and add it to the total fitness. If it's not possible, we subtract 1 from the total number of combinations and add 0 to total fitness.
    Then, we divide total fitness by the number of combinations we were able to calculate the similarity of. This becomes our fitness.

    @returns:
        total --> the total fitness for the recipe
    """
    def fitnessFunction(self):
        # dictionary mapping add in name to 'best fit' name 
    
        total = 0 # initialize total
        total_num = len(list(combinations(self.add_ins, 2))) # total number of combinations of two add-ins
        for combination in combinations(self.add_ins, 2):
            try: # try to find similarity
                if combination[0] in self.best_fit: # if it's in our best fit dictionary, take the value instead of the real name
                    ingredient1 = self.best_fit[combination[0]]
                else:
                    ingredient1 = combination[0]
                if combination[1] in self.best_fit: #if ingredient 2 is in our best fit dictionary
                    ingredient2 = self.best_fit[combination[1]]
                else:
                    ingredient2 = combination[1]
                total += fp.similarity(ingredient1, ingredient2) # compute similarity and add similarity to total 
            except KeyError: # we didn't find the ingredient in our database
                #print("Whoops! key error: ", ingredient1, " or " , ingredient2, " was not found in database")
                total_num -= 1 #subtract 1 from total num conmbinations
        if total_num > 0: #if we found some similarities
            total = (total / total_num) * 100
        else:
            total = 0
        self.fitness = total

    """
    Returns a single AddIn object to be added to a new recipe
    Walks through all of the of the AddIn ingredients of a new recipe, and adds ingredients that pair within .5 of 
    each AddIn ingredient to a dictonary called ingredient_pairings. They keys are new ingredient names from the .npy
    files, and the values are the quantities pulled from the AddIn ingredient it was paired from.
    @params:
        add_in_list --> the dictionary holding names and quantities of AddIn objects of a new recipe
    @returns:
        returns a single AddIn object
    """
    def addIngredient(self):
        # initialize dictionary that stores pairings
        ingredient_pairings = {} 
        for add_in in self.add_ins.keys(): #for each add in in the new recipe
            add_in_amount = self.add_ins[add_in] # this is an add-in object
            try: # try to find similarity
                ingredient = add_in 
                if add_in in self.best_fit: #If it's in the best fit dictionary, use the best fit name, otherwise use origional name
                    ingredient = self.best_fit[add_in] 
                pairs = fp.pairing(ingredient, .55) #Finds ingredients that pair well with each add in
                for key in pairs.keys(): #Add each ingredient from the pairings to ingredient_pairings dictionary. 
                    ingredient_pairings[key] = add_in_amount #The quantity of pairings remains the same as the AddIn it was paired from
            except KeyError: # we didn't find the ingredient in our database
                pass
                #print("Whoops! key error: ", ingredient, " was not found in database")
        dict_keys = list(ingredient_pairings.keys()) 
        if len(dict_keys) > 1:
            rand_index = random.randint(0, len(dict_keys) - 1)
            rand_key = dict_keys[rand_index] #Choose a random ingredient from the ingredients that pair well with existing add ins
            self.add_ins[rand_key] = ingredient_pairings[rand_key] # update the add_ins for this recipe and corresponding quantity
            return rand_key #return the new ingredient to be added 
        else:
            return None


    """
    Here we are trying to replace a random ingredient with an ingredient that pairs well with another ingredient in the recipe

    @params:
        add_ins --> list of add in objects
    @returns:
        the new add_in, as an object

    """
    def replaceIngredient(self):
        rand_int = random.randint(0, len(self.add_ins) - 1) # index to delete
        rand_int2 = random.randint(0, len(self.add_ins)-1) #index of what to pair new flavor with
        try: # try calling pairing function
            amount = self.add_ins[list(self.add_ins.keys())[rand_int2]]
            if self.add_ins.keys()[rand_int2] in self.best_fit.keys(): # if its in best fit dictionary
                ingredient = self.best_fit[list(self.add_ins.keys())[rand_int2]] # set ingredient to best fit
            else:
                ingredient = list(self.add_ins.keys())[rand_int2] # else set ingredient accordingly
            new_ingredients = fp.pairing(ingredient, 0.4)
        except KeyError:
            #print("couldnt pair ingredient")
            return
        if len(new_ingredients) > 1: # if we found an ingredient, add it to recipe
            rand_item = random.randint(0, len(new_ingredients)-1)
            new_ingredient = AddIns(list(new_ingredients.keys())[rand_item], {amount:1}) # Need to determine what quantity to put
            key_to_replace = list(self.add_ins.keys())[rand_int]
            del self.add_ins[key_to_replace]
            self.add_ins[new_ingredient.name] = amount
        else:
            return
        return new_ingredient








        




