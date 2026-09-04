# Ver.1.0.49 CODEMAGIC HEADLESS FIX RC

## Purpose
CodemagicのGodot regressionが終了自体は成功しても、headless描画で`Required object "p_texture" is null`を出していた問題を修正。

## Changes
- headless/self-testではUI glyph textureがnullでも描画APIを呼ばない安全ガードを追加。
- regression self-test中の不要な`queue_redraw()`を抑止。
- Codemagic CIで`SHINOBI_REGRESSION PASS ALL:`の出力を必須化。
- regressionログに`ERROR:`が残る場合はCIを失敗させ、見かけ上のfinishedを防止。
- versionを1.0.49 / iOS build 49へ同期。

## Unchanged
- ゲームルール
- save schema v4
- 初回版広告/トラッキングOFF
- 既存iPhone縦画面UI

# Ver.1.0.48 CODEMAGIC FIX RC

- Fixed Codemagic clean-checkout failure: `preload("res://ui_glyphs.png")` could be parsed before Godot generated the imported PNG cache.
- Glyph texture is now lazily loaded only in normal play; headless regression does not require presentation assets.
- Added `Import project resources` to both Codemagic workflows.
- Reduced preflight max duration to 15 minutes so future hangs fail faster.
- Gameplay logic and save schema v4 unchanged.

# Ver.1.0.46 VISUAL/CI RC

- Kept game logic and save schema v4 unchanged.
- Visual design remains replaceable; no final art lock.
- Added `codemagic.yaml` and `CODEMAGIC_SETUP.md` for cloud macOS Godot iOS export preparation.
- iOS version/build synced to 1.0.46 / 46.
- Ads/tracking remain disabled for initial release.

# Ver.1.0.45 APP STORE PREP

- App Store提出準備専用リリース。
- ゲームロジックはVer.1.0.44から変更なし。save schema v4維持。
- version 1.0.45 / build 45へ同期。
- 古いiOS設定資料のversion表記を修正。
- App Storeメタデータを提出用に整理。
- 公開可能なPrivacy Policy / Support Page HTMLを追加。
- App Store Connect入力チェックリストを現行Apple要件に合わせて整理。
- ネイティブiOSの署名・Archive・アップロードはmacOS/Xcodeが必要なため未実施。


## Ver.1.0.47 CODEMAGIC READY
- Codemagicを「認証不要のpreflight」と「Apple署名/App Store build」の2段階に分離。
- Apple認証前でもクラウドmacOS上でGodot 4.7.2回帰テストを実行可能にした。
- Apple認証後は署名ファイル取得、Xcode project、IPA、TestFlight送信まで自動化する構成を追加。
- ゲームロジック/save schema v4は変更なし。
