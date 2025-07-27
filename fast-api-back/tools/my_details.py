import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from langchain_core.tools import tool

@tool
def my_current_info() -> Dict[str, Any]:
    """
    this tool is used to get your current info.Details like what are u currently doing these days future plans, general facts about u.
      - document_id: the Google Doc ID
      - paragraphs: a list of paragraph texts
      - tables: a list of tables, each table is a list of rows, each row is a list of cell strings
      - metadata: additional document metadata
    """
    # 1) Extract the document ID
    url="https://docs.google.com/document/d/1A4n4b5XohNUnv5zbjMWD9hefCTPth0nh7fldJjYAhio/edit?tab=t.0"
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not match:
        raise ValueError(f"Could not find document ID in URL: {url}")
    doc_id = match.group(1)

    # 2) Build the HTML export URL
    export_url = f'https://docs.google.com/document/d/{doc_id}/export?format=html'

    # 3) Download
    resp = requests.get(export_url)
    resp.raise_for_status()

    # 4) Parse with BeautifulSoup
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Extract paragraphs
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]

    # Extract tables
    tables = []
    for tbl in soup.find_all('table'):
        rows = []
        for tr in tbl.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(['td', 'th'])]
            rows.append(cells)
        tables.append(rows)

    # Create JSON structure
    result = {
        "document_id": doc_id,
        "paragraphs": paragraphs,
        "tables": tables
    }

    return str(json.dumps(result, indent=2))


def my_info() -> Dict[str, Any]:
    """
    this tool is used to get your current info.Details like what are u currently doing these days future plans, general facts about u.
      - document_id: the Google Doc ID
      - paragraphs: a list of paragraph texts
      - tables: a list of tables, each table is a list of rows, each row is a list of cell strings
      - metadata: additional document metadata
    """
    # 1) Extract the document ID
    url="https://docs.google.com/document/d/1A4n4b5XohNUnv5zbjMWD9hefCTPth0nh7fldJjYAhio/edit?tab=t.0"
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not match:
        raise ValueError(f"Could not find document ID in URL: {url}")
    doc_id = match.group(1)

    export_url = f'https://docs.google.com/document/d/{doc_id}/export?format=html'

    resp = requests.get(export_url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    
    tables = []
    
    for tbl in soup.find_all('table'):
        rows = []
        for tr in tbl.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(['td', 'th'])]
            rows.append(cells)
        tables.append(rows)
    result = {
        "document_id": doc_id,
        "paragraphs": paragraphs,
        "tables": tables
    }
    return str(json.dumps(result, indent=2))