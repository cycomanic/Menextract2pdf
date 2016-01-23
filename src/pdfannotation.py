# Copyright 2012 Robert Schroll
#
# This file is part of prsannots and is distributed under the terms of
# the LGPL license.  See the file COPYING for full details.
#
# 2016 Jochen Schroeder - added creation time

from datetime import datetime
from PyPDF2.generic import *

YELLOW = [0.95, 0.9, 0.2]

def float_array(lst):
    return ArrayObject([FloatObject(i) for i in lst])

def now():
    # Python timezone handling is a messs, so just use UTC
    return TextStringObject(datetime.utcnow().strftime("D:%Y%m%d%H%M%SZ00'00"))

def _markup_annotation(rect, contents=None, author=None, subject=None,
                       cdate=None, color=None, alpha=1, flag=4):
    """Set shared properties of all markup annotations."""

    if cdate == None:
        cdate = now()
    else:
        assert isinstance(cdate, datetime), "cdate is not a datetime object"
        cdate = TextStringObject(cdate.strftime("D:%Y%m%d%H%M%SZ00'00"))
    retval = DictionaryObject({ NameObject('/CA'): FloatObject(alpha),
                                NameObject('/F'): NumberObject(flag),
                                NameObject('/Rect'): float_array(rect),
                                NameObject('/Type'): NameObject('/Annot'),
                                NameObject('/CreationDate'): cdate,
                                NameObject('/M'): now(),
                             })
    retval.popup = False  # Whether to add an explicit popup when adding to page
    if contents is not None:
        retval[NameObject('/Contents')] = TextStringObject(contents)
    if author is not None:
        retval[NameObject('/T')] = TextStringObject(author)
    if subject is not None:
        retval[NameObject('/Subj')] = TextStringObject(subject)
    if color is not None:
        retval[NameObject('/C')] = float_array(color)
    return retval

def _popup_annotation(parent, rect=None):
    """Create a 'Popup' annotation connected to parent (an indirect object)."""

    if rect is None:
        # Make Golden ratio rectangle lined up at right-hand side of parent
        _, _, x, y = parent.getObject()['/Rect']
        rect = [x, y-100, x+162, y]

    return DictionaryObject({ NameObject('/Type'): NameObject('/Annot'),
                              NameObject('/Subtype'): NameObject('/Popup'),
                              NameObject('/M'): now(),
                              NameObject('/Rect'): float_array(rect),
                              NameObject('/Parent'): parent,
                           })


def highlight_annotation(quadpoints, contents=None, author=None,
                         subject=None, cdate=None, color=YELLOW, alpha=1, flag=4):
    """Create a 'Highlight' annotation that covers the area given by quadpoints.

    Inputs: quadpoints  A list of rectangles to be highlighted as part of this
                        annotation.  Each is specified by a quadruple [x0,y0,x1,y1],
                        where (x0,y0) is the lower left corner of the rectangle and
                        (x1,y1) the upper right corner.

            contents    Strings giving the content, author, and subject of the
            author      annotation
            subject

            color       The color of the highlighted region, as an array of type
                        [g], [r,g,b], or [c,m,y,k].

            alpha       The alpha transparency of the highlight.

            flag        A bit flag of options.  4 means the annotation should be
                        printed.  See the PDF spec for more.

    Output: A DictionaryObject representing the annotation.

    """
    qpl = []

    for x0,y0,x1,y1 in quadpoints:
        qpl.extend([x0, y1, x1, y1, x0, y0, x1, y0])
    # The rectangle needs to contain the highlighted region for Evince
    # and Xpdf to display it.
    def quadpoints_col(i):
        return [pts[i] for pts in quadpoints]
    rect = [min(quadpoints_col(0)), min(quadpoints_col(1)),
            max(quadpoints_col(2)), max(quadpoints_col(3))]

    retval = _markup_annotation(rect, contents, author, subject, cdate,
                                color, alpha, flag)
    retval[NameObject('/Subtype')] = NameObject('/Highlight')
    retval[NameObject('/QuadPoints')] = float_array(qpl)
    return retval

def text_annotation(rect, contents=None, author=None, subject=None,
                    cdate=None, color=YELLOW, alpha=1, flag=4,
                    icon=None, open_=False, state=None, state_model=None):
    """Create a 'Text' annotation, a sticky note at the location rect.

    Inputs: rect        A rectangle [x0,y0,x1,y1].  The icon will be in the top-
                        left corner of this rectangle (x0,y1) regardless of the
                        size of the rectangle.

            contents    Strings giving the content, author, and subject of the
            author      annotation
            subject

            cdate

            color       The color of the note, as an array of type
                        [g], [r,g,b], or [c,m,y,k].

            alpha       The alpha transparency of the note.

            flag        A bit flag of options.  4 means the annotation should be
                        printed.  See the PDF spec for more.

            icon        The icon to use for the note.  Try "Comment", "Key",
                        "Note", "Help", "NewParagraph", "Paragraph", "Insert"

            open_       Whether the note should be opened by default.

            state       These set the state of the annotation.  See the PDF spec
            state_model for further details.

    Output: A DictionaryObject representing the annotation.

    """
    retval = _markup_annotation(rect, contents, author, subject, cdate,
                                color, alpha, flag)
    retval.popup = True
    retval[NameObject('/Subtype')] = NameObject('/Text')
    retval[NameObject('/Open')] = BooleanObject(open_)
    if icon is not None:
        retval[NameObject('/Name')] = NameObject('/' + icon)
    if state is not None:
        retval[NameObject('/State')] = TextStringObject(state)
    if state_model is not None:
        retval[NameObject('/StateModel')] = TextStringObject(state_model)
    return retval

def add_annotation(outpdf, page, annot):
    """Add the annotation 'annot' to the page 'page' that is/will be part of
    the PdfFileWriter 'outpdf'.

    """
    # We need to make an indirect reference, or Acrobat will get huffy.
    indir = outpdf._addObject(annot)
    if '/Annots' in page:
        page['/Annots'].append(indir)
    else:
        page[NameObject('/Annots')] = ArrayObject([indir])

    if annot.popup:
        popup = _popup_annotation(indir)
        indir_popup = outpdf._addObject(popup)
        annot[NameObject('/Popup')] =  indir_popup
        page['/Annots'].append(indir_popup)


if __name__ == '__main__':
    import sys
    import PyPDF2 as pyPdf
    try:
        inpdf = pyPdf.PdfFileReader(open(sys.argv[1], 'rb'))
    except (IndexError, IOError):
        print "Needs PDF file as an argument."
        raise SystemExit
    annot1 = highlight_annotation([[100, 100, 400, 125]],
                'An argument is a connected series of statements intended to establish a proposition.',
                'Graham Chapman', 'I came here for a good argument.')
    annot2 = text_annotation([100, 50, 125, 75],
                "No it isn't.", 'John Cleese', "No you didn't.")
    page = inpdf.getPage(0)
    outpdf = pyPdf.PdfFileWriter()
    add_annotation(outpdf, page, annot1)
    add_annotation(outpdf, page, annot2)
    outpdf.addPage(page)
    outpdf.write(open('pythonannotation.pdf', 'wb'))
    print "Highlighted PDF output to pythonannotation.pdf"
