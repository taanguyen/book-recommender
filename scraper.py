# scraper.py Collects book recommendations from The CEO Library
import requests, sys, webbrowser, bs4, xmltodict, json
from book import Book
from config import Config
import concurrent.futures 
import time
import threading
from collections import Counter


class Scraper:
	# URL for The CEO Library
	base_url = "https://www.theceolibrary.com/books-recommended-by/" 
	home = "http://www.theceolibrary.com"
	lock = threading.Lock()

	@staticmethod
	def bookFromUrl(url):
		try:
			# Request data from CEO Library
			# set headers
			headers = {
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
			}	
			req = requests.get(url, headers=headers)  
			req.raise_for_status()
			soup = bs4.BeautifulSoup(req.text, "html.parser") 
			
			# get cover
			cover_url = getCoverUrl(soup, 'book-cover-actions')			
			# get title
			title = getTitle(soup, "book-info-intro")
			# get authors
			authors = getAuthors(soup, "book-info-intro")
			# get isbn and rating
			#isbn, rating = getISBNRating(soup, "buy-book")	
			rating = goodReadsSearchBook(title, authors[0])
			info = getInfo(soup, "amazon-book-description")
			book = Book(title, authors, info, cover_url, "NA", rating)
			return book

		except Exception as e: 
			print(e) 
			
	@staticmethod
	def booksWithFreq(leaders):
		# get unique book urls with frequency -- multithreading
		bookUrlsWithFreq = Scraper.bookUrlsWithFreq(leaders)
		with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
			books = executor.map(Scraper.bookFromUrl, bookUrlsWithFreq.keys())
		bookObjectsWithFreq = list(zip(books, bookUrlsWithFreq.values()))
		return bookObjectsWithFreq
		# books = []
		# bookUrlsWithFreq = Scraper.bookUrlsWithFreq(leaders)
		# for url,freq in bookUrlsWithFreq:
		# 	book = Scraper.bookFromUrl(url)
		# 	books.append((book, freq))
		# return books
	# input: leader name in format "firstname lastname"
	@staticmethod
	def scrapeBookUrlsForLeader(leader):
		bookUrls = set()
		formattedLeader = leader.replace(" ", "-")
		base_url_with_leader = f"{Scraper.base_url}{formattedLeader}"
		url = base_url_with_leader
		
		curr_page_num = 0
		next_page_num = 1 
		
		while curr_page_num < next_page_num:
			try:
				# Request data from CEO Library	
				req = requests.get(url)  
				req.raise_for_status()
				soup = bs4.BeautifulSoup(req.text, "html.parser") 

				entries = soup.select(".fcl-entry")
				for entry in entries:
					# scrape for book url
					cover_container = entry.find("div", class_="book-cover")					
					book_profile = cover_container.find('a')['href']
					book_profile_url = Scraper.home + book_profile
					bookUrls.add(book_profile_url)
				
				# Fetch curr and next pages
				curr_pages_span = soup.select(".custom-wp-pagination.cf span")
				if not curr_pages_span: break
				curr_page = curr_pages_span[0]
				curr_page_num = int(curr_page.string)
				pages = soup.select(".custom-wp-pagination.cf a")
				
				for page in pages:
					next_page = page.get("href")
					next_page_num = page.string
					
					if is_int(next_page_num):
						next_page_num = int(next_page_num)
						if next_page_num > curr_page_num:
							# get url for scraping next page of recommendations
							url = base_url_with_leader + next_page
							break
			except Exception as e: 
				print(e)
				continue
		return bookUrls
	# input: names of leaders in a list 
	@staticmethod
	def bookUrlsWithFreq(leaders):
		uniqueBookUrls = Counter()
		with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
			bookUrls = executor.map(Scraper.scrapeBookUrlsForLeader, leaders)	
			with Scraper.lock: 
				for bookUrl in bookUrls:
					uniqueBookUrls.update(bookUrl)
		uniqueUrls = list(uniqueBookUrls.items())
		uniqueUrls.sort(key=lambda x: x[1])
		return uniqueBookUrls

		# uniqueBookUrls = {}
		# for leader in leaders:
		# 	bookUrls = Scraper.scrapeBookUrlsForLeader(leader)
		# 	for bookUrl in bookUrls:
		# 		if bookUrl not in uniqueBookUrls:
		# 			uniqueBookUrls[bookUrl] = 0
		# 		uniqueBookUrls[bookUrl] += 1 
		# return uniqueBookUrls

def is_int(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def print_books(books):
	for book in books:
		print(book)

def getCoverUrl(soup, class_):
	cover_div = soup.find("div", class_= class_)
	cover = cover_div.img['src']
	cover_url = Scraper.home + cover 
	return cover_url

def getTitle(soup, class_):
	title_div = soup.find("div", class_= class_)
	title = title_div.h1.a.string
	return title

def getAuthors(soup, class_):
	authors = []
	author_div = soup.find("div", class_= class_).find('p')
	author_links = author_div.find_all("a")
	for author_link in author_links:
		authors.append(author_link.string)
	return authors

def getInfo(soup, class_):
	info_container = soup.find("div", class_ = class_)
	info = info_container.find_all("p")
	unique_paras = []
	# remove duplicate paragraphs
	for i in range(len(info)):
		print(info[i].text)
		if i > 0:
			if info[i].text == info[i-1].text:
				continue
		unique_paras.append(info[i])
	return unique_paras

def getISBNRating(soup, class_):
	buy_div = soup.find("div", class_ = class_)
	bookdep_url = buy_div.find(id="aff-book-depository")['href']
	isbn, rating = scrapeBookVendor(bookdep_url)
	return isbn, rating

def scrapeBookVendor(url):
	try:
		time.sleep(1.0)
		req = requests.get(url)
		req.raise_for_status()
		soup = bs4.BeautifulSoup(req.text, "html.parser")
		rating = float(soup.find(itemprop="ratingValue").string)
		isbn = soup.find(itemprop="isbn").string
		return (isbn, rating)
	except Exception as e:
		print(e)

def goodReadsSearchBook(title, author):
	endpoint = 'https://www.goodreads.com/book/title.xml'
	params = {'format': 'xml', 'key': Config.API_KEY, \
		'title': f"{title}", \
		'author':f"{author}"}
	req = requests.get(endpoint, params=params)
	time.sleep(1)
	data_dict = xmltodict.parse(req.content)
	gr = data_dict['GoodreadsResponse']
	rating = gr['book']['average_rating']
	return rating
	#print(g['book']['average_rating'])

if __name__ == "__main__":
	leaders = ["james altucher"]
	start_time = time.time()
	bf = Scraper.booksWithFreq(leaders)
	duration = time.time() - start_time
	print(bf)
	print(f"Downloaded {len([(item, f) for item, f in bf if item])} in {duration} seconds")