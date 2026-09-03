# Codemagic / iOS build path

Goal: build the iOS project without buying a Mac.

## Prepared in this package
- Godot iOS export preset template
- `codemagic.yaml` workflow scaffold
- iOS 15+, arm64, project-only export settings
- Initial release keeps ads/tracking disabled

## Secrets intentionally NOT stored in this ZIP
Codemagic/Apple credentials and signing material must be entered in the service account UI, never committed to the project.

Required later:
1. Apple Developer Program membership.
2. App Store Connect API key / issuer ID / key ID.
3. Apple Team ID and final unique Bundle ID.
4. Signing certificate + provisioning profile, or Codemagic automatic signing configuration.

## Workflow
The scaffold installs Godot 4.7.2 on the macOS build machine, copies the iOS template preset to `export_presets.cfg`, replaces Team ID / Bundle ID from environment variables, downloads Godot export templates, and exports an Xcode project to `build/ios/ShinobiRogue.xcodeproj`.

The archive/upload stage is deliberately left for the credential/signing step because those values do not yet exist in the project.
