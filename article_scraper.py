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
	authors = authors.splitlines()
	authors = authors[2:len(authors)-1]
	authors = [re.sub('<.*?>','', author) for author in authors]
	authors = [author.replace(",", "") for author in authors]
	authors = [author.rstrip() for author in authors]
	return authors

def get_abstract(meta_element):
	meta_text = meta_element.find('p')
	abstract = "Does not exist. Propably a replacement."
	if meta_text is not None:
		abstract = meta_element.find('p').getText()
	return abstract


url = "https://arxiv.org/list/quant-ph/new"

page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")
metas = soup.select(".meta")
selected_authors = []
selected_keywords = []

with open('selected_authors.txt') as f:
    lines = [selected_authors.append(line.rstrip()) for line in f]
    #selected_authors.append(lines)
with open('selected_keywords.txt') as f:
    lines = [selected_keywords.append(line.rstrip()) for line in f]





intersting_papers = []
is_paper_interesting = False

dl_data = soup.find_all(['dd', 'dt'])

link_data = dl_data[0::2]
meta_data = dl_data[1::2]



for link, meta in zip(link_data, meta_data):
	is_paper_interesting = False
	authors = get_author_list(meta)
	title = get_title(meta)
	abstract = get_abstract(meta) 
	
	for author in authors:
		if any(s in author for s in selected_authors):
			is_paper_interesting = True

	if any(sub in title for sub in selected_keywords):
		is_paper_interesting = True

	if any(sub in abstract for sub in selected_keywords):
		is_paper_interesting = True
		

	if is_paper_interesting:
		link = link.find_all(href = True)[0]
		dictionary = {
			"title"   : title,
			"authors" : authors,
			"abstract": abstract,
			"link"	  : link
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
	link 	 = paper.get('link') 
	link 	 = str(link)
	link     = link[0:9] + "https://arxiv.org/" + link[10:]

	body += "<html>"
	body += "<body>"
	body += "<h2> Title: " + title + "</h2>" 
	body += "<h4> Link: " + str(link) + "</h4>"
	body += "<h3> Authors: " + str([author for author in authors])[1:-1].replace("'", "") + "</h3>"
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








