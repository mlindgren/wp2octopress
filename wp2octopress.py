#!/bin/env python
# -*- coding: utf-8 -*-
"""
This script extracts posts from a WordPress database and spits out Octopress-
compatible markdown files.
"""

from __future__ import unicode_literals
import sys
import os
import codecs
import re

from sqlalchemy import create_engine, MetaData, Table, or_, and_

USAGE = 'USAGE: {0} db host username password posts_dir pages_dir'
WP_COMMENTS = {'closed' : 'false', 'open' : 'true'}
WP_PUBLISH = {'draft' : 'false', 'auto-draft' : 'false', 'publish' : 'true'}

missing_name_count = 0

def fix_post_content(post_content):
    """
    This function does modifies post content to work better with Octopress
    so that you'll hopefully not have to do as much manual editing. Put
    whatever regexes and whatnot you want in here.
    """

    post_content = post_content.replace('\r\n', '\n')

    # Replace syntax highlighter blocks with Octopress equivalent
    post_content = re.sub('\[sourcecode language="([A-Za-z0-9]+)"\]',
                          '``` \\1',
                          post_content)
    post_content = re.sub('\[/sourcecode\]', '', post_content)

    return post_content

def missing_name_check(post):
    """
    Returns a valid name in case of pages and posts that are missing a
    name (which can happen with drafts and such).
    """

    # Globals are bad but I'm lazy and this is an ETL
    global missing_name_count

    if post.post_name.lstrip().rstrip() == '':
        name = ''.join([char for char in post.post_title.replace(' ', '-')
                        if char.isalnum() or char == '-'])
        if name.lstrip().rstrip() == '':
            name = 'missing-name-' + str(missing_name_count)
            missing_name_count += 1
        sys.stderr.write(
        "Warning: page/post {0} (ID {1}) has no name. Using name {2}\n"\
        .format(post.post_title, post.id, name))
    else:
        name = post.post_name

    return name

def dump_single_page(page, output_dir):
    """
    Dumps a single page.  Doesn't handle parent-child relationships between
    pages, sorry. You can just mv all the children into a subdirectory or
    whatever you want to do.
    """

    page_name = missing_name_check(page)

    subpath = os.path.join(output_dir, page_name)
    os.mkdir(subpath)
    path = os.path.join(subpath, 'index.markdown')
    output = codecs.open(path, encoding='utf-8', mode='w')

    output_params = (page.post_title,
                     str(page.post_date)[:-3],
                     WP_COMMENTS[page.comment_status],
                     fix_post_content(page.post_content))

    output.write(
"""---
layout: page
title: "{0}"
date: {1}
comments: {2}
sharing: true
footer: true
---
{3}
""".format(*output_params))
    output.close()

def dump_single_post(post, post_categories, output_dir):
    """
    Dumps a single post (as opposed to a single page)
    """

    post_name = missing_name_check(post)

    filename = '{0}-{1}-{2}-{3}.markdown'\
               .format(post.post_date.year, 
                       str(post.post_date.month).zfill(2),
                       str(post.post_date.day).zfill(2),
                       post_name)
    output = codecs.open(os.path.join(output_dir, filename), 
                         encoding='utf-8', mode='w')

    output_params = (post.post_title,
         str(post.post_date)[:-3],
         WP_COMMENTS[post.comment_status],
         ', '.join(post_categories.get(post.id) or []),
         WP_PUBLISH[post.post_status],
         fix_post_content(post.post_content))

    output.write(
"""---
layout: post
title: "{0}"
date: {1}
comments: {2}
external-url:
categories: [{3}]
published: {4}
---
{5}
""".format(*output_params))
    output.close()


def dump_posts(db, host, username, password, posts_output_dir,
               pages_output_dir):
    """
    Connects to the database and dumps the posts.
    """

    try:
        os.mkdir(posts_output_dir)
        os.mkdir(pages_output_dir)
    except OSError:
        pass

    db = create_engine('mysql://{0}:{1}@{2}/{3}?charset=utf8'\
                       .format(username, password, host, db))
    metadata = MetaData(db)
    wp_posts = Table('wp_posts', metadata, autoload=True)

    # Before we select posts, we'll select all of the categories for the posts
    # so that we can map them later. This is a lazy and inefficient way to go
    # about this; a direct join in the posts select would be better. However,
    # the wp_term_relationships table does not have a proper foreign key
    # relationship between terms and the objects they relate to, so I don't
    # think SQLAlchemy can handle the join in declarative fashion.
    # Anyway, this is a one-off script so I'm not going to go to the trouble
    # of figuring out the "right" way to do this in SQLAlchemy. Just be
    # warned that you should not use this as an example.
    category_result = db.execute("""
    select object_id, name from wp_term_taxonomy 
    inner join wp_terms using(term_id)
    inner join wp_term_relationships using(term_taxonomy_id)
    inner join wp_posts on wp_posts.id = object_id
    where taxonomy = 'category' and post_type='post' and post_status!='inherit'
    """)
    post_categories = {}
    for row in category_result:
        if not post_categories.get(row[0]):
            post_categories[row[0]] = [row[1]]
        else:
            post_categories[row[0]].append(row[1])

    posts_statement = wp_posts.select(and_(
                                      or_(wp_posts.c.post_type == 'post',
                                          wp_posts.c.post_type == 'page'),
                                      wp_posts.c.post_status != 'auto-draft'))
    result = posts_statement.execute()

    for post in result:
        if post.post_type == 'post':
            dump_single_post(post, post_categories, posts_output_dir)
        elif post.post_type == 'page':
            dump_single_page(post, pages_output_dir)

def main():
    """
    Script entry point
    """

    if len(sys.argv) < 6:
        print USAGE.format(sys.argv[0])
        return 0

    dump_posts(*sys.argv[1:])

if __name__ == "__main__":
    main()
