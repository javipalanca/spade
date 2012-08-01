all:
	mkdir -p html/images
	xsltproc --output html/ chunk-stylesheet.xsl book.xml
	cp styles.css html
	cp images/* html/images
