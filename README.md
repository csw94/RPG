# Chronicles of Pixel

Pygame CE로 만든 한글 2D 탑뷰 RPG입니다. 필드를 탐험하고, 보물상자를 열고,
턴제 전투를 진행하세요. 화면은 도트 그래픽 스타일로 표시됩니다.

## Windows에서 다운로드 및 실행

1. [최신 릴리즈 페이지](https://github.com/csw94/RPG/releases/latest)를 엽니다.
2. 릴리즈의 Assets에서 **ChroniclesOfPixel.exe**를 다운로드합니다.
3. 다운로드한 EXE 파일을 더블 클릭해 실행합니다. Python 설치는 필요하지 않습니다.

세이브 데이터는 Windows 사용자 앱 데이터 폴더에 저장됩니다. EXE에 한글 폰트가
포함되어 있으므로 별도의 에셋 폴더 없이 실행할 수 있습니다.

## 조작 방법

- 이동: 방향키 또는 WASD
- 상자 열기: 스페이스바
- 저장: F5 또는 필드 화면의 저장 버튼
- 타이틀로 돌아가기: ESC (현재 진행 상황을 저장합니다)
- 전투: 방향키 또는 WASD로 선택한 뒤 Enter/스페이스바, 또는 마우스로 행동 선택

## 소스에서 실행

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Windows 단일 실행 파일 빌드

```powershell
pyinstaller --onefile --windowed --add-data "assets;assets" --name "ChroniclesOfPixel" main.py
```

캐릭터, 맵, 상자, 몬스터는 Pygame 도형으로 그리므로 별도의 이미지 파일이 없어도
플레이할 수 있습니다. 포함된 한글 폰트의 라이선스는 `assets/fonts/OFL.txt`에 있습니다.
