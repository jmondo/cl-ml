from craigslist import CraigslistHousing, requests_get
import json
import datetime
from bs4 import BeautifulSoup
import os

def get_more_data(self, result):
  response = requests_get(result['url'], logger=self.logger)
  self.logger.info('GET %s', response.url)
  self.logger.info('Response code: %s', response.status_code)

  if response.ok:
    soup = BeautifulSoup(response.content, 'html.parser')

    if result['has_map']:
      map = soup.find('div', {'id': 'map'})
      if map:
          result['geotag'] = (float(map.attrs['data-latitude']),
                              float(map.attrs['data-longitude']))

  result['other_tags'] = []
  # result['open_house_dates'] = []
  result['thumb_count'] = len(soup.select('#thumbs img'))
  result['body'] = str(soup.find(id='postingbody'))
  result['address'] = soup.find(class_='mapaddress') and soup.find(class_='mapaddress').text

  # todo add open house dates https://sfbay.craigslist.org/sfc/apa/6133484682.html
  for span in soup.select('.attrgroup span'):
    if 'BR ' in span.text:
      result['beds'], result['baths'] = span.text.split(' / ')
    # elif "&sale_date=" in span.__str__():
    #   result['open_house_dates'].append(span.text.split(' ')[-1])
    elif "ft<sup>2" in span.__str__():
      result['size'] = span.text
    elif "housing_movein_now" in span.__str__():
      result['move_in_date'] = span['data-date']
    elif span.text in legit_types:
      result['housing_type'] = span.text
    elif span.text in legit_laundries:
      result['laundry'] = span.text
    else:
      result['other_tags'].append(span.text)

  return result

CraigslistHousing.geotag_result = get_more_data

# legit_hoods = Set([
#   "alamo square / nopa",
#   "bayview",
#   "bernal heights",
#   "castro / upper market",
#   "cole valley / ashbury hts",
#   "downtown / civic / van ness",
#   "excelsior / outer mission",
#   "financial district",
#   "glen park",
#   "haight ashbury",
#   "hayes valley",
#   "ingleside / SFSU / CCSF",
#   "inner richmond",
#   "inner sunset / UCSF",
#   "laurel hts / presidio",
#   "lower haight",
#   "lower nob hill",
#   "lower pac hts",
#   "marina / cow hollow",
#   "mission district",
#   "nob hill",
#   "noe valley",
#   "north beach / telegraph hill",
#   "pacific heights",
#   "portola district",
#   "potrero hill",
#   "richmond / seacliff",
#   "russian hill",
#   "SOMA / south beach",
#   "sunset / parkside",
#   "tenderloin",
#   "treasure island",
#   "twin peaks / diamond hts",
#   "USF / panhandle",
#   "visitacion valley",
#   "west portal / forest hill",
#   "western addition"
# ])

legit_types = set([
  "apartment",
  "condo",
  "cottage/cabin",
  "duplex",
  "flat",
  "house",
  "in-law",
  "loft",
  "townhouse",
  "manufactured",
  "assisted living",
  "land",
])

legit_laundries = set([
  "w/d in unit",
  "w/d hookups",
  "laundry in bldg",
  "laundry on site",
  "no laundry on site"
])

legit_parkings = set([
  "carport",
  "attached garage",
  "detached garage",
  "off-street parking",
  "street parking",
  "valet parking",
  "no parking"
])

cl_h = CraigslistHousing(site=os.environ['SITE'], area=os.environ['AREA'], category=os.environ['CATEGORY'],
                         filters={'has_image': 1})

results = []

try:
  for result in cl_h.get_results(sort_by='newest', geotagged='true'):
    results.append(result)
    print(result['url'])
# If anything goes wrong, including me killing the script, it will print all the results it has
finally:
  time = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
  f = open('/data/' + time + '.json', 'w')
  f.write(json.dumps(results, sort_keys=True,
                              indent=2,
                              separators=(',', ': ')))

