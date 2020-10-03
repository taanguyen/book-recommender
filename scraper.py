# scraper.py Collects book recommendations from The CEO Library
import requests, sys, webbrowser, bs4
from book import Book

class Scraper:
	# URL for The CEO Library
	base_url = "https://www.theceolibrary.com/books-recommended-by/" 
	home = "http://www.theceolibrary.com"
	
	def __init__(self, leader: str):
		self.leader = leader
		self.books = self.scrapeBooks()
	
	def scrapeBooks(self):
		books = []
		formattedLeader = self.leader.replace(" ", "-")
		url = f"{self.base_url}{formattedLeader}"

		curr_page_num = 0
		last_page_num = 1 

		while curr_page_num < last_page_num:
			try:
				# Request data from CEO Library	
				req = requests.get(url)  
				req.raise_for_status()
				soup = bs4.BeautifulSoup(req.text, "html.parser") 

				entries = soup.select(".fcl-entry")
				for entry in entries:
					# get cover
					cover_container = entry.find("div", class_="book-cover")
					cover_url = self.home + cover_container['data-bgset']
					
					# get title
					title_container = entry.find("h2", class_= "book-title")
					title = title_container.a.string
					
					# get authors
					authors = []
					author_container = entry.find("p", class_ = "book-info")
					author_links = author_container.find_all("a")
					for author_link in author_links:
						authors.append(author_link.string)
					
					# scrape profile and BookDepository for info, isbn, rating
					book_profile = cover_container.find('a')['href']
					book_profile_url = self.home + book_profile
					profile_req = requests.get(book_profile_url)
					profile_req.raise_for_status()
					profile_soup = bs4.BeautifulSoup(profile_req.text, 'html.parser')

					buy_container = profile_soup.find("div", class_ = "buy-book")
					bookdep_url = buy_container.find(id="aff-book-depository")['href']
					isbn, rating = scrapeBookVendor(bookdep_url)

					info_container = profile_soup.find("div", class_ = "amazon-book-description")
					info = info_container.find_all("p")
					
					book = Book(isbn, title, authors, cover_url, info, rating)
					books.append(book)
					
				# Fetch next page 
				curr_page = soup.select(".custom-wp-pagination.cf span")[0]
				curr_page_num = int(curr_page.string)

				pages = soup.select(".custom-wp-pagination.cf a")

				for page in pages:
					next_page = page.get("href")
					next_page_num = page.string
					
					if is_int(next_page_num):
						next_page_num = int(next_page_num)
						if next_page_num > curr_page_num:
							# get url for scraping next page of recommendations
							url = self.base_url + next_page
							last_page_num = next_page_num
							break
			except Exception as e: 
				print(e)
						
		#print_books(books)
		return books

def is_int(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def print_books(books):
	for book in books:
		print(book)

def scrapeBookVendor(url):
    req = requests.get(url)
    req.raise_for_status()
    soup = bs4.BeautifulSoup(req.text, "html.parser")
    rating = float(soup.find(itemprop="ratingValue").string)
    isbn = soup.find(itemprop="isbn").string
    return (isbn, rating)

