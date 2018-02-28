#! /usr/local/bin/python3

"""Minimal python link-dump blog script"""

import configparser
import datetime as dt
import errno
import os
import shutil
from collections import namedtuple, defaultdict
from textwrap import dedent
from typing import Tuple, Dict, List, Iterator
from functools import lru_cache

OUTPUT_DIR = 'output'
POST_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'posts')
ASSET_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'assets')
TAGS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'tags')
POSTS_DIR = 'posts'
ASSET_DIR = 'assets'
TEMPLATES_DIR = 'templates'

MONTH_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, 'month_template.html')
POST_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, 'post_template.html')
TAG_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, 'tag_template.html')

Post = namedtuple('Post', ['title', 'description', 'link', 'tags', 'comment', 'name'])


def main():
    create_output_dirs()
    copy_assets()
    new_posts = [name for name, timestamp
                 in post_names_with_timestamps()
                 if is_new_post(name, timestamp)]
    write_posts_files(new_posts)
    updated_months = [path[0:7] for path in new_posts]
    write_monthly_overview_files(updated_months)
    if updated_months:
        copy_last_month_to_index(sorted(updated_months)[0])
    write_tag_pages(post_names_with_timestamps())


def write_posts_files(new_posts):
    for name in new_posts:
        print(f'Generating new post HTML: {name.replace(".ini",".html")}')
        write_post_file(name)


def write_post_file(name: str):
    html = generate_post_html(name)
    html_file_name = name.replace('.ini', '.html')
    html_output_file_path = os.path.join(POST_OUTPUT_DIR, html_file_name)
    with open(html_output_file_path, 'w') as output_html_file:
        output_html_file.write(html)


def write_monthly_overview_files(months: List[str]):
    for month in months:
        write_monthly_overview_file(month)


def write_monthly_overview_file(month: str):
    html = generate_month_html(month)
    overview_file_path = os.path.join(OUTPUT_DIR, f'{month}.html')
    with open(overview_file_path, 'w') as output_html_file:
        output_html_file.write(html)


def write_tag_pages(post_names_timestamps: Iterator[Tuple[str, float]]):
    mapping = tag_post_mapping(post_names_timestamps)
    for item in mapping.items():
        write_tag_page(*item)


def write_tag_page(tag, pages):
    html = template(TAG_TEMPLATE_FILE)
    posts = (read_post(page.replace('.html', '.ini')) for page in pages)
    posts_html = (f'<a href="{post.name}">{post.title}</a>' for post in posts)
    tag_html = html.format(tag=tag, posts='\n'.join(posts_html))
    with open(os.path.join(TAGS_OUTPUT_DIR, f'{tag}.html'), 'w') as out_file:
        out_file.write(tag_html)


@lru_cache(maxsize=10)
def template(file: str) -> str:
    with open(file) as template_file:
        return template_file.read()


def tag_post_mapping(post_names_timestamps: Iterator[Tuple[str, float]]) -> Dict[str, List]:
    posts = (read_post(name) for name, _ in post_names_timestamps)
    tags_with_post_names = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            tags_with_post_names[tag].append(post.name)
    return tags_with_post_names


def copy_last_month_to_index(month):
    shutil.copy2(os.path.join(OUTPUT_DIR, f'{month}.html'), os.path.join(OUTPUT_DIR, 'index.html'))


def generate_month_html(month):
    first_of_month = dt.datetime.strptime(month, '%Y-%m')
    month_name = first_of_month.strftime('%B %Y')
    one_day = dt.timedelta(days=1)
    last_month = f'{(first_of_month - one_day).strftime("%Y-%m")}.html'
    posts_html = map(generate_post_in_month_html, posts_in_month(month))

    html = template(MONTH_TEMPLATE_FILE)
    return html.format(month=month_name, posts=''.join(posts_html), previous=last_month)


def generate_post_in_month_html(post):
    comment = f'<p class="hug comment"> {post.comment}</p>' if post.comment else ''
    post_html = f'''
            <h3>{post.title} <a href="posts/{post.name}">→</a></h3>
            <p class="hug">{post.description}</p>
            {comment}
            <a href="{post.link}">{post.link}</a>
            
            '''
    return dedent(post_html)


def posts_in_month(month):
    file_names = os.listdir(POSTS_DIR)
    files_in_month = (file_name for file_name in file_names if file_name.startswith(month))
    posts = map(read_post, sorted(files_in_month, reverse=True))
    return posts


def is_new_post(ini_file_name, ini_file_timestamp):
    html_file_name = ini_file_name.replace('.ini', '.html')
    html_file_path = os.path.join(POST_OUTPUT_DIR, html_file_name)
    try:
        html_file_timestamp = os.stat(html_file_path).st_mtime
        return ini_file_timestamp > html_file_timestamp
    except FileNotFoundError:
        return True


def post_names_with_timestamps() -> (str, float):
    file_names = os.listdir(POSTS_DIR)
    file_paths = [os.path.join(POSTS_DIR, file_name) for file_name in file_names]
    file_infos = map(os.stat, file_paths)
    modification_times = map(lambda stat: stat.st_mtime, file_infos)
    return zip(file_names, modification_times)


def generate_post_html(name: str) -> str:
    post = read_post(name)
    html = template(POST_TEMPLATE_FILE)
    li_tags = [f'<li><a href="../tags/{tag}.html">{tag}</a></li>' for tag in post.tags]
    tag_list = '\n'.join(li_tags)
    comment = f'<p class="hug comment"> {post.comment}</p>' if post.comment else ''
    meta_tags = [f'<meta property="article:tag" content="{tag}"/>' for tag in post.tags]
    meta_video = video_meta_for_link(post.link)
    meta_image = image_meta_for_link(post.link)
    return html.format(title=post.title, description=post.description,
                       link=post.link, tags=tag_list, comment=comment, meta_tags="\n".join(meta_tags),
                       meta_video=meta_video, meta_image=meta_image)


def image_meta_for_link(link: str):
    if link.startswith('https://www.youtube.com/watch?v='):
        return f'<meta property="og:image" content="https://img.youtube.com/vi/{link.split("=")[1]}/hqdefault.jpg" />'
    return ''


def video_meta_for_link(link: str):
    if link.startswith('https://www.youtube.com/watch?v='):
        return f'<meta property="og:video" content="https://www.youtube.com/v/{link.split("=")[1]}" />'
    return ''


@lru_cache(maxsize=100)
def read_post(name):
    post = configparser.ConfigParser()
    post.read(os.path.join(POSTS_DIR, name))
    title = post.sections()[0]
    description = post[title]['description']
    link = post[title]['link']
    tags = [s.strip() for s in post[title]['tags'].split(',')]
    comment = post[title]['comment'] if 'comment' in post[title] else None
    return Post(title=title, description=description, link=link, tags=tags, comment=comment,
                name=name.replace('.ini', '.html'))


def create_output_dirs():
    create_dir_if_needed(POSTS_DIR)
    create_dir_if_needed(ASSET_DIR)
    create_dir_if_needed(POST_OUTPUT_DIR)
    create_dir_if_needed(TAGS_OUTPUT_DIR)
    create_dir_if_needed(ASSET_OUTPUT_DIR)


def create_dir_if_needed(dir_path):
    try:
        os.makedirs(dir_path)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise


def copy_assets():
    shutil.rmtree(ASSET_OUTPUT_DIR, ignore_errors=True)
    shutil.copytree(ASSET_DIR, ASSET_OUTPUT_DIR)


if __name__ == "__main__":
    main()
