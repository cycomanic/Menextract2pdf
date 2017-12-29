FROM	python:2.7.14-jessie

WORKDIR	/usr/src/app

# Install tools
RUN		DEBIAN_FRONTEND=noninteractive  \
		apt-get update -qq && apt-get install --no-install-recommends -y sqlite3 

# Install python modules
RUN		pip install --no-cache-dir pypdf2 python-dateutil

COPY	src/* ./

COPY	menextract2pdf.sh .
RUN		chmod +x menextract2pdf.sh

CMD		[ "python", "menextract2pdf.py", "--help" ]
