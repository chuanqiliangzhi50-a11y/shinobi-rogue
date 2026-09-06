# 忍道 - SHINOBI ROGUE Web Release Plan

Target date: 2026-09-27
Release strategy: zero initial cost, Web-first.

## Goal
1. Build and release with initial cost 0 yen.
2. First, make the Web/PWA build easy for the developer to play repeatedly on iPhone.
3. Improve quality from real play feedback before public promotion.
4. Publish a free version designed for ad-supported distribution.
5. Prepare a paid ad-free Premium version priced at roughly 500-1000 yen through a compatible sales channel.

## Milestones
- 2026-09-06 to 09-09: stable personal-play Web/PWA build.
- 2026-09-10 to 09-15: developer playtest and issue collection.
- 2026-09-16 to 09-20: bug, balance, usability, and presentation fixes.
- 2026-09-21 to 09-23: release candidate and regression freeze.
- 2026-09-24 to 09-25: FREE/PREMIUM packaging and public-page preparation.
- 2026-09-26: final release checks.
- 2026-09-27: public release / platform submission complete.

## Release model
### FREE
- Full game playable without purchase.
- Ad integration is added only for the public distribution target and only in allowed placements.
- Game logic remains shared with PREMIUM.

### PREMIUM
- Same core game content.
- No ads.
- Target price: 500-1000 yen.

## Priority order
1. Crash / progression-blocking bugs
2. Save integrity
3. Touch controls and readability
4. Game balance
5. Player guidance
6. Presentation polish
7. New features

## Current baseline
Ver.1.0.49 is the validated baseline. The prior Codemagic macOS Godot 4.7.2 regression completed with `SHINOBI_REGRESSION PASS ALL:` and the previous iPhone Safari smoke test passed basic movement and dungeon start.

## Ver.1.0.51 automation milestone
Codemagic now owns the reproducible Web build path. Run `Shinobi Rogue Web release`; a successful build must complete Godot regression with `PASS ALL`, export `web/index.html`, verify `.wasm` and `.pck`, and publish `shinobi_rogue_web_v1_0_51.zip` as an artifact. No Apple Developer credentials are required.
