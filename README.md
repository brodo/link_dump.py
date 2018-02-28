# link_dump.py

This is a static site generator in ~200 LOC for 'link heavy', minimalistic blogs like [fefes blog](https://blog.fefe.de).

## Installation

Clone this repo and modify the templates in `templates` to your liking. Add assets to `assets`.

## Writing Blog Posts

1. Create a directory called `posts` in the same folder where `link_dump.py` is located.
2. Create an `ini` file with a filename like this: `YYYY-MM-DD_Post-title.ini`, e.g. `2018-02-10_My-Blogpost.ini`
3. Add the following content:
    ```ini    
    [Post Title]
    link: https://example.com
    description: Description of the link. I try to keep it neutral or use a description already provided.
    comment: Something which is a personal comment about the link (OPTIONAL)
    tags: comma, seperaged, tag list
    ``` 

4. Run `link_dump.py` - this will create or update a directory called `output` in `linkdump.py`s working folder.


## Managing your blog with git

I recommend putting your `output` and `posts` subdirectories in their own git submodules.


## License

Copyright 2018 Julian Dax

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 