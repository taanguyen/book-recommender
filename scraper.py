#! python3
# book_scraper.py Collects book recommendations from The CEO Library

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def print_books(books):
	for book in books:
		print(book)

import requests, sys, webbrowser, bs4

query = input("Name of Thought Leader: ")
query = query.split(" ")
query = "-".join(query)

# Book titles 
books = set()

# URL for The CEO Library
base_url = f"https://www.theceolibrary.com/books-recommended-by/{query}" 
url = base_url

curr_page_num = 0
last_page_num = 1 

while curr_page_num < last_page_num:
	try:
		# Request data from CEO Library	
		req = requests.get(url)  
		req.raise_for_status()
		soup = bs4.BeautifulSoup(req.text, "html.parser") 

		# Fetch all book recommendations on current page 
		title_links = soup.select(".book-title a")
		for link in title_links:
			title = str(link.contents[0])
			books.add(title)	

		# Fetch next page 
		curr_page = soup.select(".custom-wp-pagination.cf span")[0]
		curr_page_num = int(curr_page.contents[0])

		pages = soup.select(".custom-wp-pagination.cf a")
		
		for page in pages:
			next_page = page.get("href")
			next_page_num = page.contents[0]
			
			if is_int(next_page_num):
				next_page_num = int(next_page_num)
				if next_page_num > curr_page_num:
					# get url for scraping next page of recommendations
					url = base_url + next_page
					last_page_num = next_page_num
					break
	except: 
		print_books(books)
		sys.exit()
				
print_books(books)





