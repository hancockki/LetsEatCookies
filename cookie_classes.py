import selenium
import numpy
import random
import re
import flavorpairing as fp
from itertools import combinations

from webcrawl import getCookieRecipes

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
    
    
    """
    def updateQuantity(self, quantity):
        if quantity in self.quantities:
            self.quantities[quantity]+=1
        else:
            self.quantities.setdefault(quantity, 1)



"""
Attributes:
    name --> str of the name
    quantities --> dictionary where keys are strings of the name of the quantity and value is the ingredients

"""
class AddIns(object):
    def __init__(self, name, quantities):
        self.name = name
        self.quantities = quantities

    """

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


class Recipe(object):
    def __init__(self, name, base_ingredients, add_ins):
        self.name = name
        self.base_ingredients = base_ingredients
        self.add_ins = add_ins
        self.best_fit = {"M&Ms": "chocolate", "pumpkin puree": "pumpkin", "molasses": "honey", "white chocolate morsels": "chocolate", "dried cranberries": "cranberry", \
            "almond extract": "almond", "semi-sweet chocolate": "chocolate", "pistachios":"pistachio", "chocolate chips": "chocolate", "Biscoff spread": "cinnamon", \
                "pumpkin pie spice": "allspice", "bittersweet chocolate":"chocolate", "raisins":"raisin", "pure maple syrup":"honey", "semi-sweet chocolate chips":"chocolate", \
                    "white chocolate chips":"chocolate", "ground ginger":"ginger","ground cardamom":"cardamom", "Oreos":"chocolate"}
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
        print("total num", total_num)
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
                print("similarity", fp.similarity(ingredient1, ingredient2))
                total += fp.similarity(ingredient1, ingredient2) # compute similarity and add similarity to total 
            except KeyError: # we didn't find the ingredient in our database
                print("not found in database", combination[0], combination[1])
                total_num -= 1 #subtract 1 from total num conmbinations
        if total_num > 0: #if we found some similarities
            total = (total / total_num) * 100
        else:
            total = 0
        print("total similarity", total)
        self.fitness = total

    """
    Add an ingredient based on the flavor pairings list.

    @params:
        add_ins_2 --> the list of add-ins 

    @returns:
        new_ingredient --> 
    """ 
    def addRandomIngredient(self, add_ins_2):
        # dictionary mapping add in name to 'best fit' name 
        # randomly select if you mutate first or second list
        add_in_list_num = int1 = random.randint(0, 1)
        add_in_list = add_ins_2
        if add_in_list == 1:
            add_in_list = add_ins_2 #change to 1
        ingredient_pairings = {} 
        for add_in in add_in_list.keys():
            add_in_amount = add_in_list[add_in]   #.quantities
            try: # try to find similarity
                if add_in in self.best_fit: # if it's in our best fit dictionary
                    ingredient = self.best_fit[add_in]
                    #print("Add in: " + add_in + " Ingredient: " + ingredient)
                    pairs = fp.pairing(ingredient, .5)
                    for key in pairs.keys():
                        #print("Keys: " + key)
                        ingredient_pairings[key] = add_in_amount
                        #print(ingredient_pairings)
            except KeyError: # we didn't find the ingredient in our database
                print("not found in database")
        dict_keys = list(ingredient_pairings.keys())
        rand_index = random.randint(0, len(dict_keys) - 1)
        rand_key = dict_keys[rand_index]
        #print(add_in_list[rand_key])
        #print(rand_index)
        #print(rand_key)
        #print(ingredient_pairings[rand_key])
        add_in_list[rand_key] = ingredient_pairings[rand_key]
        #print(add_in_list)
        print(add_in_list[rand_key].name)
        print(add_in_list[rand_key].getQuantity())
        self.add_ins[add_in_list[rand_key].name] = add_in_list[rand_key].getQuantity()
        #return add_in_list[rand_key]

    """
    Here we are trying to replace a random ingredient with an ingredient that pairs well with another ingredient in the recipe

    @params:
        add_ins --> list of add in objects
    @returns:
        the new add_in, as an object

    """
    def replaceIngredient(self, add_ins):
        rand_int = random.randint(0, len(self.add_ins) - 1) # index to delete
        rand_int2 = random.randint(0, len(self.add_ins)-1) #index of what to pair new flavor with
        try: # try calling pairing function
            print(list(self.add_ins.keys())[rand_int2])
            if list(self.add_ins.keys())[rand_int2] in self.best_fit.keys(): # if its in best fit dictionary
                print(list(self.add_ins.keys())[rand_int2])
                ingredient = self.best_fit[list(self.add_ins.keys())[rand_int2]] # set ingredient to best fit
            else:
                ingredient = list(self.add_ins.keys())[rand_int2] # else set ingredient accordingly
            new_ingredients = fp.pairing(ingredient, 0.4)
        except KeyError:
            print("couldnt pair ingredient")
            return
        print("new ingredients list", new_ingredients)
        if len(new_ingredients) > 1: # if we found an ingredient, add it to recipe
            rand_item = random.randint(0, len(new_ingredients)-1)
            new_ingredient = AddIns(list(new_ingredients.keys())[rand_item], {"0.5 cup":1}) # Need to determine what quantity to put
            key_to_replace = list(self.add_ins.keys())[rand_int]
            del self.add_ins[key_to_replace]
            self.add_ins[new_ingredient.name] = new_ingredient.getQuantity()
        else:
            return
        return new_ingredient








        




