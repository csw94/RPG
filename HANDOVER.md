# HANDOVER — Chronicles of Pixel (v0.24.0)

## 현재 상태
- **최신 릴리즈:** v0.24.0 (태그 `v0.24.0`)
  - 릴리즈: https://github.com/csw94/RPG/releases/tag/v0.24.0 , https://github.com/csw94/Star/releases/tag/v0.24.0 (같은 로컬 빌드 `ChroniclesOfPixel.exe`를 `gh`로 두 곳에 올림)
  - 소스 저장소 `csw94/RPG`는 아직 공개(비공개 전환 보류). 배포용 공개 저장소 `csw94/Star`에는 README와 EXE 릴리즈만 있음. 절차는 CLAUDE.md 참고
  - 로컬 EXE `dist\ChroniclesOfPixel.exe`도 같은 태그로 빌드함
- 테스트 399개 모두 통과: `.venv\Scripts\python.exe -m unittest discover -s tests`

## 그래픽 개편·시작 연출·세이브 삭제 (v0.24.0)
- 주인공 새 디자인(`utils/pixel_art.py`)
  - `_HERO_HEAD`/`_HERO_TORSO` 픽셀 문자 격자와 `_paint`로 그림. 구리빛 머리, 빨간 스카프(`HERO["scarf"]`)
  - 튜닉 색은 갑옷 6종마다 다름(`HERO_ARMOR`). 옆모습 스카프 끝은 걸음마다 날림(`_SCARF_TAIL`)
- 집 부품 조합(`utils/house_art.py`)
  - `HOUSE_STYLES` 6채: 벽 재질, 지붕 모양(gable/hip/gambrel/thatch), 창문, 문, 소품
  - 너비는 5칸 또는 7칸만 씀(홀수여야 문이 타일 가운데에 옴)
  - `general_store` 키는 실제로 가렌의 거처라 `knight_quarters`로 바꿈(방패 문장, 무기 걸이). 로건은 광장 노점 상인
- 비대칭 배치(맵 구조 4)
  - `village_scene.PLACES`(집 그림 기준 타일) → `house_plot(key)`이 벽 영역과 문 좌표를 계산함
  - `BUILDINGS`, `DISTRICT`, `HOUSE_EXITS`가 모두 여기서 나옴
  - 나무는 집 그림과 겹치면 자동으로 빠짐. 길은 `road_tiles()`에 절대 좌표로 적음
  - `save_migration.LAYOUT_VERSION = 4`: 예전 문 앞 좌표를 새 문 앞으로 옮김(`VILLAGE_DOORS_V4`)
  - 촌장 집, 분수, 시작 위치, 로건, 출입구 4곳은 그대로
- 새 게임 시작 연출(`gameplay/intro.py` `ChiefCallIntro`, `VillageScene.update`)
  - 단계: 페이드 인 → 토미가 뛰어옴 → 대화 → 촌장 집 문 앞까지 안내(문 위 "!") → 문 앞에서 대기
  - 새 게임만 `quest_flags["intro_seen"]=0`을 저장함. 이 값이 없는 예전 세이브에서는 연출이 나오지 않음
  - `FieldScene.input_locked`, `skip_cutscene()`, `dialogue_done(action)`은 다른 장면에서도 쓸 수 있는 일반 연결점
- 세이브 삭제: 타이틀 슬롯 화면의 휴지통 버튼 또는 Del 키 → 예/아니오 확인 → `SaveManager.delete(slot)`
- 새 테스트: `test_house_art`, `test_village_layout`, `test_intro`, `test_save_delete`. 걷기 테스트에도 추가함
- 배포 방식 변경: 태그 푸시 릴리즈 워크플로(`release.yml`)를 없애고, 로컬 EXE를 `gh`로 RPG와 배포용 공개 저장소 `csw94/Star`에 같이 올림

## 걷기·대기 애니메이션 (v0.9.0)
- 주인공(`utils/pixel_art.py`의 `_player`):
  - (v0.24.0에서 다시 그림: 머리·몸통은 `_HERO_HEAD`/`_HERO_TORSO` 격자, 팔은 `_hero_arms`, 다리는 `_hero_legs`. 아래 프레임 규칙은 그대로)
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
- 별빛의 검은 빛 속성. 주인공 그림의 칼날 색이 무기에 따라 바뀜(`HERO_BLADES`)
- 시뮬레이터는 강철 장검과 흉갑만 사도록 되어 있음. 새 장비를 쓰면 시뮬레이션 결과보다 조금 쉬워짐

## 북쪽 제단 그리는 순서 수정 (v0.14.1)
- 북쪽 제단 공터의 그리는 순서를 고침(`ShrineClearingScene`)
  - 고치기 전에는 제단 받침·기둥·분수·아치를 주인공 위에 무조건 덮어 그려서, 제단 앞에 선 주인공이 가려졌음
  - 지금은 받침(바닥)을 먼저 깔고, 기둥 4개·분수·남쪽 아치·주인공을 발 위치 기준으로 뒤에서 앞 순서로 그림(`_depth_items`, `depth_order`)
  - 주인공은 제단 주변(`HERO_ZONE`), 남쪽 문 근처, 맨 위 울타리 바로 아래에 있을 때만 다시 그림
  - 테스트: `tests/test_shrine_clearing_depth.py`

## CI·별빛 심연·지도·서브퀘스트 (v0.15.0)
- CI와 릴리즈 노트(`.github/workflows/ci.yml`, `tools/release_notes.py`). 예전 `release.yml`(태그 푸시 시 Actions 빌드)은 v0.24.0 이후 삭제함
  - `main`에 푸시할 때마다 테스트가 돌아감
- 릴리즈는 로컬에서 빌드한 EXE를 `gh release create`로 RPG와 Star 두 곳에 올림. 릴리즈 노트는 이 파일의 "릴리즈 기록" 줄(`- **vX.Y.Z:** ...`)에서 가져오므로, **릴리즈 전에 릴리즈 기록을 먼저 적을 것**
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

## 서리 고원과 네 번째 제단 (v0.16.0)
- 제단이 4개가 됨: `gameplay/world_data.SHRINES`에 얼음 제단을 추가함. 북쪽 길은 `NORTH_UNLOCK`(2곳)을 정화하면 열림
  - 별빛의 검은 인장 4개가 있어야 깨어남. 단, 이미 3개로 깨운 예전 세이브는 그대로 유지함(`check_fountain_awakening`)
  - 얼음의 가호: 최대 MP +12, 방어력 +2. 촌장·분수·에필로그·목표 안내·상태 화면·상점 단계가 모두 4개 기준
- 서리 고원(`FIELD_ROUTES["field_north"]`, 테마 `snow`)
  - 북쪽 제단 공터의 `NORTH_GATE`(15,1)로 들어감. 잠겨 있을 때는 아치에 얼음판이 그려짐
  - 돌아올 때는 route의 `home` 값(`village_north_shrine`)으로 감
  - 지형: 얼어붙은 호수 `FieldScene.ice`(`ice_edge_*`), 눈 바닥 `snow_*`, `tree_snowpine`, `icerock_*`
  - 적: 서리 늑대(그림 이름 `frost_wolf`. `snow_` 접두사는 바닥 타일이 쓰므로 피함), 얼음 슬라임, 서리 정령(새로 그림). 얼음 슬라임·늑대는 `_frosted()`로 기존 그림을 바꾼 것
- 빙결(`freeze` 패턴): 25% 확률로 주인공에게 기절(1턴)을 걸어 다음 행동을 건너뛰게 함. 바로 다시 얼지는 않음(`BattleEngine.thawed`). 라운드 후반 처리는 `_round_tail`로 분리함
- 얼음 제단(`SHRINE_DUNGEONS["shrine_ice"]`, 2층): 보스 빙결 리자드킹(`blizzard` 패턴: 3턴마다 눈보라 30 피해, 35% 확률로 빙결)
- 밸런스: 시뮬레이터 지역 순서를 동 → 서 → 북 → 남으로 바꿈. 지역이 늘어난 만큼 불꽃 신전(HP 360)과 말포스(HP 720, 공격 58)를 강화함. 지역당 4번 싸우면 보스 승률 약 95%

## 서리 고원 마무리·고레벨 스킬 (v0.17.0)
- 필드 NPC를 일반화함: route의 `npc` 값(`{"pos", "sprite", "quest"}`)으로 정함. 토비는 예전의 `toby` 키로 그대로 동작함. 코드 안에서는 `FieldScene.field_npc`와 `toby_position`(NPC 위치)을 씀
- 서리 고원 사냥꾼 하른(새 그림 `hunter`, (24,20)): 부탁 `sq_frost_hunt`(서리 정령 4마리). 보상은 `frost_heart`(빙결 면역, 공격 +2)와 120G
- 상점이 제단을 정화할 때마다 늘어남
  - 제단 2곳: 따뜻한 목도리(빙결 면역, 회피 +3%)
  - 제단 3곳: 폭풍 할버드(바람 속성, 공격 18, 치명타 +6%)
  - 제단 4곳: 오로라 갑옷(방어 14, HP +40, MP +8)
  - 빙결 면역은 `immune: "stun"`으로 표현함
- 고레벨 스킬: 별빛 폭풍(Lv.10, MP 10, 빛 속성, 위력 30), 성스러운 기도(Lv.12, MP 12, 회복 160 + 레벨×4, 상태이상 해제). 전투 화면 스킬 버튼은 4열, 상태 화면 기술 목록은 3열
- 별빛 심연 재조정: 지역이 늘고 스킬이 생겨 쉬워졌기 때문에 강화함(녹스 HP 1100, 공격 86. 심연 적 HP·공격 약 10~15% 상승). 층마다 2번 싸우면 보스 승률 약 60%, 4번이면 약 80%, 6번이면 약 90%

## 플레이 기록·퀘스트 데이터 정리 (v0.18.0)
- 플레이 기록: 세이브에 `play_time`(초)과 `stats`(wins, losses, flees)를 저장함
  - 시간은 `Game.count_play_time`이 셈. 타이틀 화면에서는 세지 않음
  - 전투 결과는 `BattleEngine._tally`가 셈
  - 세이브 슬롯 카드에는 `gameplay/records.slot_summary`로 레벨·플레이 시간·인장 수·엔딩 여부를 표시함. 엔딩 카드에는 `EpilogueScene.record_rows`로 플레이 시간과 전투 승리 수를 표시함
- 퀘스트 데이터: 부탁 7개의 이름, 목표 수, 처치 대상(`kill`), 필요 아이템(`requires_item`), 대사(`offer`/`done`), 보상(`reward`)이 `gameplay/quests.py`의 `QUESTS` 한 곳에 있음
  - **부탁을 추가하는 법**
    1. `QUESTS`에 항목을 추가함
    2. 의뢰인 NPC를 만지는 장면에서 `self._offer_sidequest("sq_...")`를 호출함
    3. 처치형 부탁이면 `kill`만 적으면 진행도가 자동으로 오름
  - 세이브의 `sub_quests`, 상태 화면 이름, 보상 지급은 모두 이 표를 따름. `test_quest_data`가 표의 일관성과 보상 지급을 검사함

## 난이도·도감·자동 저장 (v0.19.0)
- 난이도(`gameplay/difficulty.py`): `DIFFICULTIES`의 easy/normal/hard 배율(`enemy_hp`, `damage`, `gold`)
  - 적 HP는 `BattleEngine.__init__`에서, 받는 피해는 `_hit_hero`에서, 골드는 `resolve_battle_victory`에서 배율을 곱함
  - 세이브에 `difficulty`를 저장함. 예전 세이브와 잘못된 값은 normal로 처리함
  - 타이틀에서 슬롯을 고른 뒤 `mode == "difficulty"`로 난이도를 고름. 모험 중에 설정 화면을 열면 난이도 줄이 추가됨(`SettingsScene.rows`)
  - 밸런스 시뮬레이터는 normal 기준
- 도감: 세이브에 `bestiary`({적 id: 처치 수}, 0이면 만나기만 함)를 저장함. 전투를 시작할 때 등록되고, 이기면 수가 오름
  - 상태 화면 세 번째 페이지(`PAGES`)에 6열 그리드로 표시함
  - 장비 수집 수는 `LEGACY_IDS`를 뺀 전체 장비 기준
- 자동 저장: `main.AUTOSAVE_SECONDS`(60초)마다 `Game.tick_autosave`가 저장함
  - 장면이 필드 계열일 때만 저장하고, 대화 중이면 대화가 끝난 뒤로 미룸
  - 저장하면 HUD에 "자동 저장됨"이 표시됨(`autosave_flash`)
  - 창을 닫을 때는 `Game.shutdown`이 모험 중이면 저장함

## 업적·회차 플레이·조작 편의 (v0.20.0)
- 업적(`gameplay/achievements.py`): `ACHIEVEMENTS`에 14개가 있고, 각각 `check(field)` 함수로 달성 여부를 판정함
  - 판정은 `Game.save_game`이 저장할 때마다 `check_achievements`를 호출해서 함. 새로 달성하면 효과음이 나고, `field.achievement_toasts`에 쌓인 알림을 HUD가 3초씩 차례로 띄움
  - 세이브에 `achievements` 목록을 저장함. 상태 화면 네 번째 페이지에 표시됨
- 회차 플레이(`gameplay/new_game_plus.py`)
  - 엔딩 후 촌장 대화의 `offer_new_game_plus`가 `ConfirmScene`(예/아니오, 기본값은 아니오)을 띄움. 예를 고르면 `Game.start_new_game_plus`가 같은 슬롯에서 다음 회차를 시작함
  - 이어지는 항목은 `CARRIED` 목록. 나머지(이야기 플래그, 부탁, 상자, 약초, 중요 물품, 위치)는 초기화됨. `prologue_done`은 1로 시작함
  - `cycle`이 오를 때마다 `cycle_multipliers`가 적용됨: 적 HP +160%, 받는 피해 +60%, 골드·경험치 +30%(v0.23.0에서 조정). `difficulty_of`가 난이도 배율과 곱해서 돌려줌(`xp` 키 추가)
  - 시뮬레이터 `--plus` 결과: 2회차 제단 보스는 넘겨받은 주인공이 쉽게 이기고, 최종 보스 승률은 약 75%
- 조작 편의
  - 대화 타자 효과: `TEXT_SPEEDS`(초당 18/40/90 글자 또는 즉시)
    - 설정의 `text_speed`(settings.json)로 속도를 정함
    - 행동 키를 누르면 `_press_dialogue`가 먼저 줄을 완성하고, 다시 누르면 다음 줄로 넘어감
  - 필드와 실내에서 Enter와 Z도 스페이스와 같은 행동 키(`ACTION_KEYS`)
  - 완전한 키 재설정은 하지 않음. 모든 장면이 키를 직접 확인하고 있어서 입력 처리를 한곳으로 모으는 작업이 먼저 필요함

## 마을 확장 (v0.21.0)
- 마을을 44×30으로 확장함(`VillageScene.COLS, ROWS`)
  - 기존 32×21 마을은 좌표를 그대로 두었으므로 세이브 보정이 필요 없음
  - 동쪽·남쪽 출입구만 새 가장자리로 옮김((43,10), (15,29)). 필드에서 돌아오는 위치(`return_village`)도 함께 옮김
  - 새 건물은 `DISTRICT`에, 주민은 `RESIDENTS`에 정의함. 기존 `BUILDINGS`(원래 세 건물, 골목 테스트용)와는 따로 관리함 (v0.23.0부터 주인은 실내에 있고, v0.24.0부터 크기·위치는 `PLACES`/`house_plot`에서 나옴)
  - 새 NPC 그림: innkeeper, blacksmith, librarian, apothecary, child
- 여관(로사): `inn_offer` → `ConfirmScene` → `rest_at_inn`. 숙박비는 10 + 2×레벨. 소문은 `RUMOURS` 목록에서 플레이 시간 1분마다 바뀜
- 물약 상점(미라): `ShopScene(game, "mira")`
  - `SHOP_ITEMS`의 `shop` 키로 상점을 구분함(기본값 logan)
  - 새 소모품은 `CONSUMABLES`에 있음: 마나 물약, 해독제, 엘릭서(3개까지). 세이브에는 `items` 가방으로 저장하고, 회복약 두 종류는 기존 필드를 그대로 씀
  - 전투의 "아이템" 버튼이 `item_list`를 열고, `act("item", id)`를 호출함. id 없이 `act("item")`을 부르면 예전처럼 자동으로 포션을 씀(시뮬레이터가 이 방식을 씀)
- 대장간(브론): `SmithyScene`
  - 장착 장비를 +3까지 강화함(무기 +3 공격, 방어구 +2 방어). 비용은 `upgrade_cost`. 세이브의 `upgrades`({장비 id: 단계})에 저장함
- 도서관(에델): `LibraryScene`. 책 데이터는 `gameplay/library.py`의 `BOOKS`(6권). 읽은 책은 세이브의 `books_read`에 저장하고, 모두 읽으면 "도서관의 학자" 업적을 얻음(업적 15개)
- 새 부탁 4개(전체 11개)
  - sq_inn_stew: 북쪽 길이 열린 뒤에 부탁함
  - sq_smith_ore
  - sq_library: `count: "bestiary"`. `sync_quest_progress`가 도감 수로 진행도를 맞춤
  - sq_tomi
  - 의뢰인은 `quest_due`일 때 부탁을 먼저 꺼내고, 그 밖에는 원래 기능(상점·대장간·도서관)을 엶
- 시뮬레이터는 대장간 강화와 새 소모품을 쓰지 않음. 실제 플레이는 시뮬레이션 결과보다 조금 쉬워질 수 있음

## 가방 (v0.22.0)
- 상태 화면의 다섯 번째 페이지 `bag`. 필드와 실내에서는 B 키로 바로 열림(`Game.open_status("bag")`)
- `StatusScene.bag_rows()`가 소모품·무기·방어구·장신구·중요 물품을 섹션 머리말과 함께 나열함. 빈 섹션에는 "(없음)" 줄이 들어감
  - 커서는 머리말과 빈 줄을 건너뜀. 한 화면에 `BAG_ROWS_VISIBLE`(16)줄씩 스크롤함
- Enter 동작
  - 소모품: `FieldScene.use_item_outside`. HP·MP가 가득 차 있거나 해독제처럼 회복 효과가 없으면 쓰지 않음
  - 무기·방어구: `equip`
  - 장신구: 장착 중이면 `unequip_accessory`, 아니면 장착함

## 건물 실내와 회차 재조정 (v0.23.0)
- 여관, 대장간, 도서관, 물약 상점에 실내(`village_inn`, `village_smithy`, `village_library`, `village_apothecary`)를 만듦
  - `HouseInteriorScene`의 `LAYOUTS`, `HOUSES`, `KEEPERS`, `FLAVOUR`에 등록함
  - 마을의 `DISTRICT` 항목은 `npc`·`sprite` 대신 `door`·`world`를 가짐. 문(지도 마커 `door`)에서 SPACE를 누르면 들어감. `HOUSE_EXITS`로 같은 문 앞에 나옴
  - 주인 대화는 `FieldScene.visit_keeper(name)`으로 옮김(`RUMOURS`, `inn_price`, `inn_rumour`, `rest_at_inn` 포함). 마을과 실내가 함께 씀
  - 여관 실내의 침대는 장식임. 휴식은 로사에게 돈을 내고 함
  - 지도 그래프(`world_data`)와 마을 음악(`village_` 접두어)에도 반영함
- 밸런스 시뮬레이터 `tools/balance_sim.py`
  - 기본으로 대장간 강화와 마나 물약까지 사용함. `--basic`은 이전 방식, `--plus`는 2회차까지 측정함
  - 1회차 결과는 변하지 않음(남는 골드가 거의 없어 강화를 못 함)
  - 2회차는 너무 쉬웠음. 그래서 `CYCLE_STEP`을 적 HP +160%, 받는 피해 +60%로 올림. 이제 2회차 최종 보스 승률은 약 75%

## 릴리즈 기록
- **v0.24.0:** 주인공 새 디자인(갑옷마다 옷 색 변화), 집마다 다른 모습(부품 조합), 비대칭 마을 배치, 새 게임 시작 연출(토미의 길 안내), 타이틀에서 세이브 삭제
- **v0.23.0:** 여관·대장간·도서관·물약 상점 실내 추가(주인이 안에서 기다림), 밸런스 시뮬레이터에 강화·마나 물약·2회차 반영, 회차 난이도 상향
- **v0.22.0:** 가방 페이지(B 키). 필드에서 물약 사용, 어디서든 장비 교체, 장신구 해제, 아이템 상세 정보
- **v0.21.0:** 마을 확장(44×30), 여관·대장간 강화·도서관·물약 상점, 전투 아이템 메뉴와 새 소모품, 새 주민 5명과 부탁 4개
- **v0.20.0:** 업적 14개(달성 알림과 상태 화면 업적 페이지), 엔딩 후 회차 플레이(새 여정), 대화 글자 속도 설정과 Enter·Z 행동 키
- **v0.19.0:** 난이도 선택(쉬움·보통·어려움, 모험 중 변경 가능), 상태 화면의 몬스터·장비 도감, 1분마다 자동 저장과 창을 닫을 때 저장
- **v0.18.0:** 플레이 시간과 전투 기록(세이브 슬롯과 엔딩 화면에 표시), 마을 부탁 데이터를 한 곳으로 정리
- **v0.17.0:** 서리 고원 사냥꾼 하른과 부탁(얼음 심장), 빙결 대비 장비와 제단 3·4곳 정화 단계의 상품, Lv.10 별빛 폭풍·Lv.12 성스러운 기도, 별빛 심연 난이도 재조정
- **v0.16.0:** 새 지역 「서리 고원」과 네 번째 제단 「얼음 제단」(제단 두 곳을 정화하면 열림), 새 적 4종과 빙결 상태이상, 인장 4개 기준으로 이야기 확장, 불꽃·최종 보스 밸런스 조정
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
   - 지붕 색 통일(`ROOFS`): 오두막 청록, 상점 테라코타, 촌장 집 벽돌색 (v0.24.0부터 `ROOFS`는 촌장 집만 쓰고, 나머지 집은 `utils/house_art.py`)
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
  - 집 6채의 위치는 `PLACES`(그림 기준 타일) 한 곳에서만 정함. `house_plot(key)`이 벽 영역 `(x, y, w, h)`와 문 타일을 계산하고, `BUILDINGS`·`DISTRICT`·`HOUSE_EXITS`·`QUEST_HOUSE_DOOR`·`KNIGHT_HOUSE_DOOR`가 모두 여기서 나옴
  - 집을 옮기면 `road_tiles()`(절대 좌표)의 길도 함께 고치고, 문 좌표가 바뀌면 `save_migration`에 맵 구조 단계를 추가할 것
  - 좌표는 숫자로 직접 쓰지 말고 상수를 씀: `START`, `HOUSE_EXITS`, `SHRINE_RETURN`, `SHRINE_SPAWN`, `FIELD_GATES`
  - 건물 사이에는 걸어갈 수 있는 통로를 2칸 이상 둠. 현재 오두막↔촌장 집 x 7~10, 촌장 집↔가렌 거처 x 20~22이고, `test_map_size`가 검사함
  - `CORE_OFFSET=(3,2)`는 이제 촌장 집, 로건 노점, 분수, 광장 나무(`core_trees`)를 그릴 때만 씀
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
- **릴리즈**: CLAUDE.md 절차를 따름. `gh`는 `C:\Program Files\GitHub CLI\gh.exe`에 설치됨. 릴리즈 확인은 `gh`로 할 것

## 남은 작업 및 아이디어
- 필수로 남은 작업은 없음
- 사용자 결정 대기
  - `csw94/RPG` 비공개 전환은 보류 중. 사용자가 정확히 지시하기 전에는 공개 범위를 바꾸지 말 것(한 번 미리 바꿨다가 되돌린 적 있음)
  - 비공개로 바꾸면 RPG 릴리즈도 함께 숨겨짐. 그때는 CLAUDE.md 5번(두 곳 업로드)을 Star만 올리도록 고칠지 함께 확인할 것
- 선택 과제
  - 이번 그래픽 개편을 직접 플레이로 확인: 주인공 색감, 집 크기와 위치, 토미 연출 속도(`gameplay/intro.py`의 `RUN_SPEED`, `LEAD_SPEED`)
  - 다른 NPC나 필드에도 `PLACES`/`house_art` 방식이나 `input_locked` 연출 연결점을 재사용할 수 있음
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
| `tools/release_notes.py` / `.github/workflows/ci.yml` | 릴리즈 노트 추출 / 푸시할 때 도는 테스트 CI(릴리즈 빌드 워크플로는 없음) |
| `utils/house_art.py` | 마을 집 부품 조합 `HOUSE_STYLES`, `paint_house()` |
| `gameplay/intro.py` | 새 게임 시작 연출 `ChiefCallIntro`(토미의 안내) |
| `db/save_manager.py` | 세이브 슬롯 저장·불러오기·삭제(`delete`) |
| `gameplay/objectives.py` | 다음 목표 안내 |
| `gameplay/quests.py` / `gameplay/records.py` | 마을 부탁 데이터 / 플레이 시간 표시와 세이브 슬롯 요약 |
| `gameplay/difficulty.py` | 난이도 배율 |
| `scenes/smithy_scene.py` / `scenes/library_scene.py` / `scenes/confirm_scene.py` | 대장간 / 도서관 / 예·아니오 확인 창 |
| `gameplay/library.py` / `gameplay/new_game_plus.py` / `gameplay/achievements.py` | 도서관 책 / 회차 플레이 / 업적 |
| `utils/interior_art.py` | 실내 스프라이트. `interior_sprite(name, scale=2)`, 러그는 `rug_<색>_<w>x<h>` 형식 |
| `utils/ui.py` | 공용 UI: 프레임, 막대, 버튼, 판자 띠 |
| `utils/battle_art.py` | 전투 배경 `backdrop(kind)`, 발판 위치 상수 |
| `utils/title_art.py` | 타이틀 배경 `backdrop()`과 애니메이션 `draw_overlay(surface, clock)` |
| `scenes/field_scene.py` | 필드 공통 로직: 테마, 장식, `_blob`, HUD, 대화창 |
| `scenes/village_scene.py` | 마을 레이아웃(`PLACES`, `house_plot`, `road_tiles`), 정적 레이어 캐시, 시작 연출 그리기 |
| `scenes/house_scene.py` | `LAYOUTS`, `ROOM`, `solid_tiles()` |
| `scenes/dungeon_scene.py` | 던전 레이아웃과 타일 그리기 |
| `scenes/battle_scene.py` | `backdrop_kind()`, 전투 그리기 |
| `gameplay/world_data.py` / `gameplay/enemies.py` | 필드 데이터 / 적 데이터(스프라이트 이름, 표시 크기) |
| `tests/` | `test_pixel_art`, `test_interiors`, `test_field_art`, `test_ui`, `test_map_size`, `test_dungeon_battle_art`, `test_title_art`, `test_house_art`, `test_village_layout`, `test_intro`, `test_save_delete` 및 기존 테스트 |

## 주의사항
- 화면 확인은 `main.Game()._create_world(state)`로 장면을 만들어 렌더링한다. `new_game()`은 세이브를 덮어쓰니 쓰지 않는다.
  - 대화를 끝까지 넘기는 스크립트에서는 `game.save_game = lambda *a, **k: None`으로 저장을 막는다. 시작 연출처럼 대화가 끝날 때 저장하는 경우가 있다.
  - 세이브 관련 테스트와 스크립트는 임시 DB(`SaveManager(임시경로)`)를 쓴다. 윈도우에서는 SQLite 파일이 열려 있어 `TemporaryDirectory(ignore_cleanup_errors=True)`가 필요하다.
- GitHub CLI는 `C:\Program Files\GitHub CLI\gh.exe`(`csw94`로 로그인됨). 사용자에게 `!` 명령을 안내할 때는 bash 문법(`"/c/Program Files/GitHub CLI/gh.exe" ...`)으로 적는다.
- 푸시가 `Internal Server Error`로 거부되면 잠시 뒤 다시 시도한다(일시적인 GitHub 오류).
- 풀(`grass_*`)과 나무 그림은 마을·필드·제단 공터가 같이 쓴다. 바꾸면 세 화면을 모두 확인해야 한다.
- 실행 확인용으로 EXE를 띄운 뒤에는 `Get-Process ChroniclesOfPixel`로 남은 프로세스까지 모두 종료한다. 단일 파일 빌드라 자식 프로세스가 따로 남는다.
- git 명령에는 `-c safe.directory=C:/Users/dongb/IdeaProjects/RPG`를 붙이고, 작성자는 `Codex <codex@openai.com>`로 한다.
