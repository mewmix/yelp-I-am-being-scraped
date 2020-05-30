#import beautiful soup and requests libraries required for web-scraping
from bs4 import BeautifulSoup
import requests


#yelp url to access all businesses in los angeles
print('--------Getting URLs---------')
URL = ['https://www.yelp.com/search?find_desc=Restaurants&find_loc=Laguna%20Niguel'.format(i*10) for i in range(20)]
print('Done.', end='\n\n')

#get the html content of all the pages in the url array
print('--------Getting page contents---------')
pages = [requests.get(url) for url in URL]
print('Done.', end='\n\n')

#set up beautiful soup objects to later analyse the pages
print('--------Setting up beautiful soup ---------')
soups = [BeautifulSoup(page.content, 'html.parser') for page in pages]
print('Done.', end='\n\n')

#get all restaurant divs in each page
#each business is displayed on the page with the following class. This finds and gets the content of all the divs with the following class name
business_pages = [soup.find_all("div", {"class": "lemon--div__373c0__1mboc container__373c0__3HMKB hoverable__373c0__VqkG7 margin-t3__373c0__1l90z margin-b3__373c0__q1DuY padding-t3__373c0__1gw9E padding-r3__373c0__57InZ padding-b3__373c0__342DA padding-l3__373c0__1scQ0 border--top__373c0__3gXLy border--right__373c0__1n3Iv border--bottom__373c0__3qNtD border--left__373c0__d1B7K border-color--default__373c0__3-ifU"}) for soup in soups]


#class to store and obtain information about a bussiness
class Business:
    #to initialize the class with the business' HTML content that we later analyze in the methods
    def __init__(self, HTML):
        self.HTML = HTML
        
    #within each business div, the name is present in the text field of the following <a> tag
    def name(self):
        name = self.HTML.find('a', {"class": "lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE"}).text
        
        return name
    
    #the rating is displayed in terms of stars but the <span> tag contains the stars in the form of "## star rating"
    def rating(self):
        
        rating = self.HTML.find('div',{"class": "lemon--div__373c0__1mboc display--inline-block__373c0__1ZKqC border-color--default__373c0__3-ifU"})
        rating = rating.find('span').find('div').get('aria-label')
        rating = rating.replace(' star rating', '')
        
        return rating
    
    #the price is displayed within the business div in the form of $$ signs
    def price(self):
        
        price = self.HTML.find('div',{"class": "lemon--div__373c0__1mboc priceCategory__373c0__3zW0R display--inline-block__373c0__1ZKqC border-color--default__373c0__3-ifU"})
        price = price.find('span').find('span')
        price = price.text
        
        return price
    
    def num_reviews(self):
        
        reviews = self.HTML.find('div', {'class': "lemon--div__373c0__1mboc attribute__373c0__1hPI_ display--inline-block__373c0__1ZKqC border-color--default__373c0__3-ifU"})
        
        reviews = reviews.find('span').text
        
        return reviews
        
    #keywords related to the business are displayed in a series with the same <span> tag and corresponding class name
    #this function get all those span tags and gets the keyword from them
    def keywords(self):
        
        keywords = self.HTML.find('div', {'class': 'lemon--div__373c0__1mboc priceCategory__373c0__3zW0R display--inline-block__373c0__1ZKqC border-color--default__373c0__3-ifU'})

        keywords = keywords.find_all('span', {'class': 'lemon--span__373c0__3997G display--inline__373c0__3JqBP border-color--default__373c0__3-ifU'})[1]
        #keywords here contains all the span tags that contain the keywords
        keys = []
        
        for i in range(len(keywords)):    #get the keywords from each span tag
            k = keywords.find_all('span', {'class': 'lemon--span__373c0__3997G text__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align--left__373c0__2XGa-'})[i]
            keys += [k.text.replace(', ', '')]
        
        return keys
            
    #get the business' contact number
    def number(self):
        
        number = self.HTML.find('p',{"class": "lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align--right__373c0__1f0KI text-size--small__373c0__3NVWO"})
        
        return number.text
    
    #get the address of the business displayed
    def address(self):
        
        #ignore the first one as the first p tag in the HTML contains the phone number that we already obtained
        address = self.HTML.find_all('p', {'class': 'lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align--right__373c0__1f0KI text-size--small__373c0__3NVWO'})[1:]
        
        #for each line of address found, get the text field
        address = [ad.text for ad in address]
        
        #join all the lines of addresses (separated by ; instead of , since outputting to a csv file)
        address = '; '.join(address)
        
        return address
        
f = open("businesses.csv", "w")    #open a csv file to write the data

#header for the name of the columns in the csv file
header = "Name, Rating, Price, Number of Reviews, Keywords, Phone Number, Address"

#write header as the first row of the file
f.write(header)

#for each page in the pages with businesses listed
for page in business_pages:
    #for each business within the page
    for business in page:
        #initialize the object with the HTML content of each business
        business = Business(business)
        
        #the try-except blocks help prevent errors related to some missing information on the website
        #this arises empty fields in the csv files corresponding to missing information
        try:
            name = business.name()
        except:
            name = ""
        try:
            rating = business.rating()
        except:
            rating = ""
        try:
            price = business.price()
        except:
            price = ""
        try:
            num_reviews = business.num_reviews()
        except:
            num_reviews = ""
        try:
            keywords = business.keywords()
        except:
            keywords = ""
        try:
            number = business.number()
        except:
            number = ""
        try:
            address = business.address()
        except:
            address = ""
            
        #write all the contents found in a new line in the csv file
        f.write('\n' + name + ',' + rating + ',' + price + ',' + num_reviews + ',' + str(keywords).replace(',', ';') + ',' + number + ',' + address)

#close the previously opened file
f.close()
