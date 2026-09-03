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
