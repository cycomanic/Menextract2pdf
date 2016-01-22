# Copyright 2016 Jochen Schröder
#
# This file is distributed under the terms of the
# GPLv3 licence. See the COPYING file for details

import sqlite3
from urllib import unquote
from urlparse import urlparse
import os
import pdfannotation
import PyPDF2
import warnings

HIGHLIGHTSQUERY = """SELECT Files.localUrl, FileHighlightRects.page,
                            FileHighlightRects.x1, FileHighlightRects.y1,
                            FileHighlightRects.x2, FileHighlightRects.y2
                    FROM Files
                    LEFT JOIN FileHighlights
                        ON FileHighlights.fileHash=Files.hash
                    LEFT JOIN FileHighlightRects
                        ON FileHighlightRects.highlightId=FileHighlights.id
                    WHERE FileHighlightRects.page IS NOT NULL"""

global OVERWRITE_PDFS
OVERWRITE_PDFS = False

def converturl2abspath(url):
    pth = unquote(str(urlparse(url).path)).decode("utf8") #this is necessary for filenames with unicode strings
    return os.path.abspath(pth)

def parse_query(res):
    highlights = {}
    for r in res:
        pth = converturl2abspath(r[0])
        bbox = [[r[2], r[3], r[4], r[5]]]
        pg = r[1]
        if pth in highlights:
            if pg in highlights[pth]:
                highlights[pth][pg].append(bbox)
            else:
                highlights[pth][pg] = [bbox]
        else:
            highlights[pth] = {pg: [bbox]}
    return highlights

def highlight_in_document(inpdf, outpdf, coords):
    for pg in coords.keys():
        inpg = inpdf.getPage(pg-1)
        for crd in coords[pg]:
            annot = pdfannotation.highlight_annotation(crd)
            pdfannotation.add_annotation(outpdf, inpg, annot)
        outpdf.addPage(inpg)
    return outpdf

def processpdf(fn, fn_out, coords):
    try:
        inpdf = PyPDF2.PdfFileReader(open(fn, 'rb'))
        if inpdf.isEncrypted:
            # PyPDF2 seems to think some files are encrypted even
            # if they are not. We just ignore the encryption.
            # This seems to work for the one file where I saw this issue
            inpdf._override_encryption = True
            inpdf._flatten()
    except IOError:
        print "Could not find pdffile %s"%fn
        return
    outpdf = PyPDF2.PdfFileWriter()
    outpdf = highlight_in_document(inpdf, outpdf, coords)
    if os.path.isfile(fn_out):
        if not OVERWRITE_PDFS:
            print "%s exists skipping"%fn_out
            return
        else:
            print "overwriting %s"%fn_out
    else:
        print "writing pdf to %s"%fn_out
    outpdf.write(open(fn_out, "wb"))

def mendeley2pdf(fn_db, dir_pdf):
    db = sqlite3.connect(fn_db)
    highlights = parse_query(db.execute(HIGHLIGHTSQUERY))
    for fn, locs in highlights.iteritems():
        processpdf(fn, os.path.join(dir_pdf, os.path.basename(fn)), locs)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mendeleydb", help="The mendeley sqlite database file",
                        type=str)
    parser.add_argument("dest", help="""The destination directory where to
                        save the annotated pdfs""", type=str)
    parser.add_argument("-w", "--overwrite", help="""Overwrite any PDF files in
                        the destination directory""", action="store_true")
    args = parser.parse_args()
    fn = os.path.abspath(args.mendeleydb)
    dir_pdf = os.path.abspath(args.dest)
    if args.overwrite:
        OVERWRITE_PDFS = True
    mendeley2pdf(fn, dir_pdf)






