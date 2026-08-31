# TTML HDR Converter V2

A small app for converting SDR IMSC TTML text styles to HDR settings.

## Windows Streamlit Edition

Share the project folder with the coworker as a ZIP file. On Windows, they unzip it and double-click `Run TTML HDR Converter.bat`. The app opens in their default browser at `http://localhost:8501`, where they upload up to 100 SDR TTML files and download the converted files in a ZIP archive.

No administrator permissions are needed: the launcher creates its `.venv` inside the unzipped folder. The first run needs internet access to install Streamlit, and Python 3 must already be available to their Windows user account. A Windows `.exe` cannot be built or tested on this Mac; creating a truly no-prerequisite installer would require a Windows build machine or a web host.

## Run

```sh
.venv/bin/python ttml_hdr_converter.py
```

Drop up to 100 SDR `.ttml` files into the window, choose an output folder, and select **Convert to HDR**. Source files are never overwritten.

For each non-header element with `tts:color`, the converter applies `tts:color="#929292"` and `tts:textOutline="#000000 3%"`. Non-style elements also receive `tts:opacity="0.80"`; style elements do not. The `<tt>` header element is not changed. It requires the IMSC 1.1 Text profile and rejects Rec.709-only profile metadata. All other TTML content is preserved and the output is UTF-8 XML.