from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
#from cookie_generator import Recipe
#from cookie_generator import BaseIngredients
#from cookie_generator import AddIns


"""
In this function, we are crawling the website sally's baking addiction for cookie recipes for our inspiring set

Essentially, we start the crawl from the link to the category of the website listing cookie recipes, then
go to the page for each recipe and extract the ingredients

@params:
    link_list --> the links to recipes we want!

@returns:
    recipes --> a dictionary where the keys are recipe names, and the values are dictionaries mapping each ingredient to its quantity

"""
def getCookieRecipes(link_list):
    recipes = {}
    #the below 5 lines set up the conditions for our web browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")

    # create our webdriver object
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)

    #now, we want to loop through the recipe links
    for link in link_list:
        driver.get (link) #open link to recipe
        # now, we want to find all of our ingredients and quantities
        title = driver.find_element_by_class_name("tasty-recipes-title").text #get the ingredients class from html
        print(title)
        recipes[title] = []
        ingredients = driver.find_element_by_class_name("tasty-recipes-ingredients") #get the ingredients class from html
        list_items = ingredients.find_elements_by_tag_name("li") # get list items for ingredients
        for item in list_items: # loop through ingredients
            string_ingredient = ""
            ingredient = item.find_element_by_tag_name("strong").text # this is the ingredient name
            ingredient_amounts = item.find_elements_by_css_selector('span')  # span tag holds our amount info
            for amount in ingredient_amounts: 
                data_amount = amount.get_attribute('data-amount')
                data_unit = amount.get_attribute('data-unit')
                if data_amount != None:
                    string_ingredient += data_amount + " "
                if data_unit != None:
                    string_ingredient += data_unit + " "
                #string_ingredient += "or"
                break
            #string_ingredient += ingredient
            recipes[title].append([ingredient, string_ingredient])

    print(recipes)

    # THIS WILL RETURN A DICTIONARY MAPPING INGREDIENTS TO QUANTITIES
    driver.close()
    return recipes


#getCookieRecipes('https://sallysbakingaddiction.com/category/desserts/cookies/')
#getCookieRecipes(['https://sallysbakingaddiction.com/pumpkin-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/peanut-butter-cookies/', 'https://sallysbakingaddiction.com/soft-chewy-oatmeal-raisin-cookies/', \
 #   'https://sallysbakingaddiction.com/crispy-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/soft-molasses-cookies/','https://sallysbakingaddiction.com/dark-chocolate-cranberry-almond-cookies/', \
  #      'https://sallysbakingaddiction.com/zucchini-oatmeal-chocolate-chip-cookies/', 'https://sallysbakingaddiction.com/cookies-n-cream-cookies/'])






# OLD CODE ---- IGNORE

    # initialize next link
    #next_link = starting_link 
    # there are 16 pages of cookie recipes, so we loop through all 16 (We can modify this if we want less in our inspiring set)
    
    #for i in link_list: 
"""
        driver.get(next_link) # go to the current link with our webdriver
        cookie_recipe_links = driver.find_elements_by_class_name('c-archive-post') # c-archive-post is the html class containing the href to the recipes
        for link in cookie_recipe_links: # loop through the links
            recipe_links.append(link.find_element_by_css_selector('a').get_attribute('href')) # add href to links list
            print(link.find_element_by_css_selector('a').get_attribute('href'))
        #in this next line, we append the end of the link to reflect the page num we want (represented by i)
        next_link = starting_link + "page/"+str(i)+'/' 
        """
            #for item in amount:
             #   print(item)
            #for item in specific_ingredient:
            #    amount = item.get_attribute("data-amount")
            #    data_unit = item.get_attribute("data-unit")
             #   if amount != None:
            #        print(amount)
            #    if data_unit != None:
            #        print(data_unit)
""" 
            if "recipeIngredient" in key.keys():
                for ingredient in key['recipeIngredient']:
                    recipes[name].append(ingredient)

            if "recipeInstructions" in key.keys():
                instructions = key["recipeInstructions"]
                recipes["instructions"] = []
                for step in instructions:
                    for key, value in step.items():
                        if key == 'text':
                            recipes["instructions"].append(value)

# get inner html, aka text of the javascript json
        type_link = driver.find_element_by_xpath('//script[@type="application/ld+json"]').get_attribute('innerHTML')
        # load the json object
        itemjson = json.loads(type_link.strip())
        #loop through part of the json we want
        for key in itemjson['@graph']:
            # if the json key we want is present
            if "headline" in key.keys():
                name = key["headline"]
                print(name)
                recipes[name] = {} 
"""

"""
Here, we want to build our Ingredient and Recipe objects for our inspiring set

@params:
    recipes --> dictionary of recipes
    base_ingredients --> base ingredients hard coded into our program

@returns:
    recipe_objects --> list of recipe objects


def buildInspiringSet(recipes, base_ingredients):
    base_ingredient_objects = {} # store base ingredient objects
    add_ins_object_list = [] 
    recipes_list = []
    # each key of recipes is a name and the value is the ingredients 
    for recipe_name, ingredients in recipes.items():
        for ingredient_name, ingredient_quantity in ingredients.items():
            # if our ingredient is a base ingredient
            if ingredient_name in base_ingredients:
                # if the base ingredient object has already been created
                if ingredient_name in base_ingredient_objects.keys():
                    base_ingredient_objects[ingredient_name] += 1
                else:
                    quantities = {}
                    for i in range(0, len(ingredient_quantity), 2):
                        quantity = ingredient_quantity[i] + ingredient_quantity[i+1]
                        quantities[quantity] = 1
                    base_ingredient_objects[ingredient_name] = BaseIngredients(ingredient_name, quantities)
            else:
                if ingredient_name in add_ins_object_list:

"""