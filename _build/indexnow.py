#!/usr/bin/env python3
"""Submit every sitemap URL (or the URLs given) to IndexNow (Bing, Yandex, Seznam, Naver...). Run after publishing."""
import json, re, sys, urllib.request
import glob, os
# The IndexNow key is public by design: it is the name and content of the <key>.txt file at the site root.
KEY = next(os.path.basename(f)[:-4] for f in glob.glob("[0-9a-f]"*32 + ".txt"))
urls = sys.argv[1:] or re.findall(r"<loc>([^<]+)</loc>", open("sitemap.xml").read())
body = json.dumps({"host": "marginmail.ai", "key": KEY, "keyLocation": f"https://marginmail.ai/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", body, {"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req) as r:
    print(r.status, len(urls), "URLs submitted")
