"""Write professional Japanese editions of the three plan HTML exports.

English files stay in place. Japanese files are the same name with .ja.html.
Re-run after regenerating the English exports. Untranslated sentences are printed.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPORTS = HERE / "exports"

# Exact visible strings, whitespace-collapsed, HTML entities decoded.
JA = {
    # titles
    "Red5-DHCP — continuous project delivery, by phase":
        "Red5-DHCP — フェーズで進める継続実施",
    "Red5-DHCP — workflow plan, one project":
        "Red5-DHCP — 実施計画（単一プロジェクト）",
    "Red5-DHCP — system architecture SLD: existing vs proposed":
        "Red5-DHCP — システム架構単線図（既設と更新案）",
    "Red5-DHCP — system architecture single-line diagrams":
        "Red5-DHCP — システム架構単線図",

    # phase plan lead
    "One contract for the 67-panel / 4,467-point savic-netFX2 → Delta retrofit. Five phases overlap across nine months. The completion date is the contract date plus nine months. DEJ holds the contract. TYBMS is subcontracted to DEJ.":
        "盤67面、4,467点のsavic-netFX2からDeltaへの更新を、一つの契約で実施する。五つのフェーズは9か月の中で重なる。完了日は契約日の9か月後である。元請はDEJ、TYBMSはその下請である。",
    "5, overlapping": "5（重なる）",
    "n/a": "該当なし",
    "Phases": "フェーズ",
    "9 months from the contract date": "契約日から9か月",
    "Duration": "工期",
    "Panels (Phase 1 build → Phase 3 install)": "盤（フェーズ1製作 → フェーズ3据付）",
    "Controllers + modules (Phase 1)": "コントローラ＋モジュール（フェーズ1）",
    "Field terminations (Phase 3)": "現場端末（フェーズ3）",
    "Analog devices (Phase 4)": "アナログ機器（フェーズ4）",
    "DDC programs (Phase 5)": "DDCプログラム（フェーズ5）",
    "One continuous delivery": "一つの継続実施",
    "This is one continuous delivery. Fabrication, the new device network, installation, instruments and programming overlap inside the same nine months, under the one contract. The phases name the kind of work.":
        "本工事は一つの継続実施である。盤製作、新設デバイスネットワーク、据付、計装、プログラミングは、同一契約の9か月の中で重なる。フェーズは作業の種類を示す。",
    "The phases overlap": "フェーズは重なる",
    "Phase 5 authoring starts in month C+1 so the factory can bench-load. Phase 2 proves each new network run before that wave's first panel. On site, installation, instruments and programming happen inside the same area wave, the same night. An area returns to automatic control only when its program is proved. The playbook covers one panel at a time.":
        "工場でプログラムを載せられるよう、フェーズ5の作成はC+1月から始める。フェーズ2は、そのウェーブの最初の盤の前に新しいネットワーク区間を証明する。現場では据付、計装、プログラミングを同じ工区の同じ夜に行う。区域を自動に戻すのは、プログラムの証明が終わってからである。手元運転の手順は、一度に1面だけを対象とする。",
    "Stage gates, not separate contracts": "段階確認であり、別契約ではない",
    "The commissioning checklist still records progress: factory acceptance, Wired and Terminated, P2P verified, and Func. test. Those columns are stage gates of the one delivery. They are not separate completion contracts.":
        "試運転チェックリストは進捗を残す。工場受入、配線・端末、P2P確認、機能試験である。これらの欄は一つの実施の段階確認であり、別々の完了契約ではない。",
    "The five phases": "五つのフェーズ",
    "Phase": "フェーズ",
    "Name": "名称",
    "Nature of work": "作業の性質",
    "Licence question": "許可の確認事項",
    "Window": "期間",
    "Objective": "目的",
    "Objective.": "目的。",
    "Continues from": "前段",
    "How the delivery continues": "次へのつながり",
    "Phase 1": "フェーズ1",
    "Phase 2": "フェーズ2",
    "Phase 3": "フェーズ3",
    "Phase 4": "フェーズ4",
    "Phase 5": "フェーズ5",
    "Panel fabrication, supply & factory acceptance": "盤製作・供給・工場受入",
    "Off-site manufacture / supply": "工場製作・供給",
    "Likely NOT 建設業 (goods manufacture + supply) — confirm": "建設業に該当しない可能性が高い（物品の製造・供給）。要確認",
    "C+0 to C+6 mo": "C+0〜C+6か月",
    "Deliver every DDC panel to site already built, loaded and factory-tested, so that on-site time is reduced to swapping an enclosure and landing wires.":
        "DDC盤を、製作・プログラム投入・工場試験を終えた状態で現場へ納入する。現場作業は筐体の入替えと配線の端末処理に限る。",
    "—": "—",
    "Hands panels to Phase 3 in wave order. Bench-load needs the programs from Phase 5, which starts in month C+1.":
        "盤はウェーブ順にフェーズ3へ渡す。工場でのプログラム投入には、C+1月から始まるフェーズ5のプログラムが要る。",
    "Device-network cabling": "デバイスネットワーク配線",
    "New field network, inside the same contract": "同一契約の中の新設フィールドネットワーク",
    "Same licence question as the site electrical work — confirm": "現場電気工事と同じ許可区分。要確認",
    "C+0 survey · C+2 to C+6 install · proved before each wave": "C+0調査 · C+2〜C+6布設 · 各ウェーブ前に証明",
    "Identify the installed Azbil cable and, where it is IEIEJ p-A or otherwise unsuitable, install a new device network before cutover. This phase does not add a month.":
        "既設アズビルのケーブルを確認する。IEIEJ p-Aである場合、または新設ネットワークの仕様を満たさない場合は、切替前に新しいデバイスネットワークを布設する。このフェーズは工期を1か月延ばさない。",
    "Starts with Phase 1, in the contract month": "フェーズ1と同時、契約月に開始",
    "Each cutover wave lands on a run this phase has already proved.":
        "各切替ウェーブは、このフェーズが証明済みの区間に接続する。",
    "Panel replacement & field termination": "盤更新と現場端末処理",
    "Electrical installation (on-site construction)": "電気工事（現場施工）",
    "電気工事業 — almost certainly required": "電気工事業 — ほぼ確実に必要",
    "C+5 mo mobilise · C+6 to C+8 mo by wave": "C+5か月に着工準備 · C+6〜C+8か月はウェーブ順",
    "Physically replace the Azbil RS/RCP/CP panels with the new DDC panels and transfer every field termination, without the hotel losing conditioning.":
        "アズビルのRS／RCP／CP盤を新しいDDC盤に取り替え、現場端末をすべて移設する。ホテルの空調は止めない。",
    "Phase 1 panels for that wave, and the Phase 2 run for that wave":
        "そのウェーブのフェーズ1の盤と、フェーズ2の区間",
    "The same night continues into instruments and programming.":
        "同じ夜の中で計装とプログラミングへ続く。",
    "Field instrumentation replacement & calibration": "現場計装の更新と校正",
    "Instrumentation installation (on-site construction)": "計装工事（現場施工）",
    "管工事 / 電気 / 計装 — category to be confirmed": "管工事／電気／計装 — 区分は要確認",
    "C+6 to C+8 mo, inside each wave after the panel is energised":
        "C+6〜C+8か月。各ウェーブで盤の受電後",
    "Replace and calibrate the analog field devices so the new controllers read true values, which is what the optimisation sequences depend on.":
        "アナログ現場機器を更新し校正する。新しいコントローラが真値を読むためであり、最適化シーケンスはこれに依存する。",
    "Phase 3 (panel live for that area)": "フェーズ3（その区域の盤が活線）",
    "The same night continues into the functional test.": "同じ夜の中で機能試験へ続く。",
    "Programming, integration, tuning & handover": "プログラミング・統合・調整・引渡し",
    "Engineering / software services": "エンジニアリング／ソフトウェア役務",
    "情報通信工事 — or arguably not 建設業 at all; confirm": "情報通信工事 — 建設業に該当しない可能性もある。要確認",
    "C+1 mo authoring · C+5 mo head-end · C+6 mo through completion":
        "C+1か月に作成 · C+5か月に中央装置 · C+6か月から完了まで",
    "Make the installed hardware behave: load the control logic, prove every point, tune the sequences and hand a working system to the hotel.":
        "据え付けた機器を動かす。制御ロジックを投入し、全点を証明し、シーケンスを調整して、動く系統をホテルに引き渡す。",
    "Phase 3 and Phase 4 for that area wave. Authoring itself starts in month C+1.":
        "その工区ウェーブのフェーズ3とフェーズ4。プログラム作成自体はC+1月から開始する。",
    "Closes the project at the contract date plus nine months.":
        "プロジェクトの完了は、契約日の9か月後である。",
    "The phases overlap. The right-hand column says how each one hands into the next. Completion is the contract date plus nine months.":
        "フェーズは重なる。右端の列は、次のフェーズへの渡し方を示す。完了は契約日の9か月後である。",
    "Scope, deliverables and completion criteria": "範囲、成果物、完了条件",
    "Phase 1 — Panel fabrication, supply & factory acceptance": "フェーズ1 — 盤製作・供給・工場受入",
    "Off-site manufacture / supply · C+0 to C+6 mo · depends on —":
        "工場製作・供給 · C+0〜C+6か月 · 前提なし",
    "Scope": "範囲",
    "Procure 904 Delta controllers and I/O modules against the panel schedule":
        "盤スケジュールに対し、DeltaコントローラとI/Oモジュール904台を調達する",
    "Build and wire 67 enclosures to 5,240-point capacity (4,467 used, 773 spare)":
        "盤67面を製作・内部配線する。容量5,240点（使用4,467、予備773）",
    "Head-end hardware: replacement of the BMS / SMS / DSS server role and the two operator consoles":
        "中央装置：BMS／SMS／DSSのサーバ機能と操作卓2台の更新",
    "Bench-load the GCL+ programs and simulate I/O at the factory":
        "工場でGCL+プログラムを投入し、I/Oを模擬する",
    "Panel general-arrangement and termination drawings, spares schedule":
        "盤姿図、端末図、予備品表",
    "Deliverables": "成果物",
    "67 panels delivered to site, labelled per the panel schedule":
        "盤スケジュールどおりに表示した盤67面を現場へ納入",
    "FAT certificate per panel (module count, addressing, power-up, simulated I/O)":
        "盤ごとのFAT証明書（モジュール数、アドレス、電源投入、模擬I/O）",
    "As-built panel drawings + terminal schedules": "竣工盤図と端子表",
    "Head-end hardware delivered and staged": "中央装置ハードウェアの納入と仮置き",
    "Spare-parts list and recommended holding": "予備品リストと推奨保有数",
    "Acceptance / completion": "受入／完了",
    "Module count reconciles to 904 against panels_schedule.json":
        "モジュール数がpanels_schedule.jsonの904と一致する",
    "FAT witnessed and signed per panel; no panel ships on a failed FAT":
        "盤ごとにFATを立会のうえ署名する。不合格の盤は出荷しない",
    "Delivery note signed at site — this is the transfer of title, no site work involved":
        "現場で納品書に署名する。これは引渡しであり、現場工事は含まない",
    "Phase 2 — Device-network cabling": "フェーズ2 — デバイスネットワーク配線",
    "New field network, inside the same contract · C+0 survey · C+2 to C+6 install · proved before each wave · depends on Starts with Phase 1, in the contract month":
        "同一契約の新設フィールドネットワーク · C+0調査 · C+2〜C+6布設 · 各ウェーブ前に証明 · 前提：フェーズ1と同時に契約月から開始",
    "Survey panels and risers. The 2002 drawing names IPEV-S 0.9 mm². The installed cable may be IEIEJ p-A.":
        "盤と竪穴を調査する。2002年の図面はIPEV-S 0.9 mm²である。既設ケーブルはIEIEJ p-Aの可能性がある。",
    "Reuse a run only when a test shows it meets the new network specification. IEIEJ p-A is not assumed reusable.":
        "区間を再利用するのは、試験が新設ネットワーク仕様を満たした場合だけである。IEIEJ p-Aは再利用できるとは扱わない。",
    "Design and pull the new risers and floor cabling while the old network is still in service":
        "既設ネットワークを運用したまま、新しい竪穴とフロア配線を設計し布設する",
    "Prove continuity, insulation and communications on each run before that wave starts":
        "ウェーブ開始前に、各区間の導通、絶縁、通信を証明する",
    "Record abandoned cable so a later crew does not land a new panel on it":
        "廃棄ケーブルを記録し、後の作業員が新しい盤をそこに接続しないようにする",
    "Cable identification record": "ケーブル識別記録",
    "Reuse or replace decision per riser": "竪穴ごとの再利用／新設の判定",
    "Network drawings and cable schedule": "ネットワーク図とケーブル表",
    "Segment test certificate before each wave": "各ウェーブ前の区間試験証明書",
    "As-built network drawings": "ネットワーク竣工図",
    "Cable type recorded before the network design is approved":
        "ネットワーク設計の承認前にケーブル種別を記録する",
    "Each wave's new run tested before that wave's first panel is cut over":
        "各ウェーブの新しい区間を、その最初の盤の切替前に試験する",
    "IEIEJ p-A not landed on the new panels unless a test says the run meets the specification":
        "試験がその区間の仕様適合を示すまで、IEIEJ p-Aを新盤に接続しない",
    "Phase 3 — Panel replacement & field termination": "フェーズ3 — 盤更新と現場端末処理",
    "Electrical installation (on-site construction) · C+5 mo mobilise · C+6 to C+8 mo by wave · depends on Phase 1 panels for that wave, and the Phase 2 run for that wave":
        "電気工事（現場施工） · C+5か月に着工準備 · C+6〜C+8か月はウェーブ順 · 前提：そのウェーブのフェーズ1の盤とフェーズ2の区間",
    "Remove 67 existing Azbil RS/RCP/CP panels, install their replacements":
        "既設アズビルRS／RCP／CP盤67面を撤去し、更新盤を据え付ける",
    "Transfer and land 4,467 field terminations (3,342 binary, 534 pulse, 591 analog)":
        "現場端末4,467点を移設する（バイナリ3,342、パルス534、アナログ591）",
    "Land each panel on the device-network run proved in Phase 2. Do not reuse IEIEJ p-A unless that test passed":
        "各盤を、フェーズ2で証明したデバイスネットワーク区間に接続する。試験に合格しない限りIEIEJ p-Aは再利用しない",
    "Panel power, earthing, containment and making good": "盤電源、接地、配線路、復旧",
    "Old controller left landed on a marshalling strip for rollback":
        "切戻しのため、旧コントローラは中継端子に接続したまま残す",
    "67 panels installed and energised": "盤67面を据付・受電",
    "Per-panel wiring completion certificate": "盤ごとの配線完了証明書",
    "Continuity / insulation test records": "導通・絶縁試験記録",
    "Marked-up termination drawings (as-installed)": "端末図の施工記入（竣工）",
    "Rollback arrangement demonstrated per area wave": "工区ウェーブごとに切戻し手順を実証",
    '"Wired" and "Terminated" signed for all 4,467 points on the commissioning checklist':
        "試運転チェックリストの全4,467点について「配線」「端末」に署名",
    "Insulation and continuity results within limits, per panel": "盤ごとに絶縁と導通が規格内",
    "The panel is on the proved new run before the wave is closed":
        "ウェーブを閉じる前に、盤が証明済みの新しい区間に載っている",
    "Phase 4 — Field instrumentation replacement & calibration": "フェーズ4 — 現場計装の更新と校正",
    "Instrumentation installation (on-site construction) · C+6 to C+8 mo, inside each wave after the panel is energised · depends on Phase 3 (panel live for that area)":
        "計装工事（現場施工） · C+6〜C+8か月、各ウェーブで盤受電後 · 前提：フェーズ3（その区域の盤が活線）",
    "Replace 505 analog input devices — temperature, humidity, pressure, flow, energy":
        "アナログ入力機器505台を更新する — 温度、湿度、圧力、流量、熱量",
    "Replace 86 analog output devices — modulating valves and damper actuators":
        "アナログ出力機器86台を更新する — 比例弁とダンパアクチュエータ",
    "Verify (not replace) 534 pulse / totalizer interfaces from existing meters":
        "既設計量器のパルス／積算インタフェース534点は更新せず、確認する",
    "Re-range and calibrate each loop against the I/O list engineering units":
        "各ループをI/Oリストの工業単位に合わせてレンジ変更し、校正する",
    "Immersion wells, averaging elements and impulse lines made good":
        "保護管、平均化エレメント、導圧管を整備する",
    "591 analog devices installed": "アナログ機器591台を設置",
    "Calibration certificate per loop, traceable": "ループごとのトレーサブルな校正証明書",
    "Loop schedules marked with as-installed range and units": "竣工のレンジと単位を記入したループ表",
    "534 pulse interfaces proven for count and scaling": "パルスインタフェース534点の計数とスケールを証明",
    '"P2P verified" signed for all 591 analog points': "アナログ591点の「P2P確認」に署名",
    "Two-point calibration recorded for every AI; stroke test for every AO":
        "全AIは2点校正、全AOはストローク試験を記録する",
    "Reading agreement against a reference instrument within tolerance":
        "基準器との指示差が許容内である",
    "Phase 5 — Programming, integration, tuning & handover": "フェーズ5 — プログラミング・統合・調整・引渡し",
    "Engineering / software services · C+1 mo authoring · C+5 mo head-end · C+6 mo through completion · depends on Phase 3 and Phase 4 for that area wave. Authoring itself starts in month C+1.":
        "エンジニアリング／ソフトウェア役務 · C+1か月に作成 · C+5か月に中央装置 · C+6か月から完了まで · 前提：その工区のフェーズ3とフェーズ4。作成自体はC+1月から開始",
    "Load and commission 109 DDC control programs (GCL+, one PG object per controller)":
        "DDC制御プログラム109本を投入し試運転する（GCL+、コントローラごとにPGオブジェクト1つ）",
    "Build the head-end point database and graphics for 1,383 characterised points across 259 devices":
        "機器259台、特性化ポイント1,383点の中央ポイントデータベースとグラフィックを作る",
    "R-1 chiller optimiser: economic dispatch, CW/CHW reset, staging, FDD":
        "R-1冷凍機最適化：地域冷暖房に対する経済運転、冷却水・冷水リセット、台数制御、故障検出",
    "Trend, alarm, time-program, calendar and reporting configuration":
        "トレンド、アラーム、スケジュール、カレンダ、帳票の設定",
    "Functional test of all 4,467 points; 24–48 h trend per panel before auto":
        "全4,467点の機能試験。自動復帰の前に盤ごとに24〜48時間のトレンド",
    "Seasonal tuning through first cooling season; operator training; O&M documentation":
        "最初の冷房期を通じた季節調整、運転員教育、保全文書",
    "109 programs loaded and version-controlled": "プログラム109本を投入し版管理する",
    "Head-end graphics and database live on the new servers": "新しいサーバで中央グラフィックとデータベースが稼働",
    "Functional test sheets, complete": "機能試験表一式",
    "Trend evidence per panel": "盤ごとのトレンド記録",
    "Sequence-of-Operations compliance record against docs/control_logic.md":
        "docs/control_logic.mdに対する動作説明の適合記録",
    "Training delivered; as-built documentation issued": "教育の実施と竣工図書の提出",
    '"Func. test" signed for all 4,467 points': "全4,467点の「機能試験」に署名",
    "Each controller demonstrated against its SOO": "各コントローラを動作説明に対して実証",
    "24–48 h stable trend per panel before hand-back to auto":
        "自動へ戻す前に、盤ごとに24〜48時間の安定トレンド",
    "Operator sign-off after training": "教育後の運転員署名",
    "Execution — the phases overlap by cutover area wave": "実施 — フェーズは切替工区のウェーブで重なる",
    "Windows are months after the contract date. An area returns to automatic control only when its Phase 5 programming is proved.":
        "期間は契約日からの月数である。区域を自動に戻すのは、そのフェーズ5のプログラムが証明されてからである。",
    "Wave": "ウェーブ",
    "Area": "区域",
    "Panels": "盤",
    "Points": "点",
    "Phase 1 fabricate": "フェーズ1 製作",
    "Phase 2 network": "フェーズ2 ネットワーク",
    "Phase 3 install": "フェーズ3 据付",
    "Phase 4 instruments": "フェーズ4 計装",
    "Phase 5 program": "フェーズ5 プログラム",
    "Central head-end (B2F 시스템 제어반)": "中央装置（B2F システム制御盤）",
    "proved before C+5": "C+5の前に証明",
    "C+5 — alongside FX2": "C+5 — FX2と並行",
    "Penthouse PH1/PH2 — rooftop plant, R-1, OAUs": "ペントハウス PH1／PH2 — 屋上機器、R-1、外調機",
    "proved before C+6": "C+6の前に証明",
    "Guest & public floors — 31F, 21F, 10F, 4F–1F": "客室階・パブリック階 — 31F、21F、10F、4F〜1F",
    "Basements B1–B3 — plant, hydronics, DHC intake": "地下 B1〜B3 — 機械室、水配管、地域冷暖房受入",
    "C+6–C+7, last": "C+6〜C+7、最後",
    "TOTAL": "合計",
    "Quantity reconciliation — the phases cover the whole project": "数量照合 — フェーズで工事全体を覆う",
    "Quantity": "数量",
    "Basis": "根拠",
    "67 built": "67面を製作",
    "67 installed": "67面を据付",
    "panels_schedule.json": "panels_schedule.json",
    "Controllers + modules": "コントローラ＋モジュール",
    "109 programs": "プログラム109本",
    "modTotals / functional model": "modTotals／機能モデル",
    "Field points": "現場点",
    "5,240 capacity": "容量5,240",
    "4,467 terminated": "端末4,467",
    "591 calibrated": "校正591",
    "4,467 function-tested": "機能試験4,467",
    "usedTotal / typeTotals": "usedTotal／typeTotals",
    "Device network": "デバイスネットワーク",
    "survey, new cable, proved per wave": "調査、新設ケーブル、ウェーブごとに証明",
    "landed at cutover": "切替時に接続",
    "comms proved": "通信を証明",
    "installed cable may be IEIEJ p-A": "既設ケーブルはIEIEJ p-Aの可能性",
    "Analog devices": "アナログ機器",
    "typeTotals": "typeTotals",
    "Pulse / totalizer": "パルス／積算",
    "534 landed": "534を端末",
    "534 verified": "534を確認",
    "Checklist column": "チェックリスト欄",
    "FAT record": "FAT記録",
    "run proved": "区間を証明",
    "Wired + Terminated": "配線＋端末",
    "P2P verified": "P2P確認",
    "Func. test": "機能試験",
    "build_commissioning.py": "build_commissioning.py",
    "Open items": "未確定事項",
    "Threshold basis": "許可の金額基準",
    "特定建設業許可 is triggered by the value a prime contractor SUBCONTRACTS OUT (4,500万円, or 7,000万円 for 建築一式工事) — not by the headline contract value. If that is the operative test, then how much the prime subcontracts matters more than how the contract is divided. DEJ is the prime. TYBMS is subcontracted to DEJ, so the test is the value DEJ places with TYBMS and any other subcontractor. Confirm with counsel against that subcontract, not against a four-way split.":
        "特定建設業許可は、元請が下請けに出す金額（4,500万円、建築一式工事は7,000万円）で判定され、契約の総額では判定されない。この基準が適用される場合、契約の分け方より、元請がいくら下請けに出すかが問題になる。元請はDEJであり、TYBMSはその下請である。確認は、この下請金額について顧問に求める。",
    "Licence category for BMS": "BMS工事の許可区分",
    "Whether BMS work is 電気工事, 管工事, 情報通信工事 or a combination is still unresolved. It decides which phases need a licence. Phase 1 is manufacture. Phase 5 is largely services. The site exposure sits in Phase 2, Phase 3 and Phase 4.":
        "BMS工事が電気工事、管工事、情報通信工事のいずれに該当するか、または複合かは未確定である。これにより、許可が必要なフェーズが決まる。フェーズ1は製造、フェーズ5は主として役務である。現場で許可が問題になるのはフェーズ2、3、4である。",
    "One delivery": "一つの実施",
    "The proposal is one continuous project under DEJ. It is not a four-segment split, and it is not four payment contracts. A split whose only purpose is a value cap is the arrangement this plan no longer presents.":
        "本提案は、DEJを元請とする一つの継続プロジェクトである。四つの分割でも、四本の支払い契約でもない。金額の上限だけを理由にした分割は、本計画では示さない。",
    "Prime contractor identity": "元請の特定",
    "Furukawa Denki has backed out. DEJ submits the proposal and holds the main contract. TYBMS is subcontracted to DEJ.":
        "古河電機は離脱した。提案と主契約はDEJが行い、TYBMSはDEJの下請である。",
    "Continuity of control": "制御の連続",
    "Phases 3, 4 and 5 run inside the same area wave. If installation finished building-wide before programming started, the hotel would sit on manual control for months. The playbook supports one panel at a time.":
        "フェーズ3、4、5は同じ工区ウェーブの中で行う。据付を館全体で終えてからプログラミングを始めると、ホテルは何か月も手元運転になる。手元運転の手順は、一度に1面だけである。",
    "Foreign personnel": "外国籍作業員",
    "Scope of work permitted for Korean crews, insurance liability and safety responsibility are unresolved in writing. They bear on the on-site phases, Phase 3 and Phase 4.":
        "韓国人作業員に許される作業範囲、保険上の責任、安全上の責任は、書面で未確定である。対象は現場フェーズ、すなわちフェーズ3とフェーズ4である。",
    "Generated 2026-11-26 · Red5-DHCP · basis: panels_schedule.json (판넬별 포인트 정리 26.07.30), docs/reconciliation_2026-08.md, build_cutover.py, build_commissioning.py · meeting of 2026-09-03. Print to PDF for distribution. Not legal advice — see open items.":
        "作成 2026-11-26 · Red5-DHCP · 根拠：panels_schedule.json（판넬별 포인트 정리 26.07.30）、docs/reconciliation_2026-08.md、build_cutover.py、build_commissioning.py · 2026-09-03打合せ。配布はPDF印刷。法的助言ではない。未確定事項を参照。",

}

from ja_rest import MORE  # noqa: E402

JA.update(MORE)

FONT = '"Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Noto Sans JP", Meiryo, sans-serif'
SRC = [
    "red5-dhcp_phase-plan.html",
    "red5-dhcp_sld.html",
    "red5-dhcp_workflow-plan.html",
]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def translate(raw: str) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(match: re.Match) -> str:
        inner = match.group(1)
        if "{" in inner:
            return match.group(0)
        key = norm(inner)
        if not key or not re.search(r"[A-Za-z]", key):
            return match.group(0)
        if key not in JA:
            if re.search(r"[A-Za-z]{4,}", key):
                missing.append(key)
            return match.group(0)
        return ">" + html.escape(JA[key], quote=False) + "<"

    # Keep <style> intact. The stylesheet contains no nested tags, so a naive
    # text-node scan would treat the whole sheet as one sentence.
    styles = []

    def hold(match: re.Match) -> str:
        styles.append(match.group(0))
        return f"@@STYLE{len(styles) - 1}@@"

    raw = re.sub(r"<style>.*?</style>", hold, raw, flags=re.S)
    raw = re.sub(r">([^<]*)<", repl, raw)
    for i, sheet in enumerate(styles):
        sheet = sheet.replace(
            "-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
            FONT,
        )
        sheet = sheet.replace("font:14px/1.5 ", "font:14px/1.75 ")
        raw = raw.replace(f"@@STYLE{i}@@", sheet)
    raw = raw.replace('lang="en"', 'lang="ja"')
    raw = raw.replace(
        'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif"',
        'font-family="Hiragino Sans, Hiragino Kaku Gothic ProN, Yu Gothic, Noto Sans JP, Meiryo, sans-serif"',
    )
    raw = raw.replace(
        'aria-label="Existing Azbil savic-netFX2 architecture"',
        'aria-label="既設アズビル savic-netFX2 の架構"',
    )
    raw = raw.replace(
        'aria-label="Proposed Delta / Red5 BACnet architecture"',
        'aria-label="更新案 Delta／Red5 BACnet の架構"',
    )
    raw = raw.replace(
        'aria-label="One-project nine-month programme Gantt"',
        'aria-label="単一プロジェクト、契約日から9か月の工程"',
    )
    return raw, missing


def main() -> None:
    leftover = []
    for name in SRC:
        src = EXPORTS / name
        out = src.with_name(src.stem + ".ja.html")
        text, missing = translate(src.read_text(encoding="utf-8"))
        out.write_text(text, encoding="utf-8")
        print(f"{out.name}: {len(missing)} English fragments left")
        leftover.extend(f"{name}\t{item}" for item in missing)
    report = HERE / "ja_untranslated.txt"
    report.write_text("\n".join(dict.fromkeys(leftover)), encoding="utf-8")
    print(f"report: {report.name} ({len(set(leftover))} unique)")


if __name__ == "__main__":
    main()
