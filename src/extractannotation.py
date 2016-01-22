import sqlite3
#import popplerqt4
#import PyQt4
#from urllib.parse import urlparse, unquote
from urllib import unquote
from urlparse import urlparse
import os
import pdfannotation
import PyPDF2

HIGHLIGHTSQUERY = """SELECT Files.localUrl, FileHighlightRects.page,
                            FileHighlightRects.x1, FileHighlightRects.y1,
                            FileHighlightRects.x2, FileHighlightRects.y2
                    FROM Files
                    LEFT JOIN FileHighlights
                        ON FileHighlights.fileHash=Files.hash
                    LEFT JOIN FileHighlightRects
                        ON FileHighlightRects.highlightId=FileHighlights.id
                    WHERE FileHighlightRects.page IS NOT NULL"""

def converturl2abspath(url):
    return os.path.abspath(unquote(urlparse(url).path))

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

def highlight_in_document(inpdf, outpdf, highlights):
    for pg in highlights.keys():
        inpg = inpdf.getPage(pg-1)
        for hn in highlights[pg]:
            annot = pdfannotation.highlight_annotation(hn)
            pdfannotation.add_annotation(outpdf, inpg, annot)
        outpdf.addPage(inpg)
    return outpdf

def processpdf(fn, fn_out, highlights):
    inpdf = PyPDF2.PdfFileReader(fn)
    outpdf = PyPDF2.PdfFileWriter()
    outpdf = highlight_in_document(inpdf, outpdf, highlights)
    outpdf.write(open(fn_out, "wb"))


if __name__ == "__main__":
    import sys

    fn = sys.argv[1]
    db = sqlite3.connect(fn)
    ret = db.execute(HIGHLIGHTSQUERY)
    hh = parse_query(ret)
    ff = "/home/jschrod/Uni/Papers/Mendeley/He et al._2010.pdf"
    #highlight_in_document(ff, hh[ff])






