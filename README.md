# LetsEatCookies
The purpose of this program is to use cookie recipes from the internet to generate new recipes with creative ingredients! We are using recipes from Sally's Baking as the recipes on this site are really fun and lots of them have unique add-ins that we can use!

## cookie_classes.py

### BaseIngredient Class
BaseIngredient objects have the following attributes:
- **name**, which is a string representing the name of the ingredient
- **quantities**, which is a dictionary where keys are the quantity and value is the number of times that quantity is seen across all recipes.
    For instance, if self.name = "butter and self.quantities = {"1 cup": 5, "0.5 cup": 6}, this indicates that butter
    is found in 11 recipes, 5 times with 1 cup and 6 times with 0.5 cup

The BaseIngredient class has the following functions:
- **getQuantity**, where the quantities attribute can be retreived
- **updateQuantity**, where the quantities attribute can be re-assigned

### AddIns Class
AddIn objects have the following attributes:
- **name**, which is a string representing the name of the ingredient
- **quantities**, which is a dictionary where keys are the quantity and values are the number of times that quantity occurs across all recipes.
    For instance, if self.name = "chocolate" and self.quantities= {"1 cup": 3, "2 cups": 2}, this indicates that chocolate
    is found in 5 recipes, 3 times with 1 cup and twice with 2 cups


The AddIns class has the following functions:
- **getQuantity**, where the quantities attribute can be retreived
- **updateQuantity**, where the quantities attribute can be re-assigned

### Recipe Class
Recipe objects have the following attributes:
- **name**, which is a string representing the name of the recipe
- **base_ingredients**, which is a dictionary mapping the base ingredient to the quantity. For instance, {"butter":"0.5 cup", "all purpose flour":"2 cups"} could be the attribute. The quantity is determined probabilistically based on the overall list of BaseIngredient objects, such that the more times a certain quantity is seen across all recipes, the more likely it is we pick that quantity.
- **add_ins**, which is a dictionary mapping the add in to the quantity. For instance, {"chocolate chips":"0.5 cup", "vanilla":"2 teaspoons"} could be the attribute. The quantity is determined probabilistically based on the overall list of AddIn objects, such that the more times a certain quantity is seen across all recipes, the more likely it is we pick that quantity.

### Functions Outside of Classes
- **fitnessFunction**, which returns the fitness of our recipe, based on the similarity between our ingredients. To calculate fitness, we first use combinations to get all the combinations of two add-ins. Then, we compute the similarity between them, if possible, and add it to the total fitness. If it's not possible, we subtract 1 from the total number of combinations and add 0 to total fitness. Then, we divide total fitness by the number of combinations we were able to calculate the similarity of. This becomes our fitness.
- **addIngredient**, which returns a single AddIn object to be added to a new recipe that pairs within .55 of an existing addIn ingredient. The keys are new ingredient names from the .npy files, and the values are the quantities pulled from the AddIn ingredient it was paired from.
- **replaceIngredient**, which returns an AddInn object to replace a random ingredient in a recipe with an ingredient that pairs well with another ingredient in the recipe.


## generate_cookies.py
There are no classes within generate_cookies.py, but it contains the following functions:
- **buildNewRecipe**, which creates new recipies (or "offspring") utilizing a genetic approach. Essentially, it first picks two recipes probabilistically based on their fitness (higher fitness=higher chance of being picked), then picks add-ins from these based on the flavor pairings between the recipes. Better flavor similarity across add-ins means that pair is more likely to be added. We also have mutations implemented with an 80% of a mutation. The two mutations are adding a new add-in or replacing an add-in with a new one from the flavor pairing database. If the new ingredient we add doesn't have an AddIn object created for it, we make one so that it can appear in future recipes as well.

- **getInspiringSet**, which populates the inspiring set with the dictonary of recipes from the web crawl in webcrawl.py, with the name mapped to the ingredients/quantities. It builds and returns a list of BaseIngredient objects and AddIns Objects from all of the recipes and a list of Recipe Objects. We dynamically add to each of these data structures as new recipes are made.
- **writeToFile**, which writes a given recipe to a new text (.txt) file. It is given a Recipe object, and utilized the name of the recipe to create a file in the recipies directory. In this file, each ingredient/it's corresponding quantity is written on it's own line. Instructions are also added.


## webcrawl.py
There are no classes within webcrawl.py, but it contains the following functions:
- **getCookieRecipes**, which crawls through the website sally's baking addiction for cookie recipes used to populate our inspiring set. It is given a list of links to the desired resipies to walk through. It returns a dictionary where the keys are recipe names, and the values are dictionaries mapping each ingredient to its quantity. The list of recipes can be changed as the method for grabbing the ingredients is the same on any page on the website.

## Running the program
To run the program, first clone this github repository onto your local machine in a directory of your choice.

git clone [link to this repo]
Then, simply run the following command from the terminal in the LetsEatCookies directory:

python3 generate_cookies.py

```bash
python3 generate_cookies.py
```

## Discussion
**Metric One:** From Ventura's odyssey we explored the step of Generalization. Through the process of web scraping we built an inspiring set that models the recipes from Sally's Baking Addiction and places bias on the ingredient quantities (ones that appear more have a higher probability during the selection process). This is approaching generalization, but still closely resemples memorization. Generalization is clearly seen during our recipe creation when selecting add ins. There is regulazation by selecting existing items in the recipe, particularly because their is bias towards ingredients pair well with each other, but  there is exploration through the indroduction of mutations. The mutations select items outside of the inspiring set, but with the bias of pairing well with items in the set. So there is exploration, but in a non-trivial way.

**Metric Two:** From Ventura's odyssey we also explored the step of Filtration, and ideas of self evalutaiton from our system. 

**Results:**

"As a hint for success for your overall code submission, I would encourage you to describe your two metrics/perspectives in your README, along with a description of your results which indicated that your system produced better recipes with them (as opposed to without them!)."
