# WEB EXPORT GUIDE — Ver.1.0.42 RELEASE RC2

WebはiPhone実機UI確認用です。App Store提出物そのものではありません。

1. Godot 4.7.2でプロジェクトを開く。
2. Project > Export > Web。
3. 「デバッグ付きエクスポート」をOFF。
4. `web/index.html` へRelease export。
5. HTTPS経由でiPhone Safariから確認する。

このRCでは日本語表示を `ui_glyphs.png` に統一しているため、OS/browser側の日本語フォント有無には依存しません。
