import re
import json
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from pathlib import Path


blog_page = requests.get('https://www.alexwest.co/blogs')
blog_soup = BeautifulSoup(blog_page.content, 'html.parser')
blog_post_links = blog_soup.find_all('a', href=re.compile(r'^/posts/\d+$'))


def get_blog_post(blog_post_url):
    blog_post_page = requests.get(f'https://www.alexwest.co{blog_post_url}')
    blog_post_soup = BeautifulSoup(blog_post_page.content, 'html.parser')
    blog_post_title = blog_post_soup.find('p').get_text()
    blog_post_text = blog_post_soup.find('pre').get_text()
    blog_post = {
        'title': blog_post_title,
        'text': blog_post_text,
    }
    return blog_post
    



blog_posts_cache_file = Path('blog_posts.json')

if not blog_posts_cache_file.exists():
    blog_posts = [get_blog_post(blog_post_link['href']) for blog_post_link in tqdm(blog_post_links)]
    # They're sorted from newest to oldest
    # Reorder to be oldest to newest
    blog_posts = reversed(blog_posts)
    with blog_posts_cache_file.open('w') as f:
        json.dump(list(blog_posts), f)
else:
    with blog_posts_cache_file.open('r') as f:
        blog_posts = json.load(f)


# -------------------------------------------------------------------------
# Append all blog posts to single html
# -------------------------------------------------------------------------
blogs_book = BeautifulSoup()

for blog_post in blog_posts:
    blog_post_title_div = blogs_book.new_tag('h1')
    blog_post_title_div.string = blog_post['title']
    blog_post_text_div = blogs_book.new_tag('pre')
    blog_post_text_div.string = blog_post['text']
    _ = blogs_book.append(blog_post_title_div)
    _ = blogs_book.append(blog_post_text_div)


html_output_file = Path('blogs_book.html')
with html_output_file.open('w', encoding='utf-8') as f:
    f.write(str(blogs_book))
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# Convert html to epub
# -------------------------------------------------------------------------
from datetime import datetime
timestamp_str = datetime.now().strftime('%Y%m%d')

epub_output_file = Path('alex_west_raw_blogs.epub')
import pypandoc
output = pypandoc.convert_file(
    html_output_file, 
    'epub', 
    extra_args=[
        f'--metadata=title=Daily Blogs ({timestamp_str})',
        '--metadata=author=Alex West',
    ],
    outputfile=epub_output_file,
)
# -------------------------------------------------------------------------

