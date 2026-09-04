# 忍道 - SHINOBI ROGUE Ver.1.0.49 CODEMAGIC HEADLESS FIX RC

## Ver.1.0.49

- Codemagic headless regressionで`ui_glyph_texture`がnullのまま描画される問題を防止。
- `draw_ui_text()`にnull textureガードを追加。
- headless self-test時は`queue_redraw()`を行わない。
- Codemagic regressionは`SHINOBI_REGRESSION PASS ALL:`を必須化し、`ERROR:`行があればビルドを失敗させる。
- ゲームルール、save schema v4、広告OFF方針は変更なし。


Codemagic clean-checkout regression fix release. Game rules/save schema are unchanged from Ver.1.0.47.

- Avoids parsing-time preload of `ui_glyphs.png` during clean CI regression.
- Loads the glyph texture only for normal gameplay, after regression-mode early exit.
- Adds a dedicated Godot resource-import step before regression/export.
- Keeps save schema v4 and existing gameplay logic.

# 忍道 - SHINOBI ROGUE Ver.1.0.43 FINAL DEVICE RC

App Storeネイティブ化直前の最終iPhoneスモークテスト候補版。

- 100階ローグライク
- セーブschema v4互換
- 初回版広告/トラッキングなし
- iPhone縦画面UI
- OSフォント非依存の日本語UI
- Windows自動preflight + Godot headless regression
- iOS project-only export template
- App Storeメタデータ/プライバシー/サポート草案

次のユーザー操作は原則1回のFINAL DEVICE TESTのみ。重大不具合がなければMac/Xcode工程へ移行する。


## Ver.1.0.46
- Visual redesign direction is provisional and can be replaced later without changing the game rules.
- Added Codemagic macOS/iOS project-export scaffold to pursue a no-Mac-purchase release path.
