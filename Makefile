build:
	nuitka3 --follow-imports --standalone --onefile src/boot.py -o shark

install_deps:
	pip3 install -r requirements.txt --prefix=~/.local/
