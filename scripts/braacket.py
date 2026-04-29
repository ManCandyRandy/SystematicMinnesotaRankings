import requests
import lxml
import re
import cloudscraper as cs
import time
from dataclasses import dataclass
from bs4 import BeautifulSoup


SIZE = 50
REQUEST_DELAY_SECONDS = 0.5
CONNECT_TIMEOUT_SECONDS = 10
MAX_FETCH_ATTEMPTS = 5
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
USER_AGENT = (
  "Mozilla/5.0 (X11; Linux x86_64) "
  "AppleWebKit/537.36 (KHTML, like Gecko) "
  "Chrome/133.0.0.0 Safari/537.36"
)

@dataclass
class H2HSubset:
  col_names: list
  h2h_cells: list
  num_pages: int

@dataclass
class Player:
  name: str
  braacket_rank: int #braacket rank
  colley_rank: int
  colley_score: float
  colley_strength_of_schedule: float
  records: list

@dataclass
class Record:
  opponent: Player
  wins: int
  losses: int

#Record H2H record between opponents
def record_from_cell(cell, opponent):
    results = cell.split(" - ")
    return Record(opponent=opponent, wins=int(results[0]), losses=int(results[1]))

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

def _page_summary(soup):
  title = soup.title.get_text(" ", strip=True) if soup.title else ""
  header = soup.find("h1")
  header_text = header.get_text(" ", strip=True) if header else ""
  return " | ".join(part for part in [title, header_text] if part) or "no page title available"    

def fetch_page(url):
  last_error = None
  for attempt in range(1, MAX_FETCH_ATTEMPTS + 1):
    if attempt > 1:
      time.sleep(REQUEST_DELAY_SECONDS * attempt)

    try:
      response = session.get(url, timeout=(CONNECT_TIMEOUT_SECONDS, None))
    except requests.RequestException as exc:
      last_error = exc
      continue

    if response.status_code in RETRY_STATUS_CODES:
      last_error = requests.HTTPError(f"HTTP {response.status_code} for {url}")
      continue

    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    if soup.select_one("#league_stats_headtohead") and soup.select(".search-pagination .input-group-addon"):
      return soup

    last_error = ValueError(f"Unexpected Braacket page for {url}: {_page_summary(soup)}")

  raise RuntimeError(f"Unable to load Braacket head-to-head page after {MAX_FETCH_ATTEMPTS} attempts: {last_error}")

#Load up braacket URLs and start pulling the table together
def load_players(league_id, ranking_id):
    def get_h2h_subset(r, c):
        url = (f"https://braacket.com/league/{league_id}/head2head/{ranking_id}?rows={SIZE}&cols={SIZE}"
               +f"&page={r+1}&page_cols={c+1}&data=result&game_character=&country=&search=")
        soup = fetch_page(url)
        col_names = [n.text.strip() for n in soup.select("#league_stats_headtohead tbody th:nth-child(2)")]
        rows = soup.select("#league_stats_headtohead tbody tr")
        h2h_cells = [[t.text.strip() for t in r.select("td")] for r in rows]
        num_pages = int(re.sub("[^0-9]", "", soup.select(".search-pagination .input-group-addon")[-1].text))
        print("r")
        print(r)
        print("c")
        print(c)
        return H2HSubset(col_names=col_names, h2h_cells=h2h_cells, num_pages=num_pages)

    #Building the complete table going through the pages
    scraper = cs.create_scraper()
    origin = get_h2h_subset(0, 0)
    h2h = origin.h2h_cells
    player_names = origin.col_names
    pages = origin.num_pages
    for r in range(0, pages):
      for c in range(0, pages):
        if r == 0 and c == 0:
          continue
        subset = get_h2h_subset(r, c)
        if c == 0:
          player_names.extend(subset.col_names)
          h2h.extend(subset.h2h_cells)
        else:
          for subset_row in range(0, len(subset.h2h_cells)):
            h2h[r*SIZE + subset_row].extend(subset.h2h_cells[subset_row])

    # populate players from h2h matrix
    name_to_player = {}
    players = []
    for i, p in enumerate(player_names):
      player = Player(name=p, braacket_rank=i+1, records=[], colley_rank=0, colley_score=0, colley_strength_of_schedule=0)
      name_to_player[p] = player
      players.append(player)
    for y in range(len(h2h)):
      records = []
      for x in range(len(h2h)):
        if y == x:
          continue
        record = record_from_cell(h2h[y][x], name_to_player[player_names[x]])
        if record.wins + record.losses > 0:
          records.append(record)
      name_to_player[player_names[y]].records = records
    return players, name_to_player