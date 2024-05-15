from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_title(meta_element):
	title = meta_element.select(".list-title")
	title = re.sub( '<.*?>' ,'', str(title).splitlines()[1] )
	title = title[7:]

	return title

def get_author_list(meta_element):
	authors = meta_element.select(".list-authors")
	authors = str(authors)

	print(authors)
	authors = authors.replace(',+', '')
	print(authors)
	authors = authors.split(', ')
	print(authors)		
	# authors = authors[0:len(authors)-1]
	print(authors)
	authors = [re.sub('<.*?>','', author) for author in authors]
	print(len(authors))
	# authors = [author.replace(",", "") for author in authors]
	authors = [author.rstrip() for author in authors]
	return authors

def get_abstract(meta_element):
	meta_text = meta_element.find('p')
	abstract = "Does not exist. Propably a replacement."
	if meta_text is not None:
		abstract = meta_element.find('p').getText()
	return abstract


urls = ["https://arxiv.org/list/quant-ph/new"]


selected_authors = []
selected_keywords = []

with open('selected_authors.txt') as f:
    lines = [selected_authors.append(line.rstrip()) for line in f]
    #selected_authors.append(lines)
with open('selected_keywords.txt') as f:
    lines = [selected_keywords.append(line.rstrip()) for line in f]


intersting_papers = []
is_paper_interesting = False

for url in urls:
	page = urlopen(url)
	html = page.read().decode("utf-8")
	soup = BeautifulSoup(html, "html.parser")
	metas = soup.select(".meta")




	dl_data = soup.find_all(['dd', 'dt'])

	link_data = dl_data[0::2]
	meta_data = dl_data[1::2]

	# print(meta_data)
	# link_data = link_data[0:1]
	# meta_data = meta_data[0:1]


	for link, meta in zip(link_data, meta_data):
		is_paper_interesting = False
		match_conditions = []
		# print("")
		# print("Meta")
		# print(meta)
		authors = get_author_list(meta)
		title = get_title(meta)
		abstract = get_abstract(meta) 
		
		# print("Tests")
		# tests = meta.select(".list-authors")
		# print(tests)
		# print("Tests end")

		for author in authors:
			if any(s in author for s in selected_authors):
				is_paper_interesting = True
				match_conditions.append("Author,")

		if any(sub in title for sub in selected_keywords):
			is_paper_interesting = True
			match_conditions.append("Title,")

		if any(sub in abstract for sub in selected_keywords):
			is_paper_interesting = True
			match_conditions.append('Abstract,')
			

		if is_paper_interesting:
			link = link.find_all(href = True)[0]
			dictionary = {
				"title"   : title,
				"authors" : authors,
				"abstract": abstract,
				"link"	  : link,
				"match"	  : match_conditions
			}

			intersting_papers.append(dictionary)


sender_email = "utrafastarxivscraper@gmail.com"
sender_password = "ywhf biny immg edso"
recipient_email = "christianlange@phys.au.dk"

subject = "Interesting papers from arXiv"

body = """\
<html>
	<h2>
		Hello there! <br> 
	</h3>
	<body>
		<p>
			I found these papers, that might be of interest on arXiv today. <br> <br>
		</p>
	</body>
	<hr>
</html>
"""


for paper in intersting_papers:
	title    = paper.get('title')
	authors  = paper.get('authors')
	abstract = paper.get('abstract')
	match_conditions = paper.get('match')
	seperator = ' ,'
	match_string = seperator.join(match_conditions) 
	match_string = match_string[:-1]
	link 	 = paper.get('link') 
	link 	 = str(link)
	link     = link[0:9] + "https://arxiv.org/" + link[10:]

	body += "<html>"
	body += "<body>"
	body += "<h2> Title: " + title + "</h2>" 
	body += "<h4> Link: " + str(link) + "</h4>"
	body += "<h4> Matched on: " + str(match_string) + "</h4>"		
	body += "<h3> Authors: " + str([author for author in authors])[1:-1].replace("'", "").replace("[", "").replace("]", "") + "</h3>"
	body += "<p class = 'mathjax'><b>Abstract:</b> " + abstract + "</p>"
	body += "<br>"
	body += "</body>"
	body += "<hr>"		
	body += "</html>"


body += """
<html>
	<body> 
		<p>
			Have a great day!
			<br>
		</p>
		<p>
			Contact Christian Lange (christianlange@phys.au.dk) if you have any comments or suggestions for improvement.
		</p>
	</body>
</html>
"""

message = MIMEText(body, 'html')

message['Subject'] = subject
message['To'] = recipient_email
message['From'] = sender_email

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
   server.login(sender_email, sender_password)
   server.sendmail(sender_email, recipient_email, message.as_string())

print("Email sent!")








