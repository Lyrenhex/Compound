#!/usr/bin/env python3

"""
Compound HTML Transclusion Compiler
Copyright (C) 2016  Damian Heaton <dh64784@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import bs4
import sys
import os

minify = False
nocomm = False

if "-m" in sys.argv or "--minify" in sys.argv:
    try:
        import htmlmin
        minify = True
    except ImportError as e:
        print("Minifying the output HTML requires the htmlmin module. \
Try run `pip3 install htmlmin` or `pip install htmlmin`.")

if "-c" in sys.argv or "--no-comments" in sys.argv:
    if minify:
        nocomm = True
    else:
        print("--no-comments flag requires the --minify flag to be set also.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""Compound should be used with syntax thus:
    compound <CHTML file> [any optional parameters (see docs)]""")
    else:
        files = []
        if ".c.html" in sys.argv[1]:
            files[0] = sys.argv[1]
        else:
            print("WARNING: CHTML input file does not contain '.c.html' in its \
name; are you sure that it's the correct format?")
            # no .c.html;  user likely specified a directory to build
            if os.path.isdir(sys.argv[1]):
                # it is a dir; we should go through the files and compile them
                # all.
                for f in os.listdir(sys.argv[1]):
                    if os.path.isfile(os.path.join(sys.argv[1], f)):
                        files.append(os.path.join(sys.argv[1], f))
        for f in files:
            output = ".".join(f.split(".")[:-2]).split("/")[-1] + ".html"
            if "-o" in sys.argv:
                output = sys.argv[sys.argv.index("-o") + 1]
            elif "--output" in sys.argv:
                output = sys.argv[sys.argv.index("--output") + 1]

            if "-b" in sys.argv:
                output = sys.argv[sys.argv.index("-b") + 1] + "/" + output
            elif "--build-dir" in sys.argv:
                output = sys.argv[sys.argv.index("-b") + 1] + "/" + output

            try:
                chtml = bs4.BeautifulSoup(open(f), "html.parser")

                # index all of the tags that we deal with
                transcludes = chtml.find_all("link", rel="transclusion")
                csslinks = chtml.find_all("link", rel="stylesheet")
                scriptlinks = chtml.find_all("script", src=True)

                for transclusion in transcludes:
                    try:
                        transclusion.replaceWith(bs4.BeautifulSoup(
                            open(transclusion["href"]), "html.parser"))
                    except IOError as e:
                        print("Transclusion failure: file %s could not be found\
 -- perhaps it's misspelt?" % transclusion["href"])
                        del transclusion
                    except Exception as e:
                        print("Transclusion failure:", e)

                if "--css" in sys.argv:
                    # css files
                    for cssfile in csslinks:
                        # create a new <style> tag to contain embedded css
                        csstag = chtml.new_tag("style")

                        # fill the <style> tag with the css
                        csstag.append(bs4.BeautifulSoup(open(cssfile["href"]),
                            "html.parser"))

                        # replace the link tag with the <style> tag
                        cssfile.replaceWith(csstag)

                if "--js" in sys.argv:
                    # script files
                    for scriptfile in scriptlinks:
                        # create a new <script> tag to contain embedded js
                        scripttag = chtml.new_tag("script")

                        # fill the <script> tag with the js
                        scripttag.append(bs4.BeautifulSoup(
                            open(scriptfile["src"]), "html.parser"))

                        # replace the link tag with the <script> tag
                        scriptfile.replaceWith(scripttag)

                if minify:
                    chtml = htmlmin.minify(str(chtml), remove_empty_space=True,
                        remove_comments=nocomm)

                    # TODO: if minify flag set, and -d (deep) flag is set, then 
                    # also transclude JS and CSS files into the base HTML file.
                    # (we really don't like external references ;))

                # save the new file
                f = open(output, "w")
                f.write(str(chtml))
                f.close()
                print("SUCCESS: Compiled to %s!" % output)
            except IOError as e:
                print("File %s could not be found -- are you sure you spelt it \
right?" % f)
            except Exception as e:
                print("Whoops, we couldn't compile the CHTML file. See error:",
                    e)
