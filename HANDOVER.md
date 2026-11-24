# HANDOVER — Chronicles of Pixel (v0.10.0)

## 현재 상태
- **최신 릴리즈:** v0.10.0 (태그 `v0.10.0`)
  - GitHub 릴리즈: https://github.com/csw94/RPG/releases/tag/v0.10.0 (Actions가 `ChroniclesOfPixel.exe`를 빌드해 첨부)
  - 로컬 EXE `dist\ChroniclesOfPixel.exe`도 같은 태그로 빌드함
- 테스트 128개 모두 통과: `.venv\Scripts\python.exe -m unittest discover -s tests`

## 걷기·대기 애니메이션 (v0.9.0)
- 주인공(`utils/pixel_art.py`의 `_player`):
  - `_hero_head` / `_hero_torso` / `_hero_legs`로 나눔
  - 정면·뒷모습·옆모습이 각각 따로 있고, 왼쪽은 오른쪽을 좌우 반전한 그림
  - 4프레임: 0 서기, 1 왼발, 2 서기, 3 오른발. 걸음을 디딜 때 상체가 1px 내려가고 팔이 흔들림
  - 장면에서는 `walk_frame(self.walk_clock)`을 씀. `walk_clock`은 초당 8씩 늘어남
- NPC: `npc_sprite(name, size, clock, seed)`
  - `idle_pose`가 숨쉬기(2.4초마다 머리가 1px 내려감)와 눈 깜빡임(3.7초마다)을 정함
  - NPC 눈 위치는 (6,8)과 (9,8)로 모두 같다고 가정함
- 적: `enemy_idle(name, box, clock)`이 `(그림, dy)`를 돌려줌
  - 스타일은 `IDLE_STYLES`: squash(슬라임류·버섯), hover(박쥐·하피). 나머지는 숨쉬기
  - 전투 화면과 던전 보스에 적용
- 테스트: `tests/test_walk_animation.py`

## 전투 시스템 개편 (v0.8.0)
- `gameplay/combat.py`의 `BattleEngine`: 한 턴 전체(주인공 행동 → 상태이상 → 적 행동)를 계산하고 이벤트 목록을 돌려줌. pygame 없이 테스트할 수 있음
  - 스킬 6종은 레벨에 따라 배움(`SKILLS`). 속성 약점은 1.5배, 저항은 0.5배. 독·화상·기절, 치명타 8%, 피해량 ±10%
  - 경험치와 레벨업: `FieldScene.gain_xp()`, `xp_to_next(level) = 20 + 15×level`. 레벨이 오를 때 `LEVEL_GAINS`만큼 능력치가 오름
  - 제단을 클리어해도 레벨은 더 이상 오르지 않음(능력치 보너스는 그대로)
- `scenes/battle_scene.py`: 이벤트를 하나씩 재생함. 돌진, 피격 흔들림·흰색 번쩍임, 떠오르는 숫자, 상태 배지, 스킬 목록(Esc로 뒤로), 승패 후 Enter로 계속
- 새 적 8종(`gameplay/enemies.py`, `_enemy()` 헬퍼):
  - 숲: 늑대, 독버섯
  - 협곡: 전갈, 도적
  - 화산: 불도마뱀, 마그마 슬라임
  - 던전: 박쥐, 해골 병사(그림 이름은 `skeleton_warrior`. 기존 `skeleton`은 장식용)
- 새 테스트: `tests/test_combat.py`, `tests/test_battle_scene.py`

## 세이브 위치 보정 (v0.9.2)
- 예전 세이브 위치 보정(`gameplay/save_migration.py`, `tests/test_save_migration.py`)
  - 맵 구조 버전
    - 1: v0.6.x 이하
    - 2: v0.7.0~v0.9.0. 필드 1.3배, 마을·제단 공터 +(3,2)
    - 3: v0.9.1~. 남쪽 필드 상하 반전
  - 이제 세이브에 `layout_version`을 저장함. 버전 기록이 없는 세이브는 DB의 `updated_at`(UTC)을 릴리즈 시각과 비교해 버전을 판별함
  - `SaveManager.load()`에서 변환함. 플레이어 위치, 필드별 열린 상자, 채집한 약초 좌표를 옮김. 던전·실내 좌표는 그대로
  - 맵 구조를 또 바꿀 때는 `LAYOUT_VERSION`을 올리고, `LAYOUT_SINCE`와 `_point_mover`에 단계를 추가할 것
- 아주 옛날 단일 `field` 세이브는 숲길 필드 입구에서 이어서 시작함(`main._create_world`)

## 전투 밸런스 (v0.10.0)
- 전투 밸런스 조정. 숫자는 `tools/balance_sim.py`로 시뮬레이션해서 정함
  - 목표: 필드 전투 3~4턴, 보스전 10~15턴. 지역당 4번 싸우면 보스 승률 약 85%, 5번 이상이면 거의 100%
  - 제단 보너스는 고유 효과만 남김: 바람은 회피 15%, 대지는 최대 HP +40·방어력 +4, 불은 공격력 +6. 공통으로 주던 +30 HP, +5 공격, +3 방어는 없앰(레벨업과 겹쳤기 때문)
  - 전투에서 이기면 MP +2 회복(`combat.VICTORY_MP`). 그전에는 MP를 회복할 방법이 레벨업뿐이었음
  - 던전마다 적 구성이 다름(`SHRINE_DUNGEONS[...]["monsters"]`)
  - 보스 HP: 하피 160, 골렘 260, 리자드맨 300, 말포스 580. 필드 적 HP는 약 20% 올림. 일반 적 경험치는 약 25% 올림
  - 시뮬레이터 실행: `.venv\Scripts\python.exe tools\balance_sim.py [지역당 전투 수] [반복 횟수]`

## 릴리즈 기록
- **v0.10.0:** 전투 밸런스를 다시 조정함. 제단 보너스는 고유 효과만 남김, 승리 시 MP +2, 던전별 적 구성, 보스 강화. `tools/balance_sim.py` 추가
- **v0.9.2:** 예전 세이브의 위치를 현재 맵에 맞게 자동 보정. 세이브에 `layout_version`을 저장함
- **v0.9.1:** 상점 테두리를 나무 프레임으로 통일. 남쪽 화산 필드를 위에서 아래로 내려가는 구조로 뒤집음
- **v0.9.0:** 주인공 방향별 4프레임 걷기, NPC 숨쉬기·눈 깜빡임, 적 대기 동작(위 절 참고)
- **v0.8.0:** 전투 개편. 스킬, 속성, 상태이상, 경험치와 레벨업, 지역별 적 8종, 전투 연출(위 절 참고)
- **v0.7.2:** 타이틀 화면을 "밤의 오크밸리" 장면으로 바꿈(`utils/title_art.py`). 별·반딧불이 애니메이션, 나무 판자 하단 띠 포함
- **v0.7.1:** 마을 건물 사이에 걸어갈 수 있는 통로를 확보함(오두막↔촌장 집 3칸, 촌장 집↔잡화점 2칸)
- **v0.7.0:** 그래픽 전면 개편, UI, 맵 30% 확장, 던전·전투 톤 통일(아래 "완료된 작업" 참고)

## 완료된 작업 (v0.6.3 → v0.7.0)
1. **마을 외부**
   - 체커보드 없는 풀 타일, 테두리 있는 흙길
   - 나무 3종(둥근 나무, 과일나무, 침엽수), 꽃·조약돌 장식, 나무 울타리, 그림자
   - 지붕 색 통일(`ROOFS`): 오두막 청록, 상점 테라코타, 촌장 집 벽돌색
   - 출입구는 나무 아치(`gate_arch`)
2. **집 내부**
   - 아담한 방으로 줄이고, 집마다 테마를 줌: 약초상 오두막, 노기사 거처, 촌장 집무실
   - 가구 목록(`LAYOUTS`) 하나에서 그림과 충돌을 함께 만듦
3. **필드**
   - 테마별 바닥: 숲은 풀(`grass_`), 협곡은 붉은 흙(`canyon_`), 화산은 화산재(`ash_`)
   - 바위 3종: 붉은 사암(`rock_`), 현무암(`basalt_`), 이끼 바위(`mossrock_`)
   - 굳은 표면이 있는 용암(`lava_edge_`), 거품 테두리가 있는 물가
4. **캐릭터**
   - NPC를 주인공과 같은 16×24 비율로 다시 그림(`NPC_SIZE=(32,48)`)
   - 공통 외곽선(`_outline`) 적용
   - 광장 주민 전용 그림(`townsfolk`)
5. **UI**(`utils/ui.py`)
   - 하단 상태창과 대화창은 나무 프레임 + 양피지
   - 타이틀·상점·전투 메뉴와 버튼은 호두나무색 프레임
6. **맵 면적 약 30% 확장**
   - 마을과 북쪽 제단 공터: 25×16 → 32×21
   - 필드 3곳: 40×24 → 52×31
7. **던전과 전투**
   - 던전: 제단마다 바닥·벽 팔레트가 다르고, 벽 앞면·윗면 구분, 횃불, 계단, 장식
   - 적 전용 그림: 고블린, 하피, 골렘, 리자드맨. 슬라임을 다시 그리고 흑기사에 외곽선 추가
   - 전투 배경 7종, 싸우는 장소에 따라 자동 선택
   - 던전에서 대화창이 가려지던 버그 수정

## 확정된 설계 및 기술 규칙
- **아트**
  - 코드로 그리는 픽셀아트(설계안 A). 외부 이미지 에셋은 쓰지 않음
  - 원본 16px/타일을 2배로 키워 32px로 출력
  - 외곽선 색은 `PALETTE["outline"]`(54,40,46)
  - 캐릭터·소품은 `_outline()`으로 외곽선을 넣음. 반투명 그림자에는 넣지 않음
  - 적 그림은 `fit_sprite()`로 정수 배율로만 키움(비율 유지)
  - 무작위 배치(장식, 바닥 변형, 나무 종류)는 줄무늬가 생기지 않도록 `tile_noise(x, y, seed)`로 함
- **마을**(`VillageScene`)
  - 기존 25×16 광장(core)을 `CORE_OFFSET=(3,2)`만큼 옮겨 둠
  - 집·촌장 집·상점 그림 함수는 core 좌표 기준. 그 안에서 마을 좌표 상수를 쓸 때는 `CORE_OFFSET`을 빼야 함
  - 좌표는 숫자로 직접 쓰지 말고 상수를 씀: `START`, `HOUSE_EXITS`, `SHRINE_RETURN`, `SHRINE_SPAWN`, `FIELD_GATES`
  - 건물 충돌 영역은 `BUILDINGS`(x, y, w, h). 양옆 집을 그리는 위치는 `HOUSE_TILES`(마을 좌표)
  - 건물 사이에는 걸어갈 수 있는 통로를 2칸 이상 둠. 현재 오두막↔촌장 집 x 8~10, 촌장 집↔잡화점 x 20~21이고, `test_map_size`가 검사함
  - core 좌표로 그리는 것은 촌장 집, 로건 노점, 분수뿐
  - 고정 배경은 `_paint_static()`으로 한 번만 그려 캐시
- **필드**
  - 데이터는 `gameplay/world_data.py`의 `FIELD_ROUTES`(52×31)
  - 마을로 돌아오는 위치는 `return_village`
  - 연못·용암·바위 무더기는 `FieldScene._blob()`으로 불규칙한 모양을 만듦
  - 남쪽 화산 필드는 위에서 아래로 내려가는 구조임. 마을 문이 맨 위 (16,1), 불꽃 신전이 맨 아래 (29,27). `test_south_field_runs_downhill_from_the_village`가 검사함
- **실내**(`HouseInteriorScene`)
  - 바닥 범위는 `ROOM = (5, 3, 19, 13)`, 뒷벽 면은 1~2행
  - 벽에 붙는 가구는 2타일 높이로 그리고, 바닥 쪽 칸만 충돌(`solid_tiles`)
  - 테스트에 묶인 실내 좌표: 마르타 (7,6), 가렌·촌장 (12,6), 문 (12,14), 시작 (12,12), 나가기 칸 (12,13)
- **던전**
  - 크기 25×16은 손으로 짠 미로 구조라 그대로 유지
  - 타일 결정은 `floor_tile()`, `wall_tile()`(아래가 바닥이면 앞면), `dungeon_decals()`
- **릴리즈**: CLAUDE.md 절차를 따름. 이 PC에는 `gh` CLI가 없어서, Actions와 릴리즈 확인은 `api.github.com`(공개 API)을 curl로 조회함

## 미릴리즈 변경 (다음 릴리즈에 포함)
- 침대 휴식: 마르타 오두막과 가렌 거처의 침대 옆에서 SPACE를 누르면 HP·MP가 모두 회복되고 저장됨(무료, `HouseInteriorScene._rest`)
- 상태 화면: I 또는 Tab 키로 열림(`scenes/status_scene.py`). 능력치와 그 출처, 장비, 소지품, 기술(미습득은 ??? 표시), 제단 인장, 부탁 진행도를 보여줌
- 소리(`utils/audio.py`)
  - 오디오 파일 없이 코드로 합성함. 사각파·삼각파·노이즈, `array('h')`, 22050Hz. numpy를 쓰지 않음
  - 효과음 21종(`SFX`)
    - 장면에서는 `BaseScene.sfx(name)`으로 재생함. `game.audio`가 없으면 조용히 넘어감
    - 전투 효과음은 `BattleScene._cue`가 이벤트 종류에 맞춰 고름
  - 배경음악 6곡(`MUSIC`: title, village, field, dungeon, battle, boss)
    - 직접 작곡한 짧은 반복곡이고, 시작할 때 백그라운드 스레드에서 미리 만들어 둠
    - 곡 선택은 `music_for(scene_name, enemy_id)`가 하고, 매 프레임 `Game.run`에서 갱신함. 상점·상태 화면에서는 원래 곡을 유지함
  - M 키로 음소거. 오디오 장치가 없으면 소리 없이 그대로 진행됨

## 남은 작업 및 아이디어
- 필수로 남은 작업은 없음
- 선택 과제
  - 전투 연출(타격 흔들림, 데미지 숫자)이나 캐릭터 걷기 애니메이션 보강

## 핵심 파일
| 파일 | 내용 |
|---|---|
| `utils/pixel_art.py` | 바깥 타일·소품, 캐릭터·적, 던전 타일, `tile_noise`, `fit_sprite` |
| `utils/interior_art.py` | 실내 스프라이트. `interior_sprite(name, scale=2)`, 러그는 `rug_<색>_<w>x<h>` 형식 |
| `utils/ui.py` | 공용 UI: 프레임, 막대, 버튼, 판자 띠 |
| `utils/battle_art.py` | 전투 배경 `backdrop(kind)`, 발판 위치 상수 |
| `utils/title_art.py` | 타이틀 배경 `backdrop()`과 애니메이션 `draw_overlay(surface, clock)` |
| `scenes/field_scene.py` | 필드 공통 로직: 테마, 장식, `_blob`, HUD, 대화창 |
| `scenes/village_scene.py` | 마을 레이아웃, 정적 레이어 캐시 |
| `scenes/house_scene.py` | `LAYOUTS`, `ROOM`, `solid_tiles()` |
| `scenes/dungeon_scene.py` | 던전 레이아웃과 타일 그리기 |
| `scenes/battle_scene.py` | `backdrop_kind()`, 전투 그리기 |
| `gameplay/world_data.py` / `gameplay/enemies.py` | 필드 데이터 / 적 데이터(스프라이트 이름, 표시 크기) |
| `tests/` | `test_pixel_art`, `test_interiors`, `test_field_art`, `test_ui`, `test_map_size`, `test_dungeon_battle_art`, `test_title_art` 및 기존 테스트 |

## 주의사항
- 화면 확인은 `main.Game()._create_world(state)`로 장면을 만들어 렌더링한다. `new_game()`은 세이브를 덮어쓰니 쓰지 않는다.
- 풀(`grass_*`)과 나무 그림은 마을·필드·제단 공터가 같이 쓴다. 바꾸면 세 화면을 모두 확인해야 한다.
- 실행 확인용으로 EXE를 띄운 뒤에는 `Get-Process ChroniclesOfPixel`로 남은 프로세스까지 모두 종료한다. 단일 파일 빌드라 자식 프로세스가 따로 남는다.
- git 명령에는 `-c safe.directory=C:/Users/dongb/IdeaProjects/RPG`를 붙이고, 작성자는 `Codex <codex@openai.com>`로 한다.
