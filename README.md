# wp2octopress.py

## License

Copyright (c) 2012 Mitch Lindgren

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## What is it?

wp2octopress.py is an ETL (extract, transform, load) script which will connect
to your Wordpress MySQL database and dump all of your posts and pages into
Octopress-compatible Markdown files. The primary purpose of the script is simply
to dump the posts into appropriately-named files with a reasonably correct
directory structure; very little processing is done on the actual post content
to ensure correct rendering.

Wordpress posts are stored internally as *mostly* HTML, although there are some
quirks - in particular, generally WordPress does not include `<br />`s or
`<p>`s;
those seem to be added when the page is output. This HTML format is basically
what you'll get in your dumped posts. There is a function called
`fix_post_content` which does a couple things to clean up posts and try to make
them render nicely in Octopress:

- `\r\n` newlines are replaced with just `\n`
- `[sourcecode]` tags are replaced with their Octopress equivalent

If you want to do additional automated cleanup, just edit that function and add
whatever you'd like. If you add something useful, please send me a pull request
so that others can benefit from it!

## Dependencies

`wp2octopress.py` depends on [SQLAlchemy](http://www.sqlalchemy.org/). You can
[install it](http://docs.sqlalchemy.org/en/rel_0_7/intro.html#install-via-easy-install-or-pip)
easily via `pip` (`pip install SQLAlchemy`) or `easy_install` (`easy_install
SQLAlchemy`).

## Things to watch for in output

In general I've found that Octopress does a good job of rendering the posts
directly from the Wordpress HTML, which is why I didn't put much effort into
fixing up the content.  However, there are a few things to watch out for.

- Complex nested structures may not render correctly. In particular, I've
  noticed that `<code>` blocks and `<blockquotes>` within `<li>`s can look
  messy.
- This script replaces `[sourcecode]` blocks, but not `<code>` blocks. This is
  generally okay since inline code in Markdown converts to `<code>` blocks
  anyway, but if you have a lot of inline code you should check that everything
  looks right.
- Separate lines of text with only one line break rather than two will render as
  one paragraph.
- This script doesn't replace HTML entities (e.g. `&amp;`) with their
  corresponding characters.  HTML entities within `[sourcecode]` or `[code]`
  blocks will be rendered literally.
- Sometimes Wordpress seems to insert extra `<br />`s for no apparent reason.

## Usage

Just run `./wp2octopress.py db host username password posts_dir pages_dir`.
