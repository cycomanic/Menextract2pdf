import sqlite3
#import popplerqt4
#import PyQt4
#from urllib.parse import urlparse, unquote
from urllib import unquote, urlopen
from StringIO import StringIO
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
    print fn
    try:
        inpdf = PyPDF2.PdfFileReader(open(fn, 'rb'))
        if inpdf.isEncrypted:
            # PyPDF2 seems to think some files are encrypted even
            # if they are not. We just ignore the encryption.
            # This seems to work for the one file where I saw this issue
            inpdf._override_encryption = True
            inpdf._flatten()
    except IOError:
        Warning("Could not find pdffile %s"%fn)
        return
    outpdf = PyPDF2.PdfFileWriter()
    outpdf = highlight_in_document(inpdf, outpdf, coords)
    outpdf.write(open(fn_out, "wb"))

def mendeley2pdf(fn_db, dir_pdf):
    db = sqlite3.connect(fn_db)
    highlights = parse_query(db.execute(HIGHLIGHTSQUERY))
    for fn, locs in highlights.iteritems():
        processpdf(fn, os.path.join(dir_pdf, os.path.basename(fn)), locs)

if __name__ == "__main__":
    import sys
    try:
        fn = os.path.abspath(sys.argv[1])
        dir_pdf = os.path.abspath(sys.argv[2])
    except:
        print "Usage: %s mendleydatabase pdfdirectory"
        sys.exit(-1)
    mendeley2pdf(fn, dir_pdf)







