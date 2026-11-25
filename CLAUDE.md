# Chronicles of Pixel — 작업 규칙

## 저장소 구성

- 소스: `csw94/RPG` (**비공개**). 코드, 테스트, CI(`.github/workflows/ci.yml`)
- 배포: `csw94/Star` (**공개**). README와 GitHub 릴리즈(EXE)만 둔다. 소스는 절대 올리지 않는다.
- GitHub CLI: `C:\Program Files\GitHub CLI\gh.exe` (PATH에 없으면 전체 경로로 실행)

## 릴리즈 절차 (새 버전을 낼 때마다 전부 수행)

공개 저장소의 릴리즈와 프로젝트 폴더의 EXE는 **항상 같은 버전, 같은 파일**이어야 한다.
EXE는 로컬에서 한 번 빌드하고, 그 파일을 그대로 공개 저장소에 올린다.

1. 테스트 통과 확인
   ```powershell
   .venv\Scripts\python.exe -m unittest discover -s tests
   ```
2. `HANDOVER.md`의 "릴리즈 기록"에 `- **vX.Y.Z:** 변경 요약` 줄을 추가하고 README도 필요하면 고친다.
3. 커밋 후 `main` 푸시, 버전 태그(`vX.Y.Z`)를 만들어 푸시 (비공개 소스 저장소)
   - 작성자는 기존 커밋과 같은 `Codex <codex@openai.com>`로 한다.
   - `.git` 소유자가 다른 계정이라 git 명령마다 `-c safe.directory=C:/Users/dongb/IdeaProjects/RPG`를 붙인다.
4. 로컬 EXE 빌드
   ```powershell
   .venv\Scripts\python.exe -m PyInstaller --noconfirm ChroniclesOfPixel.spec
   ```
   - 결과물: `dist\ChroniclesOfPixel.exe` (이전 파일을 덮어씀)
   - `.spec` 파일은 git에 포함되지 않으므로, 없으면 아래 명령으로 빌드한다.
     ```powershell
     .venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --add-data "assets;assets" --icon "assets/icon.ico" --name "ChroniclesOfPixel" main.py
     ```
   - 빌드 후 EXE를 잠깐 실행해 정상적으로 뜨는지 확인하고 닫는다(`Get-Process ChroniclesOfPixel`로 남은 프로세스까지 종료).
5. 공개 저장소에 릴리즈 업로드
   ```powershell
   .venv\Scripts\python.exe tools/release_notes.py vX.Y.Z --out release_notes.md
   & "C:\Program Files\GitHub CLI\gh.exe" release create vX.Y.Z dist/ChroniclesOfPixel.exe --repo csw94/Star --title "Chronicles of Pixel vX.Y.Z" --notes-file release_notes.md
   Remove-Item release_notes.md
   ```
   - 공개 저장소에는 태그가 없으므로 `gh`가 기본 브랜치에 태그를 만든다. 소스는 올라가지 않는다.
   - 릴리즈 페이지에 `ChroniclesOfPixel.exe`가 첨부됐는지 확인한다.
6. 사용자에게 공개 릴리즈 링크(`https://github.com/csw94/Star/releases/tag/vX.Y.Z`)와 로컬 EXE 경로를 함께 보고한다.

## 참고

- EXE 파일 이름은 공개 릴리즈와 로컬 모두 `ChroniclesOfPixel.exe`로 통일한다.
- 아이콘은 `tools/make_icon.py`로 `assets/icon.png`, `assets/icon.ico`를 다시 생성한다.
- 게임 기획서: `docs/별빛 결계의 수호자 게임 기획서.pdf`
