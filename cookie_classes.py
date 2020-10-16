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
from webcrawl import get_cookie_recipes


class BaseIngredient(object):
    """
    Attributes:
        name --> str of the name
        quantities --> dictionary where keys are the quantity and value is the number of times that quantity is seen across all recipes.
        For instance, if self.name = "butter and self.quantities = {"1 cup": 5, "0.5 cup": 6}, this indicates that butter
        is found in 11 recipes, 5 times with 1 cup and 6 times with 0.5 cup
    """

    def __init__(self, name, quantities):
        self.name = name
        self.quantities = quantities

    def __str__(self):
        """
        Returns a string representation of this BaseIngredient.
        """
        return self.name

    def get_quantity(self):
        """
        Returns a quantity that should correspond with a certain ingredient.
        Chosen probabilistically based on the number of times this quantity appears in the inspiring set of recipes.
        
        @params:
            quantities --> the dictionary holding certain quantities of an ingredient mapped to the number of times this quantity of the ingredient is present
        @returns:
            returns the quantity
        """
        new_quantity = 0
        for key in self.quantities.keys():
            # the quantity will be assigned to this variable
            new_quantity = key 
            break

        sum_quantity = 0 
        for q in self.quantities:
            sum_quantity += self.quantities[q]
        # random integer between 0 and the total sum
        num = random.randint(0,sum_quantity) 

        sum = 0 
        for q in self.quantities:
            if num < self.quantities[q] + sum: 
                new_quantity = q 
                break
            else:
                sum += self.quantities[q]

        return new_quantity
    
    def update_quantity(self, quantity):
        """
        Given the quantity of an ingredient, updates the quantities dictionary to maintain a count of the quantity's appearance in the inspiring set
    
        @params:
            quantity --> the quantity whose value in the quantities dict we need to update
        """
        if quantity in self.quantities:
            self.quantities[quantity]+=1
        else:
            self.quantities.setdefault(quantity, 1)


class AddIns(object):
    """
    Add in objects are a single add-in used in recipes

    Attributes:
        name --> str of the name
        quantities --> dictionary where keys are the quantity and values are the number of times that quantity occurs across all recipes.
        For instance, if self.name = "chocolate" and self.quantities= {"1 cup": 3, "2 cups": 2}, this indicates that chocolate
        is found in 5 recipes, 3 times with 1 cup and twice with 2 cups
    """
    def __init__(self, name, quantities):
        self.name = name
        self.quantities = quantities

    def __str__(self):
        """
        Returns a string representation of this AddIn.
        """
        return self.name

    def get_quantity(self):
        """
        Returns a quantity that should correspond with a certain ingredient.
        Chosen probabilistically based on the number of times this quantity appears in the inspiring set of recipes.
        
        @returns:
            returns the quantity
        """
        new_quantity = 0
        for key in self.quantities.keys():
            # the quantity will be assigned to this variable
            new_quantity = key 
            break

        sum_quantity = 0 
        for q in self.quantities:
            sum_quantity += self.quantities[q]
        # random integer between 0 and the total sum
        num = random.randint(0,sum_quantity) 

        sum = 0 
        for q in self.quantities:
            if num < self.quantities[q] + sum: 
                new_quantity = q 
                break
            else:
                sum += self.quantities[q]

        return new_quantity

    def update_quantity(self, quantity):
        """
        Given the quantity of an ingredient, updates the quantities dictionary to maintain a count of the quantity's appearance in the inspiring set
        
        @params:
            quantity --> the quantity whose value in the quantities dict we need to update
        """
        if quantity in self.quantities:
            self.quantities[quantity]+=1
        else:
            self.quantities.setdefault(quantity, 1)


class Recipe(object):
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

    def __str__(self):
        """
        Returns a string representation of this Recipe.
        """
        return self.name

    def fitness_function(self):
        """
        Returns the fitness of our recipe, based on the similarity between our ingredients

        We have the best_fit data structure to account for names of add ins that are unusual, and are not in the data base. In this case, we pair
        the ingredient to something close to it. In some cases, the ingredient is weird (like cornstarch) and so we ignore those cases

        To calculate fitness, we first use combinations to get all the combinations of two add-ins. Then, we compute the similarity between them, if possible,
        and add it to the total fitness. If it's not possible, we subtract 1 from the total number of combinations and add 0 to total fitness.
        Then, we divide total fitness by the number of combinations we were able to calculate the similarity of. This becomes our fitness.

        NOTE: If a recipe has no add-ins, the fitness is automatically 0 (since there's nothing to compare). This makes sense since a cookie with only our
        base ingredients is boring!

        @returns:
            total --> the total fitness for the recipe
        """
        # initialize total
        total = 0 
        # total number of combinations of two add-ins
        total_num = len(list(combinations(self.add_ins, 2))) 
        for combination in combinations(self.add_ins, 2):
            # try to find similarity
            try: 
                # if it's in our best fit dictionary, take the value instead of the real name
                if combination[0] in self.best_fit: 
                    ingredient1 = self.best_fit[combination[0]]
                else:
                    ingredient1 = combination[0]
                #if ingredient 2 is in our best fit dictionary
                if combination[1] in self.best_fit: 
                    ingredient2 = self.best_fit[combination[1]]
                else:
                    ingredient2 = combination[1]
                # compute similarity and add similarity to total 
                total += fp.similarity(ingredient1, ingredient2) 
            # we didn't find the ingredient in our database
            except KeyError: 
                #print("Whoops! key error: ", ingredient1, " or " , ingredient2, " was not found in database")
                #subtract 1 from total num combinations
                total_num -= 1 
        #if we found some similarities
        if total_num > 0: 
            total = (total / total_num) * 100
        else:
            total = 0
        self.fitness = total

    def add_ingredient(self):
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
        # initialize dictionary that stores pairings
        ingredient_pairings = {} 
        #for each add in in the new recipe
        for add_in in self.add_ins.keys(): 
            # this is an add-in object
            add_in_amount = self.add_ins[add_in] 
            # try to find similarity
            try: 
                ingredient = add_in 
                 #If it's in the best fit dictionary, use the best fit name, otherwise use origional name
                if add_in in self.best_fit:
                    ingredient = self.best_fit[add_in]
                #Finds ingredients that pair well with each add in 
                pairs = fp.pairing(ingredient, .55) 
                #Add each ingredient from the pairings to ingredient_pairings dictionary. 
                for key in pairs.keys(): 
                    #The quantity of pairings remains the same as the AddIn it was paired from
                    ingredient_pairings[key] = add_in_amount 
            # we didn't find the ingredient in our database
            except KeyError: 
                pass
                #print("Whoops! key error: ", ingredient, " was not found in database")
        dict_keys = list(ingredient_pairings.keys()) 
        if len(dict_keys) > 1:
            rand_index = random.randint(0, len(dict_keys) - 1)
            #Choose a random ingredient from the ingredients that pair well with existing add ins
            rand_key = dict_keys[rand_index] 
            # update the add_ins for this recipe and corresponding quantity
            self.add_ins[rand_key] = ingredient_pairings[rand_key] 
            #return the new ingredient to be added
            return rand_key  
        else:
            return None

    def replace_ingredient(self):
        """
        Here we are trying to replace a random ingredient with an ingredient that pairs well with another ingredient in the recipe

        @params:
            add_ins --> list of add in objects
        @returns:
            the new add_in, as an object
        """
        # index to delete
        rand_int = random.randint(0, len(self.add_ins) - 1) 
        #index of what to pair new flavor with
        rand_int2 = random.randint(0, len(self.add_ins)-1) 
        # try calling pairing function
        try: 
            amount = self.add_ins[list(self.add_ins.keys())[rand_int2]]
            # if its in best fit dictionary
            if self.add_ins.keys()[rand_int2] in self.best_fit.keys(): 
                # set ingredient to best fit
                ingredient = self.best_fit[list(self.add_ins.keys())[rand_int2]] 
            else:
                # else set ingredient accordingly
                ingredient = list(self.add_ins.keys())[rand_int2] 
            new_ingredients = fp.pairing(ingredient, 0.4)
        except KeyError:
            #print("couldnt pair ingredient")
            return
        # if we found an ingredient, add it to recipe
        if len(new_ingredients) > 1: 
            rand_item = random.randint(0, len(new_ingredients)-1)
            # Need to determine what quantity to put
            new_ingredient = AddIns(list(new_ingredients.keys())[rand_item], {amount:1}) 
            key_to_replace = list(self.add_ins.keys())[rand_int]
            del self.add_ins[key_to_replace]
            self.add_ins[new_ingredient.name] = amount
        else:
            return
        return new_ingredient








        




