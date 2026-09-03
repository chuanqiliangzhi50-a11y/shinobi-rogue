# iPhone Device Smoke Test Result — Ver.1.0.43

実施日: 2026-09-03
対象: Ver.1.0.43 FINAL DEVICE RC / Godot Web release / iPhone Safari
接続: Cloudflare Quick Tunnel経由、iPhone 4G

## 実機確認結果
- PASS: iPhone Safariで起動
- PASS: 「忍の里」表示
- PASS: 日本語表示
- PASS: 縦画面レイアウト
- PASS: 「出陣」タップ
- PASS: 1F生成
- PASS: 方向パッド「→」を2回タップ
- PASS: プレイヤー位置が2マス移動
- PASS: ターン表示 0 → 2
- PASS: 上記範囲でフリーズ/クラッシュなし

## 既確認のWindows側結果
- PASS: Godot 4.7.2 preflight
- PASS ALL: 保存契約 / 格子検証 / エンティティ復旧 / 階段保存 / 縛影1-8 / 満腹 / 帰還報酬 / 盗み / アイテム配置 / 階段到達 / 難易度曲線 / 遠距離射線 / アイテム一覧 / ボス門 / 配置安全 / ボス復旧 / 商店復旧 / 影分身30歩 / 広告OFF / 百階契約 / 忍気研究 / 日本語字形

## 判定
Windows/Web/iPhone Safariのリリース前スモーク範囲はPASS。Ver.1.0.44 RELEASE RCはゲームロジックを変更せず、この確認済み状態をリリース候補として固定する。

未実施: macOS/XcodeでのネイティブiOS署名、ネイティブiPhone実機、Archive/Validate/App Store Connect upload。
