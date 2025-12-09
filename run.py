import json
import re
import sys

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
        f'{{ id: "{id_}", source: "{source}", url: "{url}", title: "{title}" }}'
    )

# JS 함수 정의
js_code = """
const pageSize = 50;
let currentPage = 1;

function renderResults(list) {
  const container = document.getElementById(\"results\");
  container.innerHTML = list.map(e =>
    `<p>[${e.id}] ${e.source} - <a href=\"${e.url}\" target=\"_blank\">${e.title}</a></p>`
  ).join("");
}

function paginate(list, page) {
  const start = (page - 1) * pageSize;
  return list.slice(start, start + pageSize);
}

function renderPagination(list) {
  const totalPages = Math.ceil(list.length / pageSize);
  const container = document.getElementById(\"pagination\");
  container.innerHTML = Array.from({length: totalPages}, (_, i) =>
    `<button onclick=\"goPage(${i+1})\">${i+1}</button>`
  ).join(" ");
}

function goPage(page) {
  currentPage = page;
  const q = document.getElementById(\"searchBox\").value.toLowerCase();
  const filtered = entries.filter(e =>
    e.title.toLowerCase().includes(q) ||
    e.source.toLowerCase().includes(q)
  );
  renderResults(paginate(filtered, page));
  renderPagination(filtered);
}

document.getElementById(\"searchBox\").addEventListener(\"input\", () => goPage(1));

// 초기 렌더링
goPage(1);"""


# 최종 HTML 생성
html_output = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>검색 페이지</title>
</head>
<body>

<input type="text" id="searchBox" placeholder="검색어 입력">
<div id="results"></div>
<div id="pagination"></div>

<script>
const entries = [
%s
];
%s
</script>
</body>
</html>
""" % (",\n".join(entries, ), js_code)

with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write(html_output)

print(f"✅ 총 {len(entries)}개 항목 변환 완료. output.html 생성됨.")
