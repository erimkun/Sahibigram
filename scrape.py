import requests, urllib.parse

API_KEY = "291fbb18b5cf7ac37bb95da0f498d259"
username = (
    "render=true"
    "&wait_for_selector=tr.searchResultsItem"
    "&follow_redirect=false"
    "&premium=true"                 # or ultra_premium=true
)

proxy = f"http://{username}:{API_KEY}@proxy-server.scraperapi.com:8001"

proxies = {"http": proxy, "https": proxy}

r = requests.get(
    "https://www.sahibinden.com/kiralik-daire?page=1",
    proxies=proxies,
    timeout=120,
)
r.raise_for_status()
print(r.text[:1000])      # show first 1 KB of HTML
