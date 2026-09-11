# 忍道 - SHINOBI ROGUE v1.0.54 Release Handoff

## 現在できること
- Codemagic: Web release workflow
- Codemagic: iOS preflight workflow
- Codemagic: App Store/TestFlight workflow scaffold
- Windows/Linux: Web export script
- PWA Web export preset

## Codemagicへ渡す前提
このリリース用ZIPは `project.godot` と `codemagic.yaml` がZIP直下にあります。
展開したフォルダをリポジトリ直下として扱ってください。

## Web版
Codemagic workflow:
`shinobi-web-release`

出力:
`shinobi_rogue_web_v1_0_54.zip`

Web版はiPhone Safariでの実機確認に使用できます。

## iOS事前検査
Codemagic workflow:
`shinobi-ios-preflight`

Apple署名なしで、Godot起動・リソースImport・回帰テストまで確認します。

## TestFlight / App Store
Codemagic workflow:
`shinobi-ios-appstore`

実行前に必要:
1. Apple Developer Program加入
2. 最終Bundle ID
3. Apple Team ID
4. Codemagic App Store Connect integration名 `ShinobiRogue-AppStore`
5. Signing certificate / provisioning profile またはCodemagicの署名設定

`codemagic.yaml` の以下を実値へ変更:
- `REPLACE_WITH_FINAL_BUNDLE_ID`
- `REPLACE_WITH_10_CHAR_TEAM_ID`

## 注意
この環境にはGodot本体が無いため、ここではランタイムPASSは確認していません。
Codemagicの `Godot regression` が最初のランタイム検証になります。
