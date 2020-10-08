# LetsEatCookies
The purpose of this program is to use 

## cookie_classes.py
Class Overview:


### BaseIngredient
BaseIngredient objects have the following attributes:
- **name**, which is a string representing the name of the ingredient
- **quantities**, which is a dictionary mapping quantities of the ingredient to the number of times each quantitiy appears in the inspiring set

The BaseIngredient class has the following functions:
- **getQuantity**, where the quantities attribute can be retreived
- **updateQuantity**, where the quantities attribute can be re-assigned

### AddIns
AddIn objects have the following attributes:
- **name**, which is a string representing the name of the ingredient
- **quantities**, which is a dictionary mapping quantities of the ingredient to the number of times each quantitiy appears in the inspiring set

The AddIns class has the following functions:
- **getQuantity**, where the quantities attribute can be retreived
- **updateQuantity**, where the quantities attribute can be re-assigned

### Recipe
Recipe objects have the following attributes:
- **name**, which is a string representing the name of the recipe
- **base_ingredients**, which is a list of BaseIngredient objects 
- **add_ins**, which is a list of AddIns objects


## generate_cookies.py
There are no classes within generate_cookies.py, but it contains the following functions:
- **buildNewRecipe**, which creates new recipies (or "offspring") utilizing a genetic approach. Essentially, a random pivot point from each AddIns list list is chosen, and then a new recipe is made that is before pivot for add_ins_recipe_1 and after pivot for add_ins_recipe_2. All of the BaseIngredients are added from the given base_ingredients. A new Recipe object is returned with the new base ingredients and add ins.
- **getInspiringSet**, which populates the inspiring set with the dictonary of recipes from the web crawl in driver.py, with the name mapped to the ingredients/quantities. It builds and returns a list of BaseIngredient objects and AddIns Objects from all of the recipes and Recipe Objects for each recipe.
- **writeToFile**, which writes a given recipe to a new text (.txt) file. It is given a Recipe object, and utilized the name of the recipe to create a file in the recipies directory. In this file, each ingredient/it's corresponding quantity is written on it's own line .


## driver.py
There are no classes within driver.py, but it contains the following functions:
- **getCookieRecipes**, which crawls through the website sally's baking addiction for cookie recipes used to populate our inspiring set. It is given a list of links to the desired resipies to walk through. It returns a dictionary where the keys are recipe names, and the values are dictionaries mapping each ingredient to its quantity.

## Running the program
To run the program, first clone this github repository onto your local machine in a directory of your choice.
Then, simply run the following command from the terminal:

```bash
python3 generate_cookies.py
```
