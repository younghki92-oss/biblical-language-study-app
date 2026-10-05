# 원어 성경

히브리어 구약(WLC)과 헬라어 신약(SBLGNT), BSB 영어 번역을 단어별로 연결해 보여 주는 공부 앱입니다.
인터넷 없이도 작동하는 PWA로, 휴대폰 홈 화면이나 맥 Dock에 설치할 수 있습니다.

## 폴더 구성

| 경로 | 내용 | 웹사이트에 올림 |
|---|---|---|
| `index.html` | 앱 화면 전체 | O |
| `manifest.json` | 앱 이름과 아이콘 정보 (설치용) | O |
| `sw.js` | 인터넷 없이 작동하게 하는 보관 담당 | O |
| `data/books/01.json` ~ `66.json` | 책별 본문 데이터 (창세기=01, 마태복음=40, 요한계시록=66) | O |
| `data/glx.json`, `hlx.json`, `pt.json` | 헬라어 사전, 히브리어 사전, 문법 파싱 표 | O |
| `fonts/`, `icons/` | 글꼴과 아이콘 | O |
| `tools/` | 데이터와 글꼴, 아이콘을 만드는 프로그램 | O (참고용) |
| `_원자료/` | 내려받은 원본 자료 | X (`.gitignore`로 제외) |

## 데이터를 다시 만들 때

```bash
python3 tools/build_all.py
```

`_원자료/`에 원본 자료가 있어야 합니다. 자료 출처는 index.html 아래쪽 footer에 있습니다.
다시 만든 뒤에는 `sw.js`의 `DATA_CACHE`와 `index.html`의 `DATA_CACHE` 숫자를 함께 올려야(예: `ob-data-v1` → `ob-data-v2`) 설치된 앱도 새 데이터를 받습니다.

## 화면이나 사전을 고쳤을 때

`sw.js` 맨 위의 `VERSION` 숫자를 올려 주세요(예: `v1` → `v2`).

## 맥에서 미리 보기

```bash
python3 -m http.server 8765
```

그다음 브라우저에서 http://localhost:8765 를 엽니다.
