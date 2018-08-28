REM Helps to find the right mendeley.sqlite-DB

@echo off
set mendeleydb=
for /f "delims=" %a in ('dir /b %~1\*www.mendeley.com.sqlite') do @set mendeleydb=%a
python menextract2pdf.py %mendeleydb% --overwrite