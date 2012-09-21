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

from sqlalchemy import create_engine, MetaData, Table

USAGE = 'USAGE: {0} db host username password output_dir'
WP_COMMENTS = {'closed' : 'false', 'open' : 'true'}
WP_PUBLISH = {'draft' : 'false', 'auto-draft' : 'false', 'publish' : 'true'}

def dump_posts(db, host, username, password, output_dir):
    """
    Connects to the database and dumps the posts.
    """

    try:
        os.mkdir(output_dir)
    except OSError:
        pass

    db = create_engine('mysql://{0}:{1}@{2}/{3}?charset=utf8'\
                       .format(username, password, host, db))
    metadata = MetaData(db)
    wp_posts = Table('wp_posts', metadata, autoload=True)

    posts_statement = wp_posts.select(wp_posts.c.post_type == 'post')
    result = posts_statement.execute()

    for post in result:
        filename = '{0}-{1}-{2}-{3}.markdown'\
                   .format(post.post_date.year, 
			   str(post.post_date.month).zfill(2),
                           str(post.post_date.day).zfill(2),
                           post.post_name)
        output = codecs.open(os.path.join(output_dir, filename), 
                             encoding='utf-8', mode='w')

        output_params = (post.post_title,
			 str(post.post_date)[:-3],
			 WP_COMMENTS[post.comment_status],
			 '', # TODO: Add categories
			 WP_PUBLISH[post.post_status],
			 post.post_content.replace('\r\n', '\n'))
        
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
