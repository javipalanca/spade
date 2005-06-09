PDFLATEX=pdflatex

all: tia.tex changelog.tex

tia.tex: tia.tex changelog.tex
	$(PDFLATEX) tia.tex 
	$(PDFLATEX) tia.tex
	make clean-aux

changelog.tex: ../ChangeLog
	echo "\begin{footnotesize}" > changelog.tex
	echo "\begin{verbatim}" >> changelog.tex
	cat ../ChangeLog >> changelog.tex
	echo "\end{verbatim}" >> changelog.tex
	echo "\end{footnotesize}" >> changelog.tex
clean-aux:
	rm -f *.lof *.toc *.aux *.log changelog.tex
clean:
	make clean-aux
	rm -f tia.pdf
