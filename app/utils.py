from fastapi import HTTPException, Header
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("API_KEY")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    

def extract_text_from_element(elem):
    category = elem.get("category")
    content = elem.get("content", {})
    
    html = content.get("html", "")

    parts = []
    seen = set()

    if category == "table":
        parts.append(html)

    elif category == "figure":
        img = elem.get("base64_encoding", "")
        parts.append(img)

    else:
        soup = BeautifulSoup(html, "html.parser")

        # <br> 태그를 줄바꿈으로 교체
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # HTML 텍스트 추출 (연속 줄바꿈 제거 포함)
        html_text = soup.get_text(separator="\n").strip()
        html_text = "\n".join(line.strip() for line in html_text.splitlines() if line.strip())

        # markdown / text도 병합하되, 중복 제거
        markdown = content.get("markdown", "").strip()
        text = content.get("text", "").strip()

        for part in [html_text, markdown, text]:
            if part and part not in seen:
                parts.append(part)
                seen.add(part)

    return category, "\n".join(parts)


def chunk_by_heading1(elements):
    chunks = []
    current_chunk = None

    for elem in elements:
        if elem["category"] == "footer":
            continue
        
        category, text = extract_text_from_element(elem)

        if category == "heading1":
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = {
                "section_heading": text,
                "elements": []
            }
        else:
            if current_chunk:
                current_chunk["elements"].append({
                    "category": category,
                    "text": text,
                    "id": elem.get("id"),
                    "page": elem.get("page")
                })

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def get_base64_by_id(elements, target_id):
    for element in elements:
        if element.get("id") == target_id:
            return element.get("base64_encoding")
    return None
