import requests
import lxml
from bs4 import BeautifulSoup

html = requests.get('https://braacket.com/league/MNMelee2025/head2head/ACC72DC6-D830-4DD2-A1AD-5D516521DBA6?rows=15&cols=15&page=1&page_cols=1&data=result&game_character=&country=&search=').text
soup = BeautifulSoup(html, 'lxml')

table = soup.find('div', {'id': 'league_stats_headtohead'})

body = table.find('tbody')
hNames = body.find_all('a')

names = []

for name in hNames:
  names.append(name.text.replace('\t', '').replace('\n', ''))

print(names)