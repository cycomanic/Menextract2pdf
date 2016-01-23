# Copyright 2016 Jochen Schroeder
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
from dateutil import parser as dtparser

HIGHLIGHTSQUERY = """SELECT Files.localUrl, FileHighlightRects.page,
                            FileHighlightRects.x1, FileHighlightRects.y1,
                            FileHighlightRects.x2, FileHighlightRects.y2,
                            FileHighlights.createdTime
                    FROM Files
                    LEFT JOIN FileHighlights
                        ON FileHighlights.fileHash=Files.hash
                    LEFT JOIN FileHighlightRects
                        ON FileHighlightRects.highlightId=FileHighlights.id
                    WHERE (FileHighlightRects.page IS NOT NULL)"""

NOTESQUERY = """SELECT Files.localUrl, FileNotes.page,
                            FileNotes.x, FileNotes.y,
                            FileNotes.author, FileNotes.note,
                            FileNotes.modifiedTime
                    FROM Files
                    LEFT JOIN FileNotes
                        ON FileNotes.fileHash=Files.hash
                    WHERE FileNotes.page IS NOT NULL"""

global OVERWRITE_PDFS
OVERWRITE_PDFS = False

def convert2datetime(s):
    return dtparser.parse(s)

def converturl2abspath(url):
    """Convert a url string to an absolute path"""
    pth = unquote(str(urlparse(url).path)).decode("utf8") #this is necessary for filenames with unicode strings
    return os.path.abspath(pth)

def parse_highlights(res, highlights={}):
    for r in res:
        pth = converturl2abspath(r[0])
        pg = r[1]
        bbox = [[r[2], r[3], r[4], r[5]]]
        cdate = convert2datetime(r[6])
        hlight = {"rect": bbox, "cdate": cdate}
        if pth in highlights:
            if pg in highlights[pth] and 'highlights' in highlights[pth][pg]:
                highlights[pth][pg]['highlights'].append(hlight)
            else:
                highlights[pth][pg] = {'highlights': [hlight]}
        else:
            highlights[pth] = {pg: {'highlights':[hlight]}}
    return highlights

def parse_notes(res, notes={}):
    for r in res:
        pth = converturl2abspath(r[0])
        pg = r[1]
        bbox = [r[2], r[3], r[2]+30, r[3]+30] # needs a rectangle however size does not matter
        author = r[4]
        txt = r[5]
        cdate = convert2datetime(r[6])
        note = {"rect": bbox, "author": author, "content": txt, "cdate":cdate}
        if pth in notes:
            if pg in notes[pth] and 'notes' in notes[pth][pg]:
                notes[pth][pg]['notes'].append(note)
            else:
                notes[pth][pg] = {'notes': [note]}
        else:
            notes[pth] = {pg: {'notes':[note]}}
    return notes


def add_annotation2pdf(inpdf, outpdf, annotations):
    for pg in annotations.keys():
        inpg = inpdf.getPage(pg-1)
        if 'highlights' in annotations[pg]:
            print "pg=%d highlight"%pg
            for hn in annotations[pg]['highlights']:
                annot = pdfannotation.highlight_annotation(hn["rect"], cdate=hn["cdate"])
                pdfannotation.add_annotation(outpdf, inpg, annot)
        if 'notes' in annotations[pg]:
            print "pg=%d note"%pg
            for nt in annotations[pg]['notes']:
                print "pg=%d note=%s"%(pg, nt["content"])
                note = pdfannotation.text_annotation(nt["rect"], contents=nt["content"], author=nt["author"],
                                                     cdate=nt["cdate"])
                pdfannotation.add_annotation(outpdf, inpg, note)
        outpdf.addPage(inpg)
    return outpdf

def processpdf(fn, fn_out, annotations):
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
    outpdf = add_annotation2pdf(inpdf, outpdf, annotations)
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
    highlights = parse_highlights(db.execute(HIGHLIGHTSQUERY))
    annotations_all = parse_notes(db.execute(NOTESQUERY), highlights)
    for fn, annons in highlights.iteritems():
        processpdf(fn, os.path.join(dir_pdf, os.path.basename(fn)), annons)

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







