from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json


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
                break
            recipes[title].append([ingredient, string_ingredient])

    driver.close()
    with open('recipes.json', 'w') as fp:
        json.dump(recipes, fp)

    fp.close()
    return recipes