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

minify = False
nocomm = False

if "-m" in sys.argv or "--minify" in sys.argv:
    try:
        import htmlmin
        minify = True
    except ImportError as e:
        print("Minifying the output HTML requires the htmlmin module. Try run `pip3 install htmlmin` or `pip install htmlmin`.")

if "-c" in sys.argv or "--no-comments" in sys.argv:
    if minify:
        nocomm = True
    else:
        print("--no-comments flag requires the --minify flag to be set also.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""Compound should be used with syntax thus:
    python(3) main.py <CHTML file> [any optional parameters (see docs)]""")
    else:
        output = ".".join(sys.argv[1].split(".")[:-2]) + ".html"
        if "-o" in sys.argv:
            output = sys.argv[sys.argv.index("-o") + 1]
        elif "--output" in sys.argv:
            output = sys.argv[sys.argv.index("--output") + 1]
        try:
            if(".c.html" not in sys.argv[1]):
                print("WARNING: CHTML input file does not contain '.c.html' in its name; are you sure that it's the correct format?")
            chtml = bs4.BeautifulSoup(open(sys.argv[1]), "html.parser")
            transcludes = chtml.find_all("link", rel="transclusion")
            for transclusion in transcludes:
                try:
                    transclusion.replaceWith(bs4.BeautifulSoup(open(transclusion["href"])))
                except IOError as e:
                    print("Transclusion failure: file %s could not be found -- perhaps it's misspelt?" % transclusion["href"])
                    del transclusion
                except Exception as e:
                    print("Transclusion failure:", e)

            if minify:
                chtml = htmlmin.minify(str(chtml), remove_empty_space=True, remove_comments=nocomm)

                # TODO: if minify flag set, and -d (deep) flag is set, then also transclude JS and CSS files into the base HTML file. (we really don't like external references ;))

            # save the new file
            f = open(output, "w")
            f.write(str(chtml))
            f.close()
            print("SUCCESS: Compiled to %s!" % output)
        except IOError as e:
            print("File %s could not be found -- are you sure you spelt it right?" % sys.argv[1])
        except Exception as e:
            print("Whoops, we couldn't compile the CHTML file. See error:", e)
