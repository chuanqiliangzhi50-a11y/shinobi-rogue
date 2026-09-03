# iOS Export Setup — Ver.1.0.45 APP STORE PREP

Windows側で可能な準備は完了。ネイティブiOS書き出しはmacOS + Xcodeで行う。

## Macで入力する所有者情報
- Apple Developer Team ID
- 一意なBundle Identifier（例の com.example... は使用禁止）
- Apple DeveloperのSigning設定

## 現在のテンプレート
- short version: 1.0.45
- build: 45
- arm64: enabled
- minimum iOS: 15.0
- Xcode project-only export
- 1024×1024 App Store icon
- 初回リリース: 広告SDKなし / 解析SDKなし / 外部トラッキングなし

`export_presets.ios.template.cfg` の Team ID と Bundle Identifier を所有者情報へ置換して使用する。
