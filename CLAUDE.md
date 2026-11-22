# Chronicles of Pixel — 작업 규칙

## 릴리즈 절차 (새 버전을 낼 때마다 전부 수행)

새 버전을 릴리즈할 때는 **GitHub 릴리즈와 프로젝트 폴더의 EXE를 항상 같은 버전으로** 맞춘다.

1. 테스트 통과 확인
   ```powershell
   .venv\Scripts\python.exe -m unittest discover -s tests
   ```
2. 커밋 후 `main` 푸시
   - 작성자는 기존 커밋과 같은 `Codex <codex@openai.com>`로 한다.
   - `.git` 소유자가 다른 계정이라 git 명령마다 `-c safe.directory=C:/Users/dongb/IdeaProjects/RPG`를 붙인다.
3. 버전 태그(`vX.Y.Z`)를 만들어 푸시
   - 태그 푸시 시 `.github/workflows/release.yml`이 EXE를 빌드해 GitHub 릴리즈에 `ChroniclesOfPixel.exe`를 올린다.
   - Actions 실행이 `success`로 끝나고 릴리즈에 EXE가 첨부됐는지 확인한다.
4. **프로젝트 폴더의 EXE도 같은 버전으로 다시 빌드**
   ```powershell
   .venv\Scripts\python.exe -m PyInstaller --noconfirm ChroniclesOfPixel.spec
   ```
   - 결과물: `dist\ChroniclesOfPixel.exe` (이전 파일을 덮어씀)
   - `.spec` 파일은 git에 포함되지 않으므로, 없으면 아래 명령으로 빌드한다.
     ```powershell
     .venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --add-data "assets;assets" --icon "assets/icon.ico" --name "ChroniclesOfPixel" main.py
     ```
   - 빌드 후 EXE를 잠깐 실행해 정상적으로 뜨는지 확인하고 닫는다.
5. 사용자에게 GitHub 릴리즈 링크와 로컬 EXE 경로를 함께 보고한다.

## 참고

- EXE 파일 이름은 GitHub 릴리즈와 로컬 모두 `ChroniclesOfPixel.exe`로 통일한다.
- 아이콘은 `tools/make_icon.py`로 `assets/icon.png`, `assets/icon.ico`를 다시 생성한다.
- 게임 기획서: `docs/별빛 결계의 수호자 게임 기획서.pdf`
