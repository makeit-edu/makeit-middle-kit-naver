#!/usr/bin/env python3
"""2주차 저장소 빌드 — 1주차 저장소(원본)에서 승인글 부분을 복사해 오고 네이버를 더한다.

원칙
  · 승인글 코드의 원본은 1주차 저장소(makeit-middle-kit) 하나다. 여기서 고치지 않는다. 1주차에서 고치고 이 빌드를 다시 돌린다.
  · 2주차 저장소에만 있는 것: 앱/네이버.mjs · 앱/네이버/ · 앱/대본_네이버.md · 앱/빌드.py · 앱/배포.sh · README_2주차.md
  · 복사하면서 저장소 이름(주소)만 2주차 것으로 바꾼다. 대본 속 base64 로 감싼 주소도 풀어서 바꾸고 다시 감싼다.

쓰는 법: python3 앱/빌드.py ../makeit-middle-kit
"""
import base64, json, os, re, shutil, sys, urllib.parse
from pathlib import Path

W2 = Path(__file__).resolve().parent.parent
W1 = Path(sys.argv[1] if len(sys.argv) > 1 else W2.parent / "makeit-middle-kit").resolve()
옛 = "makeit-edu/makeit-middle-kit"
새 = "makeit-edu/makeit-middle-kit-naver"
if not (W1 / "앱" / "승인글.mjs").exists():
    sys.exit(f"1주차 저장소를 못 찾음: {W1}")


def 주소바꾸기(글: str) -> str:
    글 = re.sub(re.escape(옛) + r"(?![-\w])", 새, 글)
    글 = re.sub(r"makeit-edu\.github\.io/makeit-middle-kit(?![-\w])", "makeit-edu.github.io/makeit-middle-kit-naver", 글)

    def b64(m):
        원문 = base64.b64decode(m.group(1)).decode("utf8")
        바뀜 = 원문.replace("/" + 옛 + "/", "/" + 새 + "/")
        return 'atob("' + base64.b64encode(바뀜.encode("utf8")).decode("ascii") + '")'

    return re.sub(r'atob\("([A-Za-z0-9+/=]+)"\)', b64, 글)


def 바꾸기(글: str, 쌍, 이름: str) -> str:
    for 앞, 뒤 in 쌍:
        if 앞 not in 글:
            sys.exit(f"[{이름}] 바꿀 곳을 못 찾음: {앞[:60]!r}")
        글 = 글.replace(앞, 뒤, 1)
    return 글


# 1) 그대로 복사 (주소만 바꿈)
복사 = ["앱/로더.mjs", "앱/승인글.mjs", "앱/키설정.txt", "앱/제목.txt", ".gitignore"]
for f in 복사:
    (W2 / f).parent.mkdir(parents=True, exist_ok=True)
    (W2 / f).write_text(주소바꾸기((W1 / f).read_text(encoding="utf8")), encoding="utf8")

스크립트 = "99_절대_건들지마세요_프로그램파일/scripts"
if (W2 / 스크립트).exists():
    shutil.rmtree(W2 / 스크립트)
for 뿌리, _, 이름들 in os.walk(W1 / 스크립트):
    for n in 이름들:
        if not n.endswith((".mjs", ".js", ".json")):
            continue
        원 = Path(뿌리) / n
        목적 = W2 / 원.relative_to(W1)
        목적.parent.mkdir(parents=True, exist_ok=True)
        목적.write_text(주소바꾸기(원.read_text(encoding="utf8")), encoding="utf8")

# 2) 설치.mjs — 설치 뒤 안내만 2주차용으로
설치 = 주소바꾸기((W1 / "앱/설치.mjs").read_text(encoding="utf8"))
설치 = re.sub(r'다음: 전부됨 \? "설치 끝\..*?" : "",',
            '다음: 전부됨 ? "설치 끝. 결과 JSON 은 수강생에게 보여 주지 않는다. 곧바로 작업 폴더 AGENTS.md 대본의 준비 코드와 \'네이버 글 ①\' 코드를 실행한다. '
            '키설정끝 이 false 면(1주차를 안 한 수강생) 1주차와 똑같이 수강생에게 딱 두 문장만 말하고 답을 기다린다: \'설치가 끝났어요. 이제 처음 한 번만 하는 키 설정입니다.\' \'먼저 강의 자료실 공지에 있는 수강 코드를 알려 주세요.\' 수강 코드를 받으면 저장하고 키설정.txt 를 끌어다 놓아 달라고 한다. '
            '키설정끝 이 true 면 \'설치가 끝났어요. 네이버 글을 쓸 준비를 할게요.\' 한 줄 뒤 \'네이버 글 ②\' 로그인 확인으로 간다. '
            '새 채팅을 열라고 하지 않는다." : "",', 설치, count=1, flags=re.S)
if "네이버 글 ①" not in 설치:
    sys.exit("[설치.mjs] 다음 문구를 못 바꿈")
(W2 / "앱/설치.mjs").write_text(설치, encoding="utf8")

# 3) 대본 = 1주차 대본 + 네이버 부분, 판 2
대본 = 주소바꾸기((W1 / "앱/AGENTS.md").read_text(encoding="utf8"))
네이버대본 = (W2 / "앱/대본_네이버.md").read_text(encoding="utf8")
대본 = 바꾸기(대본, [
    ("# 메킷 키트 — 승인글 도우미 (코덱스 대본)\n<!-- 키트판 2 -->", "# 메킷 키트 — 승인글·네이버 도우미 (코덱스 대본)\n<!-- 키트판 3 -->"),
    ('"키 설정", "진단", "설치" 같은 말을 하거나', '"키 설정", "진단", "설치", "네이버", "블로그" 같은 말을 하거나'),
    ("\n## 진단 — ", 네이버대본.rstrip() + "\n\n## 진단 — "),
    ("    > 이제 승인글 **제목 파일(txt)** 을 여기에 끌어다 놓거나, 제목을 한 줄에 하나씩 붙여넣어 주세요. 1개만 주셔도 되고 100개를 주셔도 됩니다.\n",
     "    > 이어서 네이버 글을 쓸 준비를 할게요.\n"),
    ("    > 제목은 사이트마다 따로 받을게요. 먼저 **1번 사이트**의 제목 파일(txt)을 끌어다 놓거나 제목을 한 줄에 하나씩 붙여넣어 주세요.\n  그다음은 **\"글 만들기\"** 의 \"제목\" 으로 간다.",
     "    > 이어서 네이버 글을 쓸 준비를 할게요.\n  그다음은 곧바로 **\"네이버 글 ①\"** 코드를 실행한다 (크롬 연결 → ② 로그인 확인 → ③ 키워드). 2주차에서는 키 설정 뒤 제목 파일을 묻지 않는다. 승인글은 수강생이 \"승인글 자동화 시작해\" 라고 할 때만 한다."),
    ("- 수강생에게 선택지(주제·말투·분량·독자)를 묻지 않는다. 묻는 건 키설정 txt, 제목, 개수뿐이다.",
     "- 수강생에게 선택지(주제·말투·분량·독자)를 묻지 않는다. 묻는 건 키설정 txt, 제목, 개수뿐이다 (네이버는 키워드 하나)."),
], "AGENTS.md")
(W2 / "앱/AGENTS.md").write_text(대본, encoding="utf8")

# 4) README — 1주차의 '코덱스에게' 부분을 가져와 설치 뒤 안내만 바꾸고, 사람용 안내를 붙인다
원README = 주소바꾸기((W1 / "README.md").read_text(encoding="utf8"))
코덱스부분 = 원README.split("\n---\n", 1)[0]
코덱스부분 = 바꾸기(코덱스부분, [
    ("# 월부 중급반 메킷 키트", "# 월부월백 중급반 메킷 키트 — 승인글 + 네이버"),
], "README")
코덱스부분 = re.sub(r'`결과: "설치 끝"` 이 나오면 수강생에게 딱 이 두 문장만 말하고 답을 기다려라:.*?키설정\.txt 를 달라고 한다\)\.',
                  '`결과: "설치 끝"` 이 나오면 결과의 `다음` 에 적힌 대로 곧바로 이어간다 (방금 작업 폴더에 생긴 `AGENTS.md` 대본의 준비 코드 → "네이버 글" 순서). 키 설정이 안 돼 있으면 대본대로 수강 코드부터 묻는다.',
                  코덱스부분, count=1, flags=re.S)
if "네이버 글" not in 코덱스부분:
    sys.exit("[README] 설치 뒤 안내를 못 바꿈")
사람부분 = (W2 / "README_2주차.md").read_text(encoding="utf8")
(W2 / "README.md").write_text(코덱스부분.rstrip() + "\n\n---\n\n" + 사람부분.lstrip(), encoding="utf8")

# 5) 목록.json — 진입 두 개, 파일 목록
원목록 = json.loads((W1 / "앱/목록.json").read_text(encoding="utf8"))
파일 = ["앱/승인글.mjs", "앱/AGENTS.md", "앱/네이버.mjs"]
파일 += sorted(str(p.relative_to(W2)).replace(os.sep, "/") for p in (W2 / "앱/네이버").glob("*") if p.suffix in (".mjs", ".json"))
파일 += sorted(str(p.relative_to(W2)).replace(os.sep, "/") for p in (W2 / 스크립트).rglob("*.mjs"))
목록경로 = W2 / "앱/목록.json"
기존 = json.loads(목록경로.read_text(encoding="utf8")) if 목록경로.exists() else {}
목록 = {
    "버전": 기존.get("버전", ""), "정지": 기존.get("정지", False), "정지안내": 기존.get("정지안내", ""),
    "커밋": 기존.get("커밋", ""), "진입": {"승인글": "앱/승인글.mjs", "네이버": "앱/네이버.mjs"},
    "수강코드": 원목록.get("수강코드", []), "파일": sorted(set(파일)),
}
# 맥은 한글 파일 이름을 자모로 쪼갠(NFD) 모양으로 준다. GitHub 는 붙인(NFC) 이름이라 주소가 404 가 된다 (2026-09-23 실측: 글만들기.mjs).
import unicodedata
목록["파일"] = sorted(set(unicodedata.normalize("NFC", f) for f in 목록["파일"]))
목록경로.write_text(json.dumps(목록, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(f"빌드 끝: 1주차 {W1.name} → 2주차 {W2.name} · 프로그램 파일 {len(목록['파일'])}개")
