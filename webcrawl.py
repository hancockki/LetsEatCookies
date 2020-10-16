"""
Authors: Kim H, Kayla S, Lydia P
CSCI 3725 - Computational Creativity
Party Quest 2: Smart Cookies
Last Modified: Oct 16, 2020

The purpose of this program is to use cookie recipes from the internet to generate new recipes 
with creative ingredients! We are using recipes from Sally's Baking as the recipes on this site
are really fun and lots of them have unique add-ins that we can use! We hace named our system
GECCO - Genetically Exploring Creative Cookie Options.

This file in contains our web scraping functions. It is utilized in generate_cookies.py in order
to build our inspiring set from Sally's Baking Addiction website.

Known bugs:
Currently, the webcrawl looks for specific html tags that are used across ALL sally's baking addiction
recipes to store ingredients. However, there might be instances where the html tag is different in a 
recipe (such as if the webpage is changed or a certain recipe is old and has different html tags) and 
thus the webcrawl is not able to find a certain ingredient or quantity. The only recipe in our inspiring
set where this is currently an issue is in Bunny Sugar Cookies, as the program does not find quantities
for salt or butter. There might be a better way to loop through the html to avoid this, but this was 
the best way we found!

Other bugs may arise from other html tags that might not be found on the webpage if they are changed.
We are speaking about lines 68 (where we get the title of the recipe), line 72 (where we get the ingredients),
line 80 (where we get the quantities), and lines 85-85 (where we get quantity name and amount).

Also, this is not a bug, but webdriver has a number of dependencies in order to run that you might not
necessarily have installed on your machine. Lines 48-52 should help avoid this by setting certain webdriver
features off that typically lead to errors, and line 57 installs Chrome Driver Manager automatically. This is
helpful since most people probably don't have this installed already.
Before running, simply pip install webdriver and that **should** be all you need.
"""


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json


def get_cookie_recipes(link_list):
    """
    In this function, we are crawling the website sally's baking addiction for cookie recipes for our inspiring set
    Essentially, we start the crawl from the link to the category of the website listing cookie recipes, then
    go to the page for each recipe and extract the ingredients

    @params:
        link_list --> the links to recipes we want!

    @returns:
        recipes --> a dictionary where the keys are recipe names, and the values are dictionaries mapping each ingredient to its quantity
    """
    recipes = {}
    #the below 5 lines set up the conditions for our web browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")

    # create our webdriver object. We use chrome but if you have a different broswer, webdriver supports pretty much everything!
    # click this link for more info related to webdriver: https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
    #now, we want to loop through the recipe links
    for link in link_list:
        #open link to recipe
        driver.get (link) 
        # we want to find all of our ingredients and quantities 
        title = driver.find_element_by_class_name("tasty-recipes-title").text 
        # initialize list for that recipe which will store the ingredients and quantities
        recipes[title] = []
        #get the ingredients class from html
        ingredients = driver.find_element_by_class_name("tasty-recipes-ingredients") 
        # get list items of that html class, which are the ingredients
        list_items = ingredients.find_elements_by_tag_name("li") 
        # loop through ingredients
        for item in list_items: 
            ingredient_amount = ""
            # this is the ingredient name
            ingredient = item.find_element_by_tag_name("strong").text 
            # span tag holds our amount info
            ingredient_amounts = item.find_elements_by_css_selector('span')  
            #loop through amounts found (not all may make sense)
            for amount in ingredient_amounts: 
                data_amount = amount.get_attribute('data-amount') # get amount
                data_unit = amount.get_attribute('data-unit') # get unit (ex: cup)
                if data_amount != None:
                    ingredient_amount += data_amount + " "
                if data_unit != None:
                    ingredient_amount += data_unit + " "
                break
            recipes[title].append([ingredient, ingredient_amount])

    driver.close()
    #save recipes and their ingredients to a file
    with open('recipes.json', 'w') as fp:
        json.dump(recipes, fp)

    fp.close()
    return recipes