import requests
import lxml
import cloudscraper as cs
from bs4 import BeautifulSoup

# I currently do not have this looped since I'm working out of a jupyter notebook. I am going to set a loop at the beginning for, "while true" 
# and then set it to false when next page is disabled

base_url = "https://braacket.com"
current_url = "https://braacket.com/league/MNMelee2025/head2head/ACC72DC6-D830-4DD2-A1AD-5D516521DBA6?rows=50&cols=15&page=1&page_cols=1&data=result&game_character=&country=&search=&cols=50"

scraper = cs.create_scraper()

html = requests.get(current_url).text
soup = BeautifulSoup(html, 'lxml')

table = soup.find('div', {'id': 'league_stats_headtohead'})

body = table.find('tbody')
hNames = body.find_all('a')

names = []

for name in hNames:
  names.append(name.text.replace('\t', '').replace('\n', ''))

next_page_button = soup.select_one("a:has(i.fa-chevron-right)")  

if not next_page_button or next_page_button.has_attr("disabled"):
    print("no more pages")

print(names)
print(len(names))