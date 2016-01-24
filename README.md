# Menextract2pdf
*Extract Mendeley annotations to PDF Files*

Menextract2pdf extracts highlights and notes from the Mendeley database and adds
them directly to all relevant PDF files, which can then be read by most PDF readers. 

## Why?

PDF highlights and notes in Mendeley are stored in the Mendeley database and can not
be read by other programs. While it is possible to extract and save the
annotations to the PDF file, this is a tedious manual process requiring to open
every PDF and selecting export to PDF for that file. Menextract2pdf provides
a bulk export functionality.
 
## Dependencies

Menextract2pdf is written in python2.7. It requires the following packages:
* PyPDF2
* sqlite3

It further incorporate (with small adjustments) the pdfannotation.py file from  the [PRSAnnots https://github.com/rschroll/prsannots] project.

## Usage

```python
python menextract2pdf.py mendeley.sqlite /Destination/Dir/
```
where mendeley.sqlite is the mendeley database and /Destination/Dir/ is the
directory where to store the annotated PDF files. By default menextract2pdf
will not overwrite existing PDF files in the destination directory. To allow
overwriting use the ```python --overwrite``` flag. 

The software is tested on Linux, but should run on Windows or Mac as well. 

## Versions

* 0.1 first release

## Licence

The script is distributed under the GPLv3. The pdfannotations.py file is
LGPLv3. 

## Related projects

* [Mendeley2Zotero https://github.com/flinz/mendeley2zotero]
* [Adios_Mendeley https://github.com/rdiaz02/Adios_Mendeley]
