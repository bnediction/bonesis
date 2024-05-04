# Source for BoNesis documentation

This is using https://jupyterbook.org.

- Setup: `pip install -r requirements.txt`
- Build: `make build` ; optionaly `make clean build` or `make depclean build` to clear cache
- Test: `make try`

Useful docs:
- [MyST Markdown syntax cheat sheet](https://jupyterbook.org/en/stable/reference/cheatsheet.html)
- [Content elements](https://jupyterbook.org/en/stable/content/index.html)
- [MyST reference](https://myst-parser.readthedocs.io/en/latest/)
- Converting notebook to MyST: `jupytext _notebooks/file.ipynb --to myst -o file.md`
- Converting MyST to notebook: `jupytext file.md -o _notebooks/file.ipynb`
