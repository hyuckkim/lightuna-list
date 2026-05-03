import json
import re
import sys
import os

def escape_js_string(s: str) -> str:
    """JS 문자열에 안전하게 들어갈 수 있도록 따옴표와 역슬래시 이스케이프"""
    return s.replace("\\", "\\\\").replace('"', '\\"')


if len(sys.argv) != 3:
    print("사용법: python run.py input.json output.html")
    sys.exit(1)
  
# JSON 파일 읽기
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

entries = []
for item in data:
    # username 안의 <b> 태그 제거
    username = re.sub(r"</?b>", "", item.get("username", ""))
    # 각 필드 이스케이프
    id_ = str(item["threadId"])
    source = escape_js_string(username.strip())
    url = escape_js_string(f'https://bbs2.tunaground.net/archive/{item["boardId"]}/{item["threadId"]}')
    title = escape_js_string(item["title"].strip())

    entries.append(
        {"id": id_, "source": source, "url": url, "title": title}
    )

# threadId를 기준으로 오름차순 정렬
entries.sort(key=lambda x: int(x["id"]))

# JavaScript 객체 형식으로 변환
entries_js = [
    f'{{ id: "{entry["id"]}", source: "{entry["source"]}", url: "{entry["url"]}", title: "{entry["title"]}" }}'
    for entry in entries
]

# 템플릿 파일 읽기
template_path = os.path.join(os.path.dirname(sys.argv[0]), "template.html")
with open(template_path, "r", encoding="utf-8") as f:
    template_html = f.read()

# 최종 HTML 생성
entries_str = ",\n".join(entries_js)
html_output = template_html.replace("/*ENTRIES*/", entries_str)

with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write(html_output)

print(f"✅ 총 {len(entries)}개 항목 변환 완료. output.html 생성됨.")
