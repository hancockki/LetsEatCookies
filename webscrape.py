from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json

"""
In this function, we are crawling the website sally's baking addiction for cookie recipes for our inspiring set

Essentially, we start the crawl from the link to the category of the website listing cookie recipes, then
go to the page for each recipe and extract the ingredients

@params:
    starting_link --> the link we are starting the crawl from

"""
def getCookieRecipes(starting_link):
    recipe_links = [] #empty list which we will populate with links to specific recipes
    recipes = {}
    #the below 5 lines set up the conditions for our web browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")

    # create our webdriver object
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
    # initialize next link
    next_link = starting_link 
    # there are 16 pages of cookie recipes, so we loop through all 16 (We can modify this if we want less in our inspiring set)
    for i in range(1): 
        driver.get(next_link) # go to the current link with our webdriver
        cookie_recipe_links = driver.find_elements_by_class_name('c-archive-post') # c-archive-post is the html class containing the href to the recipes
        for link in cookie_recipe_links: # loop through the links
            recipe_links.append(link.find_element_by_css_selector('a').get_attribute('href')) # add href to links list
            #print(link.find_element_by_css_selector('a').get_attribute('href'))
        #in this next line, we append the end of the link to reflect the page num we want (represented by i)
        next_link = starting_link + "page/"+str(i)+'/' 

    #now, we want to loop through the recipe links
    for link in recipe_links:
        driver.get (link) #open link to recipe
        # get inner html, aka text of the javascript json
        type_link = driver.find_element_by_xpath('//script[@type="application/ld+json"]').get_attribute('innerHTML')
        # load the json object
        itemjson = json.loads(type_link.strip())
        #loop through part of the json we want
        for key in itemjson['@graph']:
            # if the json key we want is present
            if "headline" in key.keys():
                name = key["headline"]
                recipes[name] = []
            if "recipeIngredient" in key.keys():
                for ingredient in key['recipeIngredient']:
                    recipes[name].append(ingredient)
                    #print(ingredient)

    driver.close()
    return recipes


#getCookieRecipes('https://sallysbakingaddiction.com/category/desserts/cookies/')
