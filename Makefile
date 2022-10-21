PKG := /home/dletran/PYTHONPATH/sqlwrapper

reinstall: uninstall install

uninstall:
	python3 -m pip uninstall sqlwrapper -y

install:
	cd $(PKG) && git pull
	python3 -m pip install $(PKG)

