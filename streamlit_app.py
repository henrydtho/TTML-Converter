"""Browser-based Windows-friendly UI for the TTML HDR converter."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET

import streamlit as st

from ttml_conversion import convert_ttml_to_hdr, suggested_destination


st.set_page_config(page_title="TTML HDR Converter", page_icon="HDR", layout="centered")

st.title("TTML HDR Converter V2")
st.caption("IMSC 1.1 SDR-to-HDR text style conversion")

uploaded_files = st.file_uploader(
    "Drop up to 100 SDR TTML files here", type=["ttml"], accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 100:
        st.error("Select no more than 100 TTML files at a time.")
    else:
        st.write(f"{len(uploaded_files)} TTML file(s) selected")

        if st.button("Convert to HDR", type="primary"):
            archive = BytesIO()
            completed_files = 0
            updated_styles = 0
            failures: list[str] = []

            with ZipFile(archive, "w", ZIP_DEFLATED) as output_zip:
                for uploaded_file in uploaded_files:
                    source_name = Path(uploaded_file.name)
                    try:
                        converted_ttml, file_updated_styles = convert_ttml_to_hdr(uploaded_file.getvalue())
                    except (ET.ParseError, UnicodeDecodeError, ValueError) as error:
                        failures.append(f"{source_name.name}: {error}")
                    else:
                        output_zip.writestr(suggested_destination(source_name).name, converted_ttml)
                        completed_files += 1
                        updated_styles += file_updated_styles

            if completed_files:
                st.success(f"Converted {completed_files} file(s) and {updated_styles} text style(s).")
                st.download_button(
                    "Download HDR TTML ZIP",
                    data=archive.getvalue(),
                    file_name="TTML_HDR_V2.zip",
                    mime="application/zip",
                    type="primary",
                )
            for failure in failures:
                st.error(failure)

with st.expander("HDR settings applied"):
    st.code(
        'tts:color="#929292"\n'
        'tts:textOutline="#000000 3%"',
        language="xml",
    )
    st.write("TT header content remains unchanged. Style elements do not receive tts:opacity. The app requires the IMSC 1.1 Text profile and rejects Rec.709-only profile metadata.")