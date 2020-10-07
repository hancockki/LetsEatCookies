import selenium
import numpy
import random
import re
import flavorpairing as fp
from itertools import combinations

from driver import getCookieRecipes

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
        self.similarity = self.fitnessFunction()

    """
    Returns the fitness of our recipe, based on the similarity between our ingredients

    We have the best_fit data structure to account for names of add ins that are unusual, and are not in the data base. In this case, we pair
    the ingredient to something close to it. In some cases, the ingredient is weird (like cornstarch) and so we ignore those cases

    To calculate fitness, we first use combinations to get all the combinations of two add-ins. Then, we compute the similarity between them, if possible,
    and add it to the total fitness. If it's not possible, we subtract 1 from the total number of combinations and add 0 to total fitness.
    Then, we divide total fitness by the number of combinations we were able to calculate the similarity of. This becomes our fitness.

    """
    def fitnessFunction(self):
        # dictionary mapping add in name to 'best fit' name 
        best_fit = {"M&Ms": "chocolate", "pumpkin puree": "pumpkin", "molasses": "honey", "white chocolate morsels": "chocolate", "dried cranberries": "cranberry", \
            "almond extract": "almond", "semi-sweet chocolate": "chocolate", "pistachios":"pistachio", "chocolate chips": "chocolate", "Biscoff spread": "cinnamon", \
                "pumpkin pie spice": "allspice", "bittersweet chocolate":"chocolate", "raisins":"raisin", "pure maple syrup":"honey", "semi-sweet chocolate chips":"chocolate", \
                    "white chocolate chips":"chocolate", "ground ginger":"ginger","ground cardamom":"cardamom", "Oreos":"chocolate"}
        
        total = 0 # initialize total
        total_num = len(list(combinations(self.add_ins, 2))) # total number of combinations
        print("total num", total_num)
        for combination in combinations(self.add_ins, 2):
            try: # try to find similarity
                if combination[0] in best_fit: # if it's in our best fit dictionary
                    ingredient1 = best_fit[combination[0]]
                else:
                    ingredient1 = combination[0]
                if combination[1] in best_fit: #if ingredient 2 is in our best fit dictionary
                    ingredient2 = best_fit[combination[1]]
                else:
                    ingredient2 = combination[1]
                print("similarity", fp.similarity(ingredient1, ingredient2))
                total += fp.similarity(ingredient1, ingredient2) # add similarity to total 
            except KeyError: # we didn't find the ingredient in our database
                print("not found in database", combination[0], combination[1])
                total_num -= 1 #subtract 1 from total num conmbinations
        if total_num > 0: #if we found some similarities
            total = (total / total_num) * 100
        else:
            total = 0
        print("total similarity", total)
        return total



    




