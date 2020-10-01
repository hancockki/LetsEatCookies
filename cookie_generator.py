import selenium
import re
import random

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

    #need to extract the quantities dictionary for each 

    # BASE INGREDIENTS #
    base_ingredients = []
    base_ingredients.append(BaseIngredient(name="flour",quantities={}))
    base_ingredients.append(BaseIngredient(name="egg", quantities={}))
    base_ingredients.append(BaseIngredient(name="granulated sugar", quantities={}))
    base_ingredients.append(BaseIngredient(name="brown sugar", quantities={}))
    base_ingredients.append(BaseIngredient(name="butter", quantities={}))
    base_ingredients.append(BaseIngredient(name="salt", quantities={}))
    base_ingredients.append(BaseIngredient(name="all-purpose flour", quantities={}))
    base_ingredients.append(BaseIngredient(name="baking soda", quantities={}))
    base_ingredients.append(BaseIngredient(name="baking powder", quantities={}))

    # update quantities dictionary for each of the base ingredients
    for i in base_ingredients:
        for recipe in recipes:
            for ingredient in recipes[recipe]:
                if i.name in ingredient:
                    q = re.search(r'^[0-9]+(\/[0-9]+)*(\sand\s)*([0-9]+(\/[0-9]+))*\s[a-zA-Z]+', ingredient)
                    if q is not None:
                        quantity = q.group()
                        i.updateQuantity(quantity)



                    

processRecipes()


