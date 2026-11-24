# HANDOVER — Chronicles of Pixel (v0.15.0)

## 현재 상태
- **최신 릴리즈:** v0.15.0 (태그 `v0.15.0`)
  - GitHub 릴리즈: https://github.com/csw94/RPG/releases/tag/v0.15.0 (Actions가 `ChroniclesOfPixel.exe`를 빌드해 첨부)
  - 로컬 EXE `dist\ChroniclesOfPixel.exe`도 같은 태그로 빌드함
- 테스트 227개 모두 통과: `.venv\Scripts\python.exe -m unittest discover -s tests`

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

## 휴식·상태 화면·소리 (v0.11.0)
- 침대 휴식: 마르타 오두막과 가렌 거처의 침대 옆에서 SPACE를 누르면 HP·MP가 모두 회복되고 저장됨(무료, `HouseInteriorScene._rest`)
- 상태 화면: I 또는 Tab 키로 열림(`scenes/status_scene.py`). 능력치와 그 출처, 장비, 소지품, 기술(미습득은 ??? 표시), 제단 인장, 부탁 진행도를 보여줌
- 소리(`utils/audio.py`)
  - 오디오 파일 없이 코드로 합성함. 사각파·삼각파·노이즈, `array('h')`, 22050Hz. numpy를 쓰지 않음
  - 효과음 21종(`SFX`)
    - 장면에서는 `BaseScene.sfx(name)`으로 재생함. `game.audio`가 없으면 조용히 넘어감
    - 전투 효과음은 `BattleScene._cue`가 이벤트 종류에 맞춰 고름
  - 배경음악 7곡(`MUSIC`: title, village, field, dungeon, battle, boss, final)
    - 직접 작곡한 짧은 반복곡이고, 시작할 때 백그라운드 스레드에서 미리 만들어 둠
    - 곡 선택은 `music_for(scene_name, enemy_id)`가 하고, 매 프레임 `Game.run`에서 갱신함. 상점·상태 화면에서는 원래 곡을 유지함
  - M 키로 음소거. 오디오 장치가 없으면 소리 없이 그대로 진행됨. 음량은 설정 화면에서 조절함

## 패배 후 선택·최종 보스 2페이즈 (v0.12.0)
- 패배 화면에서 "다시 도전"과 "마을로 돌아가기" 중 고름
  - `BattleScene.snapshot`은 전투 시작 직전의 `field.serialize()`임
  - 다시 도전하면 `Game.retry_battle(snapshot, enemy_id)`가 그 상태를 복원하고 같은 적과 다시 싸우게 함
- 최종 보스 2페이즈(`BattleEngine.phase`, `_check_phase`)
  - 흑기사 말포스의 HP가 절반 이하가 되면 한 번만 발동함. 상태이상 해제, 암흑 베기 +8, 어둠의 파동이 2턴마다 24 피해
  - 연출: 화면 번쩍임, 보랏빛 하늘, 보스 뒤의 기운, 효과음 `phase`, 전용 곡 `final`
  - `BattleScene.music_track`이 장면 기본 곡을 덮어씀(`Game.run`)
  - 시뮬레이터 결과: 지역당 4회 싸웠을 때 최종 보스 승률 약 81%, 5회 이상이면 100%

## 조작법·설정 화면 (v0.13.0)
- 타이틀 메뉴: 새 모험 시작 / 모험 이어하기 / 조작법 / 설정 / 게임 종료. `_choose_menu`는 순서가 아니라 메뉴 이름으로 동작을 고름
- 조작법 화면(`scenes/help_scene.py`): `CONTROLS`와 `TIPS` 목록을 그대로 그림. 키를 추가하면 이 목록과 README도 고칠 것
- 설정 화면(`scenes/settings_scene.py`): 타이틀 메뉴나 필드에서 O 키로 열림
  - 배경음악과 효과음 음량을 0~10 단계로 조절함(`Audio.set_volumes`)
  - 화면 크기는 1x, 1.5x, 2x, 전체 화면 중에서 고름
  - 설정은 `%APPDATA%/ChroniclesOfPixel/settings.json`에 저장됨(`utils/user_settings.py`)
- 화면 확대(`utils/display.py`)
  - 모든 장면은 800×600 `Game.canvas`에 그림. `Game.present()`가 이를 창 크기로 확대해서 그리고(nearest), 전체 화면에서는 4:3 비율로 가운데 맞춤
  - 마우스 좌표는 `display.map_events`가 캔버스 좌표로 바꿈. 장면 코드는 계속 800×600 좌표만 쓰면 됨
  - 모니터에 들어가지 않는 창 크기는 `available_modes`가 목록에서 뺌
- README를 현재 게임 내용에 맞게 다시 씀

## 장비 다양화 (v0.14.0)
- 데이터는 `gameplay/equipment.py`
  - 무기: `element`(일반 공격에 속성 적용), `crit`(치명타 확률 추가), `proc`(상태, 확률, 턴). 보스는 기절 확률이 절반
  - 방어구: `health`, `mp`, `immune`
  - 장신구 `ACCESSORIES`: `attack`, `evasion`, `victory_mp`, `immune`
  - 기존 ID(iron_sword, silver_sword, leather_armor, chainmail)는 예전 세이브를 위해 남겨 둠
- 장신구 칸이 새로 생김: 세이브에 `accessory`, `owned_accessories` 추가. 예전 세이브는 장신구 없음(None)으로 시작함
- `FieldScene`
  - 장비 정보: `weapon_info`, `armor_info`, `accessory_info`
  - 능력치: `attack_power`(장신구 공격력 포함), `evasion`(바람의 가호 + 장신구), `immunities`
  - `equip(kind, id)`는 방어구의 최대 HP·MP 차이를 함께 반영함
- 상점(`scenes/shop_scene.py`)
  - 무기·방어구·장신구·소모품 탭으로 나뉨
  - 파는 물건은 `shop_stock(정화한 제단 수, 종류)`로 정함. `tier`는 그 물건이 나오는 데 필요한 제단 수
  - 이미 가진 장비는 무료로 다시 장착할 수 있음
- 별빛의 검은 빛 속성. 주인공 그림의 칼날 색이 무기에 따라 바뀜(`_hero_torso`의 `blade`)
- 시뮬레이터는 강철 장검과 흉갑만 사도록 되어 있음. 새 장비를 쓰면 시뮬레이션 결과보다 조금 쉬워짐

## 북쪽 제단 그리는 순서 수정 (v0.14.1)
- 북쪽 제단 공터의 그리는 순서를 고침(`ShrineClearingScene`)
  - 고치기 전에는 제단 받침·기둥·분수·아치를 주인공 위에 무조건 덮어 그려서, 제단 앞에 선 주인공이 가려졌음
  - 지금은 받침(바닥)을 먼저 깔고, 기둥 4개·분수·남쪽 아치·주인공을 발 위치 기준으로 뒤에서 앞 순서로 그림(`_depth_items`, `depth_order`)
  - 주인공은 제단 주변(`HERO_ZONE`), 남쪽 문 근처, 맨 위 울타리 바로 아래에 있을 때만 다시 그림
  - 테스트: `tests/test_shrine_clearing_depth.py`

## CI·별빛 심연·지도·서브퀘스트 (v0.15.0)
- CI와 릴리즈 자동화(`.github/workflows/ci.yml`, `release.yml`, `tools/release_notes.py`)
  - `main`에 푸시할 때마다 테스트가 돌아감
  - 태그를 푸시하면 테스트 → EXE 빌드 → 릴리즈 순서로 진행함. 릴리즈 노트는 이 파일의 "릴리즈 기록" 줄(`- **vX.Y.Z:** ...`)에서 가져오므로, **태그를 만들기 전에 릴리즈 기록을 먼저 적을 것**
  - Python은 로컬과 같은 3.14. `test_release_tooling`이 버전이 같은지 검사함
- 엔딩 후 던전 별빛 심연(`POSTGAME_DUNGEONS["shrine_abyss"]`, 3층)
  - `DUNGEONS = SHRINE_DUNGEONS + POSTGAME_DUNGEONS`. 층 수는 `floors`, 층별 상자는 `floor_chests`로 정함. 층이 3개 이상인 던전에서는 EXIT가 위층, STAIRS가 아래층으로 이어짐
  - 입구는 북쪽 제단. 최종 보스를 쓰러뜨린 뒤 제단을 조사하면 `enter_abyss`가 실행됨. 제단 공터로 나올 때는 `return_pos`에 놓임
  - 적 3종과 보스 `abyss_lord`는 기존 그림을 `_abyssal()`로 보랏빛으로 바꾼 것. 보스 패턴 `abyss`는 3턴마다 52 고정 피해
  - 보상: 2층 상자 `accessory:star_amulet`, 보스 처치 시 `abyss_crown` + 500G. 플래그는 `quest_flags["abyss_lord"]`
  - 시뮬레이션(본편을 지역당 5회씩 싸우고 클리어, 용비늘 갑옷·힘의 팔찌 장착 가정): 층마다 2번 싸우면 보스 승률 약 45%, 4번이면 약 90%
- 지도 페이지와 다음 목표
  - 상태 화면에서 ←→로 기록과 지도를 오감(`StatusScene.page`)
  - 장면마다 `map_markers()`로 표시할 지점을 넘겨줌. 다음 목표는 `gameplay/objectives.py`의 `next_objective`
- 서브퀘스트 3개 추가: 숲의 사냥꾼(광장 주민, 숲늑대 4), 용암석 수집(로건, 제단을 하나 정화한 뒤, 마그마 슬라임 3), 동굴 소탕(가렌, 옛 검 부탁을 마친 뒤, 동굴 박쥐 4)
  - 처치 수를 세는 부탁은 `KILL_QUESTS` 표에, 보상은 `QUEST_REWARDS` 표에 있음
  - 보상 장신구: 늑대 송곳니 부적(치명타 +10%), 용암석 팔찌(공격 +3, 화상 면역), 수호자의 훈장(방어 +5). 이제 장신구가 치명타와 방어력도 올릴 수 있음

## 릴리즈 기록
- **v0.15.0:** 엔딩 후 도전 던전 「별빛 심연」(3층, 숨겨진 보스와 전용 장신구), 상태 화면의 지도 페이지와 다음 목표 안내, 마을 부탁 3개 추가(전용 장신구 보상), CI 자동 테스트와 릴리즈 노트 자동화
- **v0.14.1:** 북쪽 제단에서 주인공이 제단·기둥에 가려지던 문제 수정(깊이 순서로 그리기)
- **v0.14.0:** 장비 다양화. 속성 무기 3종, 방어구 2종, 장신구 칸과 장신구 4종, 탭으로 나뉜 상점, 제단 진행도에 따라 늘어나는 상품
- **v0.13.0:** 타이틀의 조작법 화면, 설정 화면(음량·화면 크기·전체 화면), README 갱신
- **v0.12.0:** 패배 후 다시 도전 선택지, 최종 보스 2페이즈(연출·전용 곡 포함)
- **v0.11.0:** 침대 휴식, 상태 화면(I/Tab), 코드로 만든 효과음과 배경음악(M으로 음소거)
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

## 남은 작업 및 아이디어
- 필수로 남은 작업은 없음
- 선택 과제
  - 직접 플레이한 뒤의 피드백 반영: 소리 음량·곡 분위기(`SFX_VOLUME`, `MUSIC_VOLUME`, `MUSIC`), 난이도(`tools/balance_sim.py`로 다시 측정)

## 핵심 파일
| 파일 | 내용 |
|---|---|
| `utils/pixel_art.py` | 바깥 타일·소품, 캐릭터·적, 던전 타일, `tile_noise`, `fit_sprite` |
| `gameplay/combat.py` | 전투 규칙 `BattleEngine`(이벤트 반환), 스킬, 레벨업, 최종 보스 페이즈 |
| `gameplay/save_migration.py` | 예전 세이브의 좌표를 현재 맵 구조로 변환 |
| `utils/audio.py` | 코드로 만든 효과음과 배경음악, `music_for` |
| `scenes/status_scene.py` | 상태 화면(I/Tab) |
| `scenes/settings_scene.py` / `scenes/help_scene.py` | 설정 화면(O) / 조작법 화면 |
| `utils/display.py` / `utils/user_settings.py` | 창 크기 확대와 마우스 좌표 변환 / 설정 파일 |
| `tools/balance_sim.py` | 전투 밸런스 시뮬레이터 |
| `tools/release_notes.py` / `.github/workflows/` | 릴리즈 노트 추출 / CI 테스트와 릴리즈 빌드 |
| `gameplay/objectives.py` | 다음 목표 안내 |
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
