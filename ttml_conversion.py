"""Shared IMSC TTML SDR-to-HDR conversion logic."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET


TTS_NAMESPACE = "http://www.w3.org/ns/ttml#styling"
TTP_NAMESPACE = "http://www.w3.org/ns/ttml#parameter"
HDR_TEXT_COLOR = "#929292"
HDR_TEXT_OPACITY = "0.80"
HDR_TEXT_OUTLINE = "#000000 3%"
TT_TAG = "{http://www.w3.org/ns/ttml}tt"
HEAD_TAG = "{http://www.w3.org/ns/ttml}head"


def source_namespaces(source: str | Path | BytesIO) -> dict[str, str]:
    namespaces: dict[str, str] = {}
    for _, declaration in ET.iterparse(source, events=("start-ns",)):
        prefix, uri = declaration
        namespaces[prefix or ""] = uri
    return namespaces


def convert_ttml_to_hdr(ttml_data: bytes) -> tuple[bytes, int]:
    """Apply HDR text settings and return converted UTF-8 TTML bytes."""
    namespaces = source_namespaces(BytesIO(ttml_data))
    tree = ET.parse(BytesIO(ttml_data))
    profile_attribute = f"{{{TTP_NAMESPACE}}}contentProfiles"
    color_attribute = f"{{{TTS_NAMESPACE}}}color"
    opacity_attribute = f"{{{TTS_NAMESPACE}}}opacity"
    outline_attribute = f"{{{TTS_NAMESPACE}}}textOutline"
    profile = tree.getroot().get(profile_attribute, "")
    normalized_profile = profile.lower().replace(".", "").replace(" ", "")

    if "imsc1.1/text" not in profile:
        raise ValueError("The TTML must declare the IMSC 1.1 Text content profile.")
    if "rec709" in normalized_profile:
        raise ValueError("The TTML profile metadata is restricted to Rec.709; review it before HDR delivery.")

    def update_element(element: ET.Element) -> int:
        if element.tag in (TT_TAG, HEAD_TAG):
            return 0

        updated_elements = 0
        if color_attribute in element.attrib:
            element.set(color_attribute, HDR_TEXT_COLOR)
            element.set(opacity_attribute, HDR_TEXT_OPACITY)
            element.set(outline_attribute, HDR_TEXT_OUTLINE)
            updated_elements += 1

        for child in element:
            updated_elements += update_element(child)
        return updated_elements

    updated_styles = sum(update_element(child) for child in tree.getroot())

    if updated_styles == 0:
        raise ValueError("No tts:color attributes were found in this TTML file.")

    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    output = BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output.getvalue(), updated_styles


def convert_to_hdr(source: Path, destination: Path) -> int:
    if source.suffix.lower() != ".ttml":
        raise ValueError("Select a TTML file with a .ttml extension.")
    if source.resolve() == destination.resolve():
        raise ValueError("Choose a new output location; the source file cannot be overwritten.")

    converted_ttml, updated_styles = convert_ttml_to_hdr(source.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(converted_ttml)
    return updated_styles


def suggested_destination(source: Path) -> Path:
    stem = source.stem.replace("UHDSDR", "UHDPQ")
    if stem == source.stem:
        stem = f"{stem}_HDR"
    return source.with_name(f"{stem}.ttml")