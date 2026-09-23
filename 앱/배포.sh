#!/bin/zsh
# 2주차 저장소 배포: 앱/배포.sh "<커밋 메시지>"
# 1) 1주차 저장소(원본)에서 승인글 부분을 복사 (앱/빌드.py)  2) 커밋  3) 그 커밋 sha 를 목록.json 에 적어 한 번 더 커밋  4) makeit-edu 계정으로 푸시
set -e
cd "$(dirname "$0")/.."
W1="${W1:-../makeit-middle-kit}"
MSG="${1:-2주차 갱신}"
python3 앱/빌드.py "$W1"
for f in 앱/*.mjs 앱/네이버/*.mjs 99_절대_건들지마세요_프로그램파일/scripts/**/*.mjs(N); do node --check "$f"; done
VER="$(date +%Y-%m-%d)$(python3 -c "import json,datetime;v=json.load(open('앱/목록.json')).get('버전','');d=datetime.date.today().strftime('%Y-%m-%d');print(chr(ord(v[-1])+1) if v.startswith(d) and v[-1].isalpha() and v[-1]!='z' else 'a')")"
git add -A
git diff --cached --quiet || git commit -q -m "$MSG"
sha=$(git rev-parse HEAD)
python3 - "$sha" "$VER" <<'PY'
import json,sys
sha,ver=sys.argv[1],sys.argv[2]
m=json.load(open("앱/목록.json",encoding="utf8"))
m.update({"버전":ver,"커밋":sha})
json.dump(m,open("앱/목록.json","w",encoding="utf8"),ensure_ascii=False,indent=2)
open("앱/목록.json","a").write("\n")
print("목록:",ver,sha[:8],len(m["파일"]),"파일")
PY
git add 앱/목록.json
git commit -q -m "앱 목록: 버전 $VER → 커밋 ${sha:0:8}"
if git remote get-url origin >/dev/null 2>&1; then
  gh auth switch -u makeit-edu >/dev/null 2>&1 || true
  git push -q origin main && echo "푸시 완료 $(git rev-parse --short HEAD)"
  gh auth switch -u dreamyapp >/dev/null 2>&1 || true
else
  echo "원격 저장소 없음 — 커밋만 함"
fi
