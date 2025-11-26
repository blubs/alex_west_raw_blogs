import re
import json
import hashlib
import requests
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup


last_hash_file = Path('last_hash.txt')
last_hash = None
if last_hash_file.exists():
    with last_hash_file.open('r') as f:
        last_hash = f.read()


blog_page = requests.get('https://www.alexwest.co/blogs')
blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
blog_post_links = blog_soup.find_all('a', href=re.compile(r'^/posts/\d+$'))
blog_post_hrefs = [blog_post_link['href'] for blog_post_link in blog_post_links]
blog_posts_checksum = hashlib.sha256(json.dumps(list(sorted(blog_post_hrefs))).encode()).hexdigest()


print('---------------------------')
print('Checking for blog post updates:')
print('Prior hash:', last_hash)
print('Cur hash:', blog_posts_checksum)
print('---------------------------')


# If hashes equivalent, skip
if blog_posts_checksum == last_hash:
    print('No new blog posts')
    exit(1)
    
    
# Otherwise, update the hash file
with last_hash_file.open('w') as f:
    f.write(blog_posts_checksum)

exit(0)