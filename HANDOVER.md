# HANDOVER — 그래픽 퀄리티 업그레이드 (스타듀풍 아늑한 톤)

## 완료된 작업
- **1단계 마을 외부**
  - 풀 타일의 체커보드를 없애고 단일 베이스 색에 풀포기를 얹음
  - 흙길에 테두리를 넣고 폭을 균일하게 맞춤
  - 나무 3종(둥근 나무, 과일나무, 침엽수), 꽃·조약돌 장식, 나무 울타리 테두리, 그림자 추가
- **집 색과 출입구**
  - 지붕을 한 계열로 통일: 오두막 청록, 상점 테라코타, 촌장 집 벽돌색(`ROOFS`)
  - 외곽선 색 통일(`PALETTE["outline"]`)
  - 출입구를 나무 아치 `gate_arch`로 교체
- **2단계 집 내부**: 컴팩트한 방과 레이아웃 데이터 방식으로 전면 개편
  - 가구 목록(`LAYOUTS`) 하나에서 그림과 충돌을 함께 생성함
- **3단계 필드**
  - 테마별 바닥: 숲은 풀(`grass_`), 협곡은 붉은 흙(`canyon_`), 화산은 화산재(`ash_`)
  - 바위 3종: 붉은 사암(`rock_`), 현무암(`basalt_`), 이끼 바위(`mossrock_`)
  - 용암 가장자리와 굳은 표면(`lava_edge_`), 물가 거품 테두리
  - 장식(`field_decals`), 출입구 아치, 외곽선 있는 상자·제단·제단 입구
  - 북쪽 제단 공터의 테두리를 울타리로 변경
- **NPC 크기 맞춤**
  - 모든 NPC를 주인공과 같은 16×24 비율로 다시 그림(`NPC_SIZE=(32,48)`, 그릴 때 y를 16 올림)
  - 주인공과 NPC에 같은 외곽선(`_outline`)을 적용

- **4단계 UI**
  - `utils/ui.py`에 나무 프레임, 양피지·호두나무색 패널, 체력·마나 막대, 동전, 버튼을 모음
  - 하단 상태창: 지명, HP·MP 막대, 금화를 양피지 위에 표시
  - 대화창은 양피지, 타이틀·상점·전투 메뉴는 호두나무색 프레임
- **광장 주민** 전용 그림(`townsfolk`): 밀짚모자, 하늘색 셔츠, 빵바구니
- **맵 면적 약 30% 확장**
  - 마을 25×16 → 32×21
    - 기존 광장을 `CORE_OFFSET=(3,2)`만큼 옮겨 가운데 배치
    - 바깥 둘레에 과수원, 연못, 텃밭(`crops`), 산책로를 추가
    - 고정 배경은 한 번만 그려 캐시(`_paint_static`)하고, 카메라로 스크롤
  - 북쪽 제단 공터 25×16 → 32×21, 카메라 대응
  - 필드 40×24 → 52×31: 좌표를 1.3배로 옮기고 숲·바위·용암을 추가
  - 연못·용암·바위 무더기는 불규칙한 자연 모양(`_blob`)
  - 장식과 나무 종류는 줄무늬가 생기지 않는 해시(`tile_noise`)로 배치

- **던전·전투 톤 통일**
  - 던전: 제단마다 바닥·벽 팔레트가 다름(바람·대지·불꽃). 벽돌 앞면과 윗면을 구분하고, 횃불·계단(`dstairs`)·장식 추가
  - 던전 대화창이 지도에 가려 안 보이던 문제 수정
  - 적 전용 그림 추가: 고블린, 폭풍 하피, 바위 골렘, 화염 리자드맨. 슬라임은 다시 그리고 흑기사에는 외곽선 추가
  - `fit_sprite`: 적 그림을 정수 배율로만 키워 비율이 찌그러지지 않게 함
  - 전투 배경(`utils/battle_art.py`): 숲, 협곡, 화산, 마을(황혼), 던전 3종. 싸우는 장소에 따라 자동 선택(`BattleScene.backdrop_kind`)

## 확정된 설계 및 규칙
- 그리는 방식: 코드로 그리는 픽셀아트(설계안 A). 화풍은 스타듀풍 아늑한 톤
- 픽셀 단위: 원본 16px/타일을 2배로 키워 32px로 출력. 외곽선은 `PALETTE["outline"]`(54,40,46)
- 실내 규칙
  - 바닥 범위: `HouseInteriorScene.ROOM = (5, 3, 19, 13)`
  - 뒷벽 면은 1~2행
  - 벽에 붙는 가구는 2타일 높이로 그리고, 바닥 쪽 칸만 충돌(`solid_tiles`)
- 마을 좌표는 `VillageScene` 상수만 사용
  - 마을 상수: `START`, `HOUSE_EXITS`, `SHRINE_RETURN`, `SHRINE_SPAWN`, `FIELD_GATES` 등
  - 필드에서 마을로 돌아오는 위치는 `FIELD_ROUTES[*]["return_village"]`
- 마을의 집·촌장 집·상점 그림은 기존 25×16 기준 좌표로 그린 뒤 core 영역에 붙임. 그림 함수 안에서 마을 좌표 상수를 쓸 때는 `CORE_OFFSET`을 빼야 함
- 고정 좌표(테스트에 묶여 있음)
  - NPC 위치: 마르타 (7,6), 가렌·촌장 (12,6)
  - 문 (12,14), 시작 위치 (12,12), 나가기 칸 (12,13)

## 남은 작업
1. 맵 좌표가 바뀌어서, 예전 세이브는 다른 위치에서 이어질 수 있음
   - 막힌 칸이면 안전한 위치로 자동 복구됨
2. 정식 릴리즈(버전 태그, GitHub 릴리즈)는 아직 안 함. 로컬 `dist\ChroniclesOfPixel.exe`만 중간 점검용으로 다시 빌드함

## 핵심 파일
- `utils/pixel_art.py`: 외부 타일과 소품(풀, 흙길, 나무, 울타리, `gate_arch` 등)
- `utils/interior_art.py`: 실내 스프라이트. `interior_sprite(name, scale=2)`, 러그는 `rug_<색>_<w>x<h>` 형식
- `scenes/village_scene.py`: `road_tiles()`, `ground_decals()`, `tree_kind()`, `ROOFS`
- `scenes/house_scene.py`: `LAYOUTS`, `ROOM`, `solid_tiles()`
- `utils/ui.py`: 공용 UI. `FieldScene._draw_hud`, `_draw_dialogue`에서 사용
- `gameplay/world_data.py`: 52×31 필드 데이터
- `utils/battle_art.py`: 전투 배경. `scenes/dungeon_scene.py`의 `floor_tile`, `wall_tile`, `dungeon_decals`
- 테스트: `test_dungeon_battle_art`, `test_pixel_art`, `test_interiors`, `test_field_art`, `test_ui`, `test_map_size`(크기 및 모든 지점 도달 가능 여부)

## 주의사항
- 화면 확인은 `main.Game()._create_world(state)`로 장면을 만들어 렌더링한다. `new_game()`은 세이브를 덮어쓰니 쓰지 않는다.
- 풀(`grass_*`)과 나무(`tree`) 그림은 필드에서도 같이 쓴다. 바꾸면 필드 화면도 함께 확인해야 한다.
