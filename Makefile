build:
	jupyter-book build .
clean:
	jupyter-book clean --all .
try:
	xdg-open _build/html/index.html
