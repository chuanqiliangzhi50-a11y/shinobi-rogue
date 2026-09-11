# Codemagic 最小操作手順 — SHINOBI ROGUE v1.0.54

## まず行う
1. `shinobi_rogue_v1_0_54_RELEASE_PREP.zip` を展開。
2. 展開した中身をGitHubリポジトリ直下へ置く。
3. Codemagicでそのリポジトリを追加。

## 最初の実行
Apple設定はまだ不要です。

Codemagicで  
`shinobi-web-release`  
を選んでBuildを開始。

成功条件:
- Godot regression PASS
- Web export PASS
- `shinobi_rogue_web_v1_0_54.zip` がArtifactsに出る

これが最初の実動確認です。

## 次に実行
`shinobi-ios-preflight`

これは署名前のiOS事前確認です。
Godot起動・Import・回帰テストまで確認します。

## TestFlightへ進む時だけ必要
以下4点を用意します。

1. Apple Developer Program加入
2. 最終Bundle ID
3. Apple Team ID
4. App Store Connect API keyをCodemagicへ登録

`codemagic.yaml` の
- `REPLACE_WITH_FINAL_BUNDLE_ID`
- `REPLACE_WITH_10_CHAR_TEAM_ID`

を実値へ変更します。

Codemagic側のApp Store Connect integration名は
`ShinobiRogue-AppStore`
に合わせます。

その後、
`shinobi-ios-appstore`
を実行します。

成功時はIPA作成後、TestFlightへ送信します。
App Store本番提出は自動実行しない設定です。

## 現時点の推奨順
Web release → iOS preflight → Apple設定 → TestFlight

この順なら、Apple Developer登録前でもゲーム本体の実動不具合を先に切り分けできます。
