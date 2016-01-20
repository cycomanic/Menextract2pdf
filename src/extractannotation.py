import sqlite3
import popplerqt4
import PyQt4
from urllib.parse import urlparse, unquote
import os

HIGHLIGHTSQUERY = """SELECT Files.localUrl, FileHighlightRects.page,
                            FileHighlightRects.x1, FileHighlightRects.y1,
                            FileHighlightRects.x2, FileHighlightRects.y2
                    FROM Files
                    LEFT JOIN FileHighlights
                        ON FileHighlights.fileHash=Files.hash
                    LEFT JOIN FileHighlightRects
                        ON FileHighlightRects.highlightId=FileHighlights.id
                    WHERE FileHighlightRects.page IS NOT NULL"""


def create_bbox(x1, y1, x2, y2):
    rc = PyQt4.QtCore.QRectF()
    rc.setCoords(x1,y1,x2,y2)
    return rc

def get_highlighted_text(doc, pgno, bbox):
    pg = doc.page(pgno-1)
    return pg.text(bbox)

def parse_query(res):
    highlights = {}
    for r in res:
        pth = os.path.abspath(unquote(urlparse(r[0]).path))
        bbox = create_bbox(r[2], r[3], r[4], r[5])
        pg = r[1]
        if pth in highlights:
            highlights[pth].append([pg, bbox])
        else:
            highlights[pth] = [[pg, bbox]]
    return highlights

def highlight_in_document(fn, highlights):
    doc = popplerqt4.Poppler.Document.load(fn)
    for hn in highlights:
        print("====%d===="%hn[0])
        print("----")
        print(str(get_highlighted_text(doc, hn[0], hn[1])))
        print("----")


if __name__ == "__main__":
    import sys

    fn = sys.argv[1]
    db = sqlite3.connect(fn)
    ret = db.execute(HIGHLIGHTSQUERY)
    hh = parse_query(ret)
    ff = "/home/jschrod/Uni/Papers/Mendeley/He et al._2010.pdf"
    highlight_in_document(ff, hh[ff])






