# Codemagic + Apple 本人操作ハンドオフ

Ver.1.0.47 CODEMAGIC READY

## こちらで完了済み
- Godot 4.7.2 のクラウドMac導入
- Godot回帰テスト用ワークフロー
- iOS Xcodeプロジェクト生成
- App Store用署名ファイル取得・IPA生成・TestFlight送信のワークフロー雛形
- 初回リリースは広告/トラッキングOFF

## 本人操作が不可避になる地点
1. Apple Developer Programへの加入/契約同意（未加入の場合）
2. App Store ConnectでAPIアクセスを有効化し、Codemagic専用APIキーを生成
3. APIキー(.p8)、Issuer ID、Key IDをCodemagicのDeveloper Portal integrationへ登録
4. App Store Connectでアプリレコードを作成し、最終Bundle IDを確定
5. CodemagicでGitリポジトリを接続し、APPLE_TEAM_ID / IOS_BUNDLE_IDを設定

API秘密鍵はチャットへ貼らないこと。Codemagicへ直接登録する。
