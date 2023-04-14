build_app:
	pyinstaller --name "AlphaLoL" --icon icon.ico --specpath misc \
				--add-data "../img;img" \
				--clean --noconfirm src/main.py

.PHONY: build_app
