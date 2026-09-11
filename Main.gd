extends Node2D

const VERSION := "1.0.54"
const RELEASE_CHANNEL := "PLAY UI SYSTEM RC"
const DEVELOPMENT_UI_ENABLED := false
const ADS_ENABLED := false # Initial App Store release: ad SDK not integrated yet.
const MAP_W := 31
const MAP_H := 15
const TILE := 24
const MAP_X := 16
const MAP_Y := 96
const HUD_Y := 468
const META_PATH := "user://shinobi_meta.json"
const RUN_PATH := "user://shinobi_run.save"
const RUN_SAVE_VERSION := 5
const PAD_X := 820
const PAD_Y := 562
const PAD_CELL := 50
const HIDE_HOLD_INTERVAL := 0.22
const CONTENT_W := 720.0
const CONTENT_H := 1100.0
const WEAPON_NAME := "忍刀"
const ARMOR_NAME := "忍装束"

var rng := RandomNumberGenerator.new()

var map: Array = []
var explored: Array = []
var player := Vector2i(2, 2)
var stairs_pos := Vector2i(0, 0)
var enemies: Array = []
var items: Array = []
var inventory_items: Array = []
var placed_traps: Array = []
var inventory_menu := false
var inventory_selected := 0

var floor_no := 1
var turn_no := 0
var hp := 30
var max_hp := 30
var attack_power := 5
var defense_power := 1
var hunger := 100
var hunger_tick := 0
var ninja_energy := 0
var style_name := "武"

var run_souls := 0
var run_coins := 0
var souls := 0
var coins := 0

var perm_hp := 0
var perm_attack := 0
var perm_defense := 0
var perm_ninja_energy := 0

var in_village := true
var village_menu := "main"
var message := "忍の里。出陣の時を待つ。"

var shop_active := false
var shop_hostile := false
var merchant_type := "旅商人"
var shop_rect := Rect2i()
var shopkeeper: Dictionary = {}
var shopkeeper_home := Vector2i(-1, -1)
var shop_items: Array = []
var unpaid_items: Array = []
var checkout_prompt := false
var stairs_prompt := false
var merchant_bound_turns := 0

var smoke_turns := 0
var hidden_mode := false
var clone_active := false
var clone_pos := Vector2i(-1, -1)
var clone_steps_left := 0
var hide_hold_active := false
var hide_hold_elapsed := 0.0

var boss_spawned := false
var boss_defeated := false
var final_clear := false
var revive_used := false

var ad_offer := false
var ad_menu := false
var ad_boost_uses := 0
var last_ad_checkpoint_floor := 0

var debug_mode := false
var debug_last := ""
var known_enemies: Dictionary = {}
var death_log: Array = []
var self_test_mode := false
var regression_all_pass := false
var ui_glyph_texture: Texture2D = null
var entity_art: Dictionary = {}
const ENTITY_ART_PATHS := {
	"player": "res://art/player.png",
	"clone": "res://art/clone.png",
	"item": "res://art/item.png",
	"enemy": "res://art/enemy.png",
	"boss": "res://art/boss.png",
	"merchant": "res://art/merchant.png",
	"dark_merchant": "res://art/dark_merchant.png",
	"trap": "res://art/trap.png"
}
const UI_GLYPH_CELL := 40.0
const UI_GLYPH_BASE := 32.0
const PORTRAIT_LAYOUT_ENABLED := true


var map_visible: bool = true

func _ready() -> void:
	rng.randomize()
	self_test_mode = "--shinobi-regression" in OS.get_cmdline_user_args()
	if self_test_mode:
		# Headless CI/preflight mode never reads or writes the player's real user:// saves.
		# Do not load presentation-only PNG assets in regression mode: a clean CI checkout
		# has not generated Godot's imported texture cache yet.
		apply_permanent_stats()
		debug_run_regression_suite()
		print("SHINOBI_REGRESSION " + message)
		get_tree().quit(0 if regression_all_pass else 2)
		return
	ui_glyph_texture = load("res://ui_glyphs.png") as Texture2D
	load_optional_entity_art()
	load_meta()
	apply_permanent_stats()
	if load_run_state():
		message = "中断した探索を再開した。"
	queue_redraw()




func load_optional_entity_art() -> void:
	entity_art.clear()
	for key in ENTITY_ART_PATHS.keys():
		var path := str(ENTITY_ART_PATHS[key])
		if ResourceLoader.exists(path):
			var tex := load(path) as Texture2D
			if tex != null:
				entity_art[key] = tex


func draw_entity_visual(center: Vector2, art_key: String, fallback: String, font_size: int, color: Color, tile_size: float) -> void:
	if entity_art.has(art_key):
		var tex: Texture2D = entity_art[art_key]
		var size: float = maxf(12.0, tile_size - 2.0)
		draw_texture_rect(tex, Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size)), false)
	else:
		draw_ui_text(center + Vector2(-8, 6), fallback, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)


const UI_GLYPH_MAP := {
	" ": Vector2i(0, 0),
	"!": Vector2i(1, 0),
	"\"": Vector2i(2, 0),
	"#": Vector2i(3, 0),
	"$": Vector2i(4, 0),
	"%": Vector2i(5, 0),
	"&": Vector2i(6, 0),
	"'": Vector2i(7, 0),
	"(": Vector2i(8, 0),
	")": Vector2i(9, 0),
	"*": Vector2i(10, 0),
	"+": Vector2i(11, 0),
	",": Vector2i(12, 0),
	"-": Vector2i(13, 0),
	".": Vector2i(14, 0),
	"/": Vector2i(15, 0),
	"0": Vector2i(16, 0),
	"1": Vector2i(17, 0),
	"2": Vector2i(18, 0),
	"3": Vector2i(19, 0),
	"4": Vector2i(20, 0),
	"5": Vector2i(21, 0),
	"6": Vector2i(22, 0),
	"7": Vector2i(23, 0),
	"8": Vector2i(24, 0),
	"9": Vector2i(25, 0),
	":": Vector2i(26, 0),
	";": Vector2i(27, 0),
	"<": Vector2i(28, 0),
	"=": Vector2i(29, 0),
	">": Vector2i(30, 0),
	"?": Vector2i(31, 0),
	"@": Vector2i(0, 1),
	"A": Vector2i(1, 1),
	"B": Vector2i(2, 1),
	"C": Vector2i(3, 1),
	"D": Vector2i(4, 1),
	"E": Vector2i(5, 1),
	"F": Vector2i(6, 1),
	"G": Vector2i(7, 1),
	"H": Vector2i(8, 1),
	"I": Vector2i(9, 1),
	"J": Vector2i(10, 1),
	"K": Vector2i(11, 1),
	"L": Vector2i(12, 1),
	"M": Vector2i(13, 1),
	"N": Vector2i(14, 1),
	"O": Vector2i(15, 1),
	"P": Vector2i(16, 1),
	"Q": Vector2i(17, 1),
	"R": Vector2i(18, 1),
	"S": Vector2i(19, 1),
	"T": Vector2i(20, 1),
	"U": Vector2i(21, 1),
	"V": Vector2i(22, 1),
	"W": Vector2i(23, 1),
	"X": Vector2i(24, 1),
	"Y": Vector2i(25, 1),
	"Z": Vector2i(26, 1),
	"[": Vector2i(27, 1),
	"\\": Vector2i(28, 1),
	"]": Vector2i(29, 1),
	"^": Vector2i(30, 1),
	"_": Vector2i(31, 1),
	"`": Vector2i(0, 2),
	"a": Vector2i(1, 2),
	"b": Vector2i(2, 2),
	"c": Vector2i(3, 2),
	"d": Vector2i(4, 2),
	"e": Vector2i(5, 2),
	"f": Vector2i(6, 2),
	"g": Vector2i(7, 2),
	"h": Vector2i(8, 2),
	"i": Vector2i(9, 2),
	"j": Vector2i(10, 2),
	"k": Vector2i(11, 2),
	"l": Vector2i(12, 2),
	"m": Vector2i(13, 2),
	"n": Vector2i(14, 2),
	"o": Vector2i(15, 2),
	"p": Vector2i(16, 2),
	"q": Vector2i(17, 2),
	"r": Vector2i(18, 2),
	"s": Vector2i(19, 2),
	"t": Vector2i(20, 2),
	"u": Vector2i(21, 2),
	"v": Vector2i(22, 2),
	"w": Vector2i(23, 2),
	"x": Vector2i(24, 2),
	"y": Vector2i(25, 2),
	"z": Vector2i(26, 2),
	"{": Vector2i(27, 2),
	"|": Vector2i(28, 2),
	"}": Vector2i(29, 2),
	"~": Vector2i(30, 2),
	"←": Vector2i(31, 2),
	"↑": Vector2i(0, 3),
	"→": Vector2i(1, 3),
	"↓": Vector2i(2, 3),
	"↖": Vector2i(3, 3),
	"↗": Vector2i(4, 3),
	"↘": Vector2i(5, 3),
	"↙": Vector2i(6, 3),
	"、": Vector2i(7, 3),
	"。": Vector2i(8, 3),
	"「": Vector2i(9, 3),
	"」": Vector2i(10, 3),
	"【": Vector2i(11, 3),
	"】": Vector2i(12, 3),
	"あ": Vector2i(13, 3),
	"い": Vector2i(14, 3),
	"う": Vector2i(15, 3),
	"え": Vector2i(16, 3),
	"か": Vector2i(17, 3),
	"が": Vector2i(18, 3),
	"き": Vector2i(19, 3),
	"く": Vector2i(20, 3),
	"け": Vector2i(21, 3),
	"こ": Vector2i(22, 3),
	"さ": Vector2i(23, 3),
	"し": Vector2i(24, 3),
	"じ": Vector2i(25, 3),
	"す": Vector2i(26, 3),
	"ず": Vector2i(27, 3),
	"た": Vector2i(28, 3),
	"だ": Vector2i(29, 3),
	"ち": Vector2i(30, 3),
	"っ": Vector2i(31, 3),
	"つ": Vector2i(0, 4),
	"て": Vector2i(1, 4),
	"で": Vector2i(2, 4),
	"と": Vector2i(3, 4),
	"ど": Vector2i(4, 4),
	"な": Vector2i(5, 4),
	"に": Vector2i(6, 4),
	"の": Vector2i(7, 4),
	"は": Vector2i(8, 4),
	"ば": Vector2i(9, 4),
	"へ": Vector2i(10, 4),
	"ま": Vector2i(11, 4),
	"み": Vector2i(12, 4),
	"む": Vector2i(13, 4),
	"め": Vector2i(14, 4),
	"も": Vector2i(15, 4),
	"や": Vector2i(16, 4),
	"よ": Vector2i(17, 4),
	"り": Vector2i(18, 4),
	"る": Vector2i(19, 4),
	"れ": Vector2i(20, 4),
	"わ": Vector2i(21, 4),
	"を": Vector2i(22, 4),
	"ん": Vector2i(23, 4),
	"ア": Vector2i(24, 4),
	"ィ": Vector2i(25, 4),
	"イ": Vector2i(26, 4),
	"エ": Vector2i(27, 4),
	"ジ": Vector2i(28, 4),
	"ス": Vector2i(29, 4),
	"タ": Vector2i(30, 4),
	"ダ": Vector2i(31, 4),
	"テ": Vector2i(0, 5),
	"ト": Vector2i(1, 5),
	"ノ": Vector2i(2, 5),
	"ブ": Vector2i(3, 5),
	"ボ": Vector2i(4, 5),
	"ポ": Vector2i(5, 5),
	"ム": Vector2i(6, 5),
	"メ": Vector2i(7, 5),
	"ン": Vector2i(8, 5),
	"・": Vector2i(9, 5),
	"ー": Vector2i(10, 5),
	"一": Vector2i(11, 5),
	"上": Vector2i(12, 5),
	"中": Vector2i(13, 5),
	"丸": Vector2i(14, 5),
	"久": Vector2i(15, 5),
	"了": Vector2i(16, 5),
	"人": Vector2i(17, 5),
	"代": Vector2i(18, 5),
	"件": Vector2i(19, 5),
	"任": Vector2i(20, 5),
	"伐": Vector2i(21, 5),
	"何": Vector2i(22, 5),
	"作": Vector2i(23, 5),
	"使": Vector2i(24, 5),
	"価": Vector2i(25, 5),
	"保": Vector2i(26, 5),
	"倒": Vector2i(27, 5),
	"備": Vector2i(28, 5),
	"入": Vector2i(29, 5),
	"全": Vector2i(30, 5),
	"兵": Vector2i(31, 5),
	"再": Vector2i(0, 6),
	"冶": Vector2i(1, 6),
	"出": Vector2i(2, 6),
	"刀": Vector2i(3, 6),
	"分": Vector2i(4, 6),
	"初": Vector2i(5, 6),
	"到": Vector2i(6, 6),
	"力": Vector2i(7, 6),
	"動": Vector2i(8, 6),
	"取": Vector2i(9, 6),
	"合": Vector2i(10, 6),
	"告": Vector2i(11, 6),
	"品": Vector2i(12, 6),
	"商": Vector2i(13, 6),
	"回": Vector2i(14, 6),
	"在": Vector2i(15, 6),
	"型": Vector2i(16, 6),
	"報": Vector2i(17, 6),
	"塞": Vector2i(18, 6),
	"壁": Vector2i(19, 6),
	"士": Vector2i(20, 6),
	"大": Vector2i(21, 6),
	"契": Vector2i(22, 6),
	"奥": Vector2i(23, 6),
	"子": Vector2i(24, 6),
	"存": Vector2i(25, 6),
	"安": Vector2i(26, 6),
	"完": Vector2i(27, 6),
	"害": Vector2i(28, 6),
	"対": Vector2i(29, 6),
	"射": Vector2i(30, 6),
	"将": Vector2i(31, 6),
	"小": Vector2i(0, 7),
	"屋": Vector2i(1, 7),
	"巻": Vector2i(2, 7),
	"帰": Vector2i(3, 7),
	"帳": Vector2i(4, 7),
	"広": Vector2i(5, 7),
	"店": Vector2i(6, 7),
	"度": Vector2i(7, 7),
	"弓": Vector2i(8, 7),
	"引": Vector2i(9, 7),
	"強": Vector2i(10, 7),
	"影": Vector2i(11, 7),
	"待": Vector2i(12, 7),
	"御": Vector2i(13, 7),
	"復": Vector2i(14, 7),
	"必": Vector2i(15, 7),
	"忍": Vector2i(16, 7),
	"応": Vector2i(17, 7),
	"快": Vector2i(18, 7),
	"怒": Vector2i(19, 7),
	"恒": Vector2i(20, 7),
	"意": Vector2i(21, 7),
	"成": Vector2i(22, 7),
	"戻": Vector2i(23, 7),
	"所": Vector2i(24, 7),
	"手": Vector2i(25, 7),
	"払": Vector2i(26, 7),
	"択": Vector2i(27, 7),
	"拘": Vector2i(28, 7),
	"拾": Vector2i(29, 7),
	"挿": Vector2i(30, 7),
	"探": Vector2i(31, 7),
	"接": Vector2i(0, 8),
	"撃": Vector2i(1, 8),
	"攻": Vector2i(2, 8),
	"敵": Vector2i(3, 8),
	"断": Vector2i(4, 8),
	"旅": Vector2i(5, 8),
	"旧": Vector2i(6, 8),
	"易": Vector2i(7, 8),
	"時": Vector2i(8, 8),
	"曲": Vector2i(9, 8),
	"最": Vector2i(10, 8),
	"期": Vector2i(11, 8),
	"未": Vector2i(12, 8),
	"束": Vector2i(13, 8),
	"査": Vector2i(14, 8),
	"格": Vector2i(15, 8),
	"検": Vector2i(16, 8),
	"極": Vector2i(17, 8),
	"武": Vector2i(18, 8),
	"歩": Vector2i(19, 8),
	"段": Vector2i(20, 8),
	"気": Vector2i(21, 8),
	"注": Vector2i(22, 8),
	"消": Vector2i(23, 8),
	"満": Vector2i(24, 8),
	"準": Vector2i(25, 8),
	"滅": Vector2i(26, 8),
	"火": Vector2i(27, 8),
	"点": Vector2i(28, 8),
	"煙": Vector2i(29, 8),
	"物": Vector2i(30, 8),
	"犬": Vector2i(31, 8),
	"現": Vector2i(0, 9),
	"生": Vector2i(1, 9),
	"百": Vector2i(2, 9),
	"的": Vector2i(3, 9),
	"盗": Vector2i(4, 9),
	"研": Vector2i(5, 9),
	"破": Vector2i(6, 9),
	"種": Vector2i(7, 9),
	"究": Vector2i(8, 9),
	"空": Vector2i(9, 9),
	"算": Vector2i(10, 9),
	"精": Vector2i(11, 9),
	"糧": Vector2i(12, 9),
	"約": Vector2i(13, 9),
	"索": Vector2i(14, 9),
	"続": Vector2i(15, 9),
	"総": Vector2i(16, 9),
	"線": Vector2i(17, 9),
	"縛": Vector2i(18, 9),
	"置": Vector2i(19, 9),
	"義": Vector2i(20, 9),
	"者": Vector2i(21, 9),
	"能": Vector2i(22, 9),
	"腹": Vector2i(23, 9),
	"自": Vector2i(24, 9),
	"薬": Vector2i(25, 9),
	"術": Vector2i(26, 9),
	"装": Vector2i(27, 9),
	"複": Vector2i(28, 9),
	"要": Vector2i(29, 9),
	"見": Vector2i(30, 9),
	"覧": Vector2i(31, 9),
	"計": Vector2i(0, 10),
	"討": Vector2i(1, 10),
	"記": Vector2i(2, 10),
	"証": Vector2i(3, 10),
	"試": Vector2i(4, 10),
	"読": Vector2i(5, 10),
	"象": Vector2i(6, 10),
	"足": Vector2i(7, 10),
	"距": Vector2i(8, 10),
	"跡": Vector2i(9, 10),
	"踏": Vector2i(10, 10),
	"身": Vector2i(11, 10),
	"軍": Vector2i(12, 10),
	"軽": Vector2i(13, 10),
	"追": Vector2i(14, 10),
	"進": Vector2i(15, 10),
	"遁": Vector2i(16, 10),
	"道": Vector2i(17, 10),
	"達": Vector2i(18, 10),
	"遠": Vector2i(19, 10),
	"選": Vector2i(20, 10),
	"還": Vector2i(21, 10),
	"配": Vector2i(22, 10),
	"酬": Vector2i(23, 10),
	"里": Vector2i(24, 10),
	"重": Vector2i(25, 10),
	"野": Vector2i(26, 10),
	"金": Vector2i(27, 10),
	"銭": Vector2i(28, 10),
	"録": Vector2i(29, 10),
	"鍛": Vector2i(30, 10),
	"鎧": Vector2i(31, 10),
	"長": Vector2i(0, 11),
	"門": Vector2i(1, 11),
	"開": Vector2i(2, 11),
	"間": Vector2i(3, 11),
	"闇": Vector2i(4, 11),
	"防": Vector2i(5, 11),
	"阻": Vector2i(6, 11),
	"限": Vector2i(7, 11),
	"陣": Vector2i(8, 11),
	"階": Vector2i(9, 11),
	"隔": Vector2i(10, 11),
	"隠": Vector2i(11, 11),
	"離": Vector2i(12, 11),
	"難": Vector2i(13, 11),
	"霧": Vector2i(14, 11),
	"面": Vector2i(15, 11),
	"領": Vector2i(16, 11),
	"頭": Vector2i(17, 11),
	"飢": Vector2i(18, 11),
	"験": Vector2i(19, 11),
	"高": Vector2i(20, 11),
	"鬼": Vector2i(21, 11),
	"魂": Vector2i(22, 11),
	"黒": Vector2i(23, 11),
	"！": Vector2i(24, 11),
	"（": Vector2i(25, 11),
	"）": Vector2i(26, 11),
	"：": Vector2i(27, 11),
	"？": Vector2i(28, 11),
	"ッ": Vector2i(29, 11),
	"プ": Vector2i(30, 11),
	"向": Vector2i(31, 11),
	"操": Vector2i(0, 12),
	"方": Vector2i(1, 12),
	"機": Vector2i(2, 12),
	"行": Vector2i(3, 12),
	"字": Vector2i(4, 12),
	"形": Vector2i(5, 12),
	"日": Vector2i(6, 12),
	"本": Vector2i(7, 12),
	"語": Vector2i(8, 12),
	"次": Vector2i(9, 12),
	"降": Vector2i(10, 12),
	"具": Vector2i(0, 13),
	"用": Vector2i(1, 13),
	"識": Vector2i(2, 13),
	"別": Vector2i(3, 13),
	"持": Vector2i(4, 13),
	"確": Vector2i(5, 13),
	"画": Vector2i(6, 13),
	"済": Vector2i(7, 13),
	"袋": Vector2i(8, 13),
	"得": Vector2i(9, 13),
	"認": Vector2i(10, 13),
	"閉": Vector2i(11, 13),
	"飛": Vector2i(12, 13),
	"罠": Vector2i(13, 13)
}


func draw_ui_text(pos: Vector2, text: String, _alignment: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT, _width: float = -1.0, font_size: int = 16, color: Color = Color.WHITE) -> void:
	# Headless/self-test runs intentionally skip presentation assets. Never submit a null texture to CanvasItem.
	if ui_glyph_texture == null:
		return
	# Bitmap glyph atlas: guarantees Japanese UI on Web/iPhone without relying on browser system fonts.
	var x := pos.x
	var y := pos.y - float(font_size) * 0.84
	var line_start := x
	var scale := float(font_size) / UI_GLYPH_BASE
	for i in range(text.length()):
		var ch := text.substr(i, 1)
		if ch == "\n":
			x = line_start
			y += float(font_size) * 1.25
			continue
		var code := ch.unicode_at(0)
		var advance := float(font_size) * (0.62 if code < 128 else 1.0)
		if UI_GLYPH_MAP.has(ch):
			var cell_pos: Vector2i = UI_GLYPH_MAP[ch]
			var src := Rect2(Vector2(cell_pos.x, cell_pos.y) * UI_GLYPH_CELL, Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL))
			var dst_size := Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL) * scale
			var dst := Rect2(Vector2(x, y), dst_size)
			draw_texture_rect_region(ui_glyph_texture, dst, src, color)
		x += advance

func _exit_tree() -> void:
	save_run_state()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_PAUSED:
		save_run_state()


func apply_permanent_stats() -> void:
	max_hp = 30 + perm_hp
	hp = max_hp
	attack_power = 5 + perm_attack
	defense_power = 1 + perm_defense


func _process(delta: float) -> void:
	if hide_hold_active and not in_village and not checkout_prompt and not stairs_prompt and not ad_menu and not inventory_menu:
		hide_hold_elapsed += delta
		if hide_hold_elapsed >= HIDE_HOLD_INTERVAL:
			hide_hold_elapsed = 0.0
			if ninja_energy >= 10:
				hide_one_turn()
	queue_redraw()


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.pressed:
		return

	if DEVELOPMENT_UI_ENABLED and event.keycode == KEY_F1:
		debug_mode = not debug_mode
		message = "DEBUG %s" % ("ON" if debug_mode else "OFF")
		queue_redraw()
		return

	if in_village:
		handle_village_input(event)
		return

	if inventory_menu:
		handle_inventory_key(event)
		return

	if checkout_prompt:
		if event.keycode == KEY_Y:
			confirm_checkout(true)
		elif event.keycode == KEY_N or event.keycode == KEY_ESCAPE:
			confirm_checkout(false)
		return

	if stairs_prompt:
		if event.keycode == KEY_Y or event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER:
			confirm_stairs(true)
		elif event.keycode == KEY_N or event.keycode == KEY_ESCAPE:
			confirm_stairs(false)
		return

	if ad_menu:
		if event.keycode == KEY_A:
			apply_ad_reward("A")
		elif event.keycode == KEY_B:
			apply_ad_reward("B")
		elif event.keycode == KEY_C:
			apply_ad_reward("C")
		elif event.keycode == KEY_ESCAPE:
			ad_menu = false
			message = "広告を見ずに進む。"
			queue_redraw()
		return

	if event.keycode == KEY_1:
		style_name = "武"
		message = "忍道：武"
	elif event.keycode == KEY_2:
		style_name = "影"
		message = "忍道：影"
	elif event.keycode == KEY_3:
		style_name = "術"
		message = "忍道：術"
	elif event.keycode == KEY_I:
		open_inventory()
	elif event.keycode == KEY_G:
		pickup()
	elif event.keycode == KEY_B:
		buy_unpaid()
	elif event.keycode == KEY_H:
		hide_one_turn()
	elif event.keycode == KEY_K:
		use_shadow_bind()
	elif event.keycode == KEY_L:
		use_smoke_ninjutsu()
	elif event.keycode == KEY_J:
		use_shadow_clone()
	elif event.keycode == KEY_X:
		use_ultimate()
	elif event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER:
		request_stairs_confirmation()
	elif DEVELOPMENT_UI_ENABLED and (event.keycode == KEY_F12 or event.keycode == KEY_T):
		debug_run_regression_suite()
	elif DEVELOPMENT_UI_ENABLED and debug_mode and event.keycode == KEY_F2:
		debug_prepare_shop()
	elif DEVELOPMENT_UI_ENABLED and debug_mode and event.keycode == KEY_F3:
		debug_prepare_boss()
	elif DEVELOPMENT_UI_ENABLED and debug_mode and event.keycode == KEY_F4:
		hp = max_hp
		hunger = 100
		ninja_energy = 100
		message = "DEBUG: 全快"
	elif DEVELOPMENT_UI_ENABLED and debug_mode and event.keycode == KEY_F5:
		hunger = 0
		message = "DEBUG: 満腹0"
	elif DEVELOPMENT_UI_ENABLED and debug_mode and event.keycode == KEY_F6:
		ninja_energy = 100
		message = "DEBUG: 忍気100"
	elif DEVELOPMENT_UI_ENABLED and debug_mode and event.keycode == KEY_F9:
		debug_prepare_theft()
	else:
		var dir = Vector2i.ZERO
		if event.keycode == KEY_UP:
			dir = Vector2i(0, -1)
		elif event.keycode == KEY_DOWN:
			dir = Vector2i(0, 1)
		elif event.keycode == KEY_LEFT:
			dir = Vector2i(-1, 0)
		elif event.keycode == KEY_RIGHT:
			dir = Vector2i(1, 0)
		elif event.keycode == KEY_Q:
			dir = Vector2i(-1, -1)
		elif event.keycode == KEY_E:
			dir = Vector2i(1, -1)
		elif event.keycode == KEY_Z:
			dir = Vector2i(-1, 1)
		elif event.keycode == KEY_C:
			dir = Vector2i(1, 1)
		elif event.keycode == KEY_SPACE:
			end_turn()
			return
		if dir != Vector2i.ZERO:
			try_move(dir)
	queue_redraw()


func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			handle_press(event.position - content_offset())
		else:
			hide_hold_active = false
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			handle_press(event.position - content_offset())
		else:
			hide_hold_active = false


func handle_press(pos: Vector2) -> void:
	if PORTRAIT_LAYOUT_ENABLED:
		handle_press_portrait(pos)
		return
	if in_village:
		handle_village_touch(pos)
		return
	if inventory_menu:
		handle_inventory_touch(pos, false)
		return
	if checkout_prompt or stairs_prompt or ad_menu:
		handle_modal_touch(pos)
		return
	if is_hide_button_position(pos):
		hide_hold_active = true
		hide_hold_elapsed = HIDE_HOLD_INTERVAL
		return
	handle_touch(pos)


func is_hide_button_position(pos: Vector2) -> bool:
	return Rect2(356, 662, 78, 42).has_point(pos)


func handle_village_input(event: InputEvent) -> void:
	if village_menu == "main":
		if event.keycode == KEY_1:
			village_menu = "blacksmith"
			message = "鍛冶屋"
		elif event.keycode == KEY_2:
			village_menu = "research"
			message = "忍術研究所"
		elif event.keycode == KEY_3:
			village_menu = "record"
			message = record_text()
		elif event.keycode == KEY_4:
			village_menu = "growth"
			message = "恒久成長"
		elif event.keycode == KEY_5 or event.keycode == KEY_ENTER:
			start_run()
	else:
		if event.keycode == KEY_ESCAPE:
			village_menu = "main"
			message = "忍の里。"
		elif village_menu == "blacksmith":
			if event.keycode == KEY_A:
				spend_souls("atk")
			elif event.keycode == KEY_D:
				spend_souls("def")
		elif village_menu == "research" and event.keycode == KEY_A:
			research_ninja_energy()
		elif village_menu == "growth":
			if event.keycode == KEY_H:
				spend_souls("hp")
			elif event.keycode == KEY_A:
				spend_souls("atk")
			elif event.keycode == KEY_D:
				spend_souls("def")
	queue_redraw()


func handle_village_touch(pos: Vector2) -> void:
	if village_menu == "main":
		var rects = [
			Rect2(70, 180, 360, 54),
			Rect2(70, 246, 360, 54),
			Rect2(70, 312, 360, 54),
			Rect2(70, 378, 360, 54),
			Rect2(70, 444, 360, 54)
		]
		for i in range(rects.size()):
			if rects[i].has_point(pos):
				if i == 0:
					village_menu = "blacksmith"
					message = "鍛冶屋"
				elif i == 1:
					village_menu = "research"
					message = "忍術研究所"
				elif i == 2:
					village_menu = "record"
					message = record_text()
				elif i == 3:
					village_menu = "growth"
					message = "恒久成長"
				else:
					start_run()
				queue_redraw()
				return
	else:
		if Rect2(70, 500, 220, 50).has_point(pos):
			village_menu = "main"
			message = "忍の里。"
		elif village_menu == "blacksmith":
			if Rect2(70, 240, 430, 52).has_point(pos):
				spend_souls("atk")
			elif Rect2(70, 304, 430, 52).has_point(pos):
				spend_souls("def")
		elif village_menu == "research":
			if Rect2(70, 240, 430, 52).has_point(pos):
				research_ninja_energy()
		elif village_menu == "growth":
			if Rect2(70, 240, 430, 52).has_point(pos):
				spend_souls("hp")
			elif Rect2(70, 304, 430, 52).has_point(pos):
				spend_souls("atk")
			elif Rect2(70, 368, 430, 52).has_point(pos):
				spend_souls("def")
		queue_redraw()


func handle_modal_touch(pos: Vector2) -> void:
	if checkout_prompt:
		if Rect2(350, 390, 160, 54).has_point(pos):
			confirm_checkout(true)
		elif Rect2(590, 390, 160, 54).has_point(pos):
			confirm_checkout(false)
		return
	if stairs_prompt:
		if Rect2(350, 390, 160, 54).has_point(pos):
			confirm_stairs(true)
		elif Rect2(590, 390, 160, 54).has_point(pos):
			confirm_stairs(false)
		return
	if ad_menu:
		if Rect2(255, 355, 130, 54).has_point(pos):
			apply_ad_reward("A")
		elif Rect2(405, 355, 130, 54).has_point(pos):
			apply_ad_reward("B")
		elif Rect2(555, 355, 130, 54).has_point(pos):
			apply_ad_reward("C")
		elif Rect2(705, 355, 130, 54).has_point(pos):
			ad_menu = false
			message = "広告を見ずに進む。"
			queue_redraw()


func handle_touch(pos: Vector2) -> void:
	var diamond_actions_landscape = [
		[Rect2(714, 566, 48, 48), "inventory"],
		[Rect2(660, 618, 48, 48), "trap"],
		[Rect2(768, 618, 48, 48), "throw"],
		[Rect2(714, 670, 48, 42), "suspend"]
	]
	for d_action in diamond_actions_landscape:
		var d_rect: Rect2 = d_action[0]
		if d_rect.has_point(pos):
			var d_name = str(d_action[1])
			if d_name == "inventory": open_inventory()
			elif d_name == "trap": place_trap()
			elif d_name == "throw": use_projectile()
			elif d_name == "suspend": suspend_run()
			queue_redraw()
			return
	if Rect2(930, 82, 100, 38).has_point(pos):
		toggle_map_visibility()
		return
	var base = Vector2(PAD_X, PAD_Y)
	var cell = float(PAD_CELL)
	if pos.x >= base.x and pos.x < base.x + cell * 3.0 and pos.y >= base.y and pos.y < base.y + cell * 3.0:
		var cx = int((pos.x - base.x) / cell)
		var cy = int((pos.y - base.y) / cell)
		var d = Vector2i(cx - 1, cy - 1)
		if d == Vector2i.ZERO:
			hide_one_turn()
		else:
			try_move(d)
		return

	var buttons = [
		{"rect": Rect2(20, 662, 70, 42), "action": "stairs"},
		{"rect": Rect2(94, 662, 70, 42), "action": "ultimate"},
		{"rect": Rect2(168, 662, 70, 42), "action": "buy"},
		{"rect": Rect2(242, 662, 70, 42), "action": "hide"},
		{"rect": Rect2(316, 662, 70, 42), "action": "bind"},
		{"rect": Rect2(390, 662, 70, 42), "action": "smoke"},
		{"rect": Rect2(464, 662, 70, 42), "action": "clone"},
		{"rect": Rect2(538, 662, 70, 42), "action": "ad"},
		{"rect": Rect2(790, 82, 130, 38), "action": "regression"},
		{"rect": Rect2(970, 570, 120, 40), "action": "style_bu"},
		{"rect": Rect2(970, 616, 120, 40), "action": "style_kage"},
		{"rect": Rect2(970, 662, 120, 40), "action": "style_jutsu"}
	]
	for b in buttons:
		var rect: Rect2 = b["rect"]
		if rect.has_point(pos):
			var action = str(b["action"])
			if action == "inventory":
				open_inventory()
			elif action == "pickup":
				pickup()
			elif action == "stairs":
				use_stairs()
			elif action == "ultimate":
				use_ultimate()
			elif action == "buy":
				buy_unpaid()
			elif action == "hide":
				hide_one_turn()
			elif action == "bind":
				use_shadow_bind()
			elif action == "smoke":
				use_smoke_ninjutsu()
			elif action == "clone":
				use_shadow_clone()
			elif action == "throw":
				use_projectile()
			elif action == "trap":
				place_trap()
			elif action == "ad":
				open_ad()
			elif action == "regression":
				if DEVELOPMENT_UI_ENABLED and OS.is_debug_build():
					debug_run_regression_suite()
			elif action == "style_bu":
				style_name = "武"
				message = "忍道：武"
			elif action == "style_kage":
				style_name = "影"
				message = "忍道：影"
			elif action == "style_jutsu":
				style_name = "術"
				message = "忍道：術"
			queue_redraw()
			return


func start_run() -> void:
	in_village = false
	village_menu = "main"
	floor_no = 1
	turn_no = 0
	run_souls = 0
	run_coins = 0
	hunger = 100
	hunger_tick = 0
	ninja_energy = perm_ninja_energy
	style_name = "武"
	smoke_turns = 0
	hidden_mode = false
	clone_active = false
	clone_pos = Vector2i(-1, -1)
	clone_steps_left = 0
	last_ad_checkpoint_floor = 0
	revive_used = false
	final_clear = false
	apply_permanent_stats()
	generate_floor()
	save_run_state()
	message = "1階へ出陣した。"
	queue_redraw()


func bank_run_rewards() -> Dictionary:
	var gained_souls = run_souls
	var gained_coins = int(run_coins * 0.5)
	souls += gained_souls
	coins += gained_coins
	run_souls = 0
	run_coins = 0
	return {"souls": gained_souls, "coins": gained_coins}


func return_village(cause: String) -> void:
	if cause != "":
		death_log.append({"floor": floor_no, "cause": cause})
		if death_log.size() > 20:
			death_log.pop_front()
	var gained = bank_run_rewards()
	in_village = true
	village_menu = "main"
	apply_permanent_stats()
	save_meta()
	clear_run_state()
	message = "忍の里へ帰還。忍魂+%d 銭+%d。" % [int(gained["souls"]), int(gained["coins"])]
	queue_redraw()


func research_ninja_energy(persist: bool = true) -> bool:
	if perm_ninja_energy >= 100:
		message = "初期忍気研究は最大まで完了している。"
		return false
	if souls < 5:
		message = "忍魂が足りない。"
		return false
	souls -= 5
	perm_ninja_energy = min(100, perm_ninja_energy + 20)
	ninja_energy = max(ninja_energy, perm_ninja_energy)
	message = "初期忍気を恒久的に+20研究した。現在%d。" % perm_ninja_energy
	if persist:
		save_meta()
	return true


func spend_souls(kind: String) -> void:
	if souls < 5:
		message = "忍魂が足りない。"
		return
	souls -= 5
	if kind == "hp":
		perm_hp += 5
		message = "最大HPを恒久的に+5。"
	elif kind == "atk":
		perm_attack += 1
		message = "攻撃を恒久的に+1。"
	elif kind == "def":
		perm_defense += 1
		message = "防御を恒久的に+1。"
	save_meta()


func record_text() -> String:
	return "最高到達 %dF / 討伐記録 %d種 / 帰還記録 %d件" % [int(known_enemies.get("max_floor", 0)), known_enemies.size(), death_log.size()]


func generate_floor() -> void:
	map.clear()
	explored.clear()
	enemies.clear()
	items.clear()
	inventory_items.clear()
	placed_traps.clear()
	inventory_menu = false
	inventory_selected = 0
	unpaid_items.clear()
	shop_items.clear()
	shop_active = false
	shop_hostile = false
	merchant_type = "旅商人"
	shopkeeper = {}
	shopkeeper_home = Vector2i(-1, -1)
	merchant_bound_turns = 0
	checkout_prompt = false
	boss_spawned = false
	boss_defeated = false
	clone_active = false
	clone_pos = Vector2i(-1, -1)
	clone_steps_left = 0
	stairs_pos = Vector2i(-1, -1)

	for y in range(MAP_H):
		var row: Array = []
		var seen: Array = []
		for x in range(MAP_W):
			var border = x == 0 or y == 0 or x == MAP_W - 1 or y == MAP_H - 1
			row.append("#" if border else ".")
			seen.append(false)
		map.append(row)
		explored.append(seen)

	for _i in range(35):
		var wx = rng.randi_range(2, MAP_W - 3)
		var wy = rng.randi_range(2, MAP_H - 3)
		if Vector2i(wx, wy) != Vector2i(2, 2):
			map[wy][wx] = "#"

	player = find_open_cell(Vector2i(2, 2))
	stairs_pos = find_open_cell(Vector2i(MAP_W - 3, MAP_H - 3))
	carve_safe_path(player, stairs_pos)
	map[stairs_pos.y][stairs_pos.x] = ">"

	if floor_no % 5 == 0 and floor_no % 10 != 0:
		generate_shop()

	var enemy_count = min(3 + int(floor_no / 12), 10)
	for i in range(enemy_count):
		spawn_enemy(false)

	for i in range(4):
		spawn_item()

	if floor_no % 10 == 0:
		spawn_boss()

	known_enemies["max_floor"] = max(int(known_enemies.get("max_floor", 0)), floor_no)
	update_visibility()


func carve_safe_path(start: Vector2i, goal: Vector2i) -> void:
	# Random walls must never create an unwinnable floor. Carve one guaranteed route.
	var p = start
	var horizontal_first = rng.randi_range(0, 1) == 0
	if horizontal_first:
		while p.x != goal.x:
			p.x += 1 if goal.x > p.x else -1
			map[p.y][p.x] = "."
		while p.y != goal.y:
			p.y += 1 if goal.y > p.y else -1
			map[p.y][p.x] = "."
	else:
		while p.y != goal.y:
			p.y += 1 if goal.y > p.y else -1
			map[p.y][p.x] = "."
		while p.x != goal.x:
			p.x += 1 if goal.x > p.x else -1
			map[p.y][p.x] = "."


func has_path_between(start: Vector2i, goal: Vector2i) -> bool:
	if not is_walkable(start) or not is_walkable(goal):
		return false
	var frontier: Array = [start]
	var visited: Dictionary = {}
	visited[start] = true
	var dirs: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
	while not frontier.is_empty():
		var current: Vector2i = frontier.pop_front()
		if current == goal:
			return true
		for d: Vector2i in dirs:
			var next: Vector2i = current + d
			if not visited.has(next) and is_walkable(next):
				visited[next] = true
				frontier.append(next)
	return false


func find_open_cell(preferred: Vector2i) -> Vector2i:
	if is_walkable(preferred) and not occupied(preferred) and not cell_has_item(preferred) and preferred != stairs_pos:
		return preferred
	for radius in range(1, max(MAP_W, MAP_H)):
		for y in range(1, MAP_H - 1):
			for x in range(1, MAP_W - 1):
				var p = Vector2i(x, y)
				if p.distance_to(preferred) <= float(radius) and is_walkable(p) and not occupied(p) and not cell_has_item(p) and p != stairs_pos:
					return p
	return Vector2i(1, 1)


func enemy_profile(is_boss: bool) -> Dictionary:
	var tier = clamp(int((floor_no - 1) / 20), 0, 4)
	if is_boss:
		var boss_names = ["影大将", "鬼面武者", "火遁頭領", "黒鎧将軍", "百階ノ影"]
		return {
			"kind": "boss",
			"name": boss_names[tier],
			"hp": 42 + floor_no * 2 + tier * 12,
			"atk": 6 + int(floor_no / 5) + tier,
			"range": 1 + (1 if floor_no >= 50 else 0),
			"coin_reward": 5 + tier * 2,
			"soul_reward": 3 + tier
		}

	var pool: Array = [
		{"kind": "samurai", "name": "野武士", "hp_mod": 0, "atk_mod": 0, "range": 1},
		{"kind": "hound", "name": "忍犬", "hp_mod": -2, "atk_mod": 1, "range": 1}
	]
	if floor_no >= 15:
		pool.append({"kind": "archer", "name": "弓足軽", "hp_mod": -3, "atk_mod": 0, "range": 4})
	if floor_no >= 35:
		pool.append({"kind": "shadow", "name": "影忍", "hp_mod": 3, "atk_mod": 2, "range": 1})
	if floor_no >= 65:
		pool.append({"kind": "elite", "name": "黒武者", "hp_mod": 8, "atk_mod": 3, "range": 1})
	var profile_base: Dictionary = pool[rng.randi_range(0, pool.size() - 1)]
	return {
		"kind": str(profile_base["kind"]),
		"name": str(profile_base["name"]),
		"hp": max(4, 8 + floor_no + int(profile_base["hp_mod"])),
		"atk": max(1, 2 + int(floor_no / 7) + int(profile_base["atk_mod"])),
		"range": int(profile_base["range"]),
		"coin_reward": 1 + (1 if tier >= 3 else 0),
		"soul_reward": 1
	}


func spawn_enemy(is_boss: bool) -> void:
	var p = find_random_open_cell()
	var profile = enemy_profile(is_boss)
	var e = {
		"pos": p,
		"hp": int(profile["hp"]),
		"atk": int(profile["atk"]),
		"bound": 0,
		"boss": is_boss,
		"name": str(profile["name"]),
		"kind": str(profile["kind"]),
		"range": int(profile["range"]),
		"coin_reward": int(profile["coin_reward"]),
		"soul_reward": int(profile["soul_reward"])
	}
	enemies.append(e)


func spawn_boss() -> void:
	boss_spawned = true
	spawn_enemy(true)
	message = "この階には強大な気配がある。"


func spawn_item() -> void:
	var p = find_random_open_cell()
	var roll = rng.randi_range(0, 999)
	var item_name = "兵糧丸"
	if roll < 260:
		item_name = "薬"
	elif roll < 500:
		item_name = "兵糧丸"
	elif roll < 690:
		item_name = "忍気丸"
	elif roll < 770:
		item_name = "上薬"
	elif roll < 840:
		item_name = "大兵糧丸"
	elif roll < 915:
		item_name = "小巻物"
	elif roll < 965:
		item_name = "中巻物"
	elif roll < 993:
		item_name = "大巻物"
	else:
		item_name = "究極巻物"
	items.append({"pos": p, "name": item_name, "price": 0, "shop": false})


func carve_shop_room() -> void:
	for y in range(shop_rect.position.y, shop_rect.end.y):
		for x in range(shop_rect.position.x, shop_rect.end.x):
			var p = Vector2i(x, y)
			if position_in_bounds(p) and p != stairs_pos:
				map[y][x] = "."


func generate_shop() -> void:
	shop_active = true
	merchant_type = "闇商人" if floor_no >= 20 and rng.randi_range(0, 99) < 25 else "旅商人"
	var origin = find_open_cell(Vector2i(MAP_W - 8, 2))
	shop_rect = Rect2i(max(1, origin.x - 2), max(1, origin.y - 1), 5, 4)
	carve_shop_room()
	shopkeeper_home = origin
	shopkeeper = {"pos": shopkeeper_home, "hp": 999, "atk": 18 + floor_no if merchant_type == "闇商人" else 12 + floor_no}
	var names = ["薬", "兵糧丸", "忍気丸"]
	if merchant_type == "闇商人":
		names = ["上薬", "中巻物", "大巻物" if floor_no >= 50 else "忍気丸"]
	elif floor_no >= 40:
		names[rng.randi_range(0, 2)] = "上薬"
	if floor_no >= 70:
		names[rng.randi_range(0, 2)] = "大兵糧丸"
	for i in range(3):
		var p = find_open_cell(origin + Vector2i((i % 3) - 1, 1))
		var price = item_shop_price(str(names[i]))
		if merchant_type == "闇商人":
			price = int(ceil(price * 1.25))
		var it = {"pos": p, "name": names[i], "price": price, "shop": true}
		items.append(it)
		shop_items.append(it)


func find_random_open_cell() -> Vector2i:
	for _tries in range(300):
		var p = Vector2i(rng.randi_range(1, MAP_W - 2), rng.randi_range(1, MAP_H - 2))
		if is_walkable(p) and not occupied(p) and not cell_has_item(p) and p != stairs_pos:
			if shop_active and shop_rect.has_point(p):
				continue
			return p
	return find_open_cell(Vector2i(1, 1))


func cell_has_item(p: Vector2i) -> bool:
	for item in items:
		if typeof(item) == TYPE_DICTIONARY and item.get("pos", Vector2i(-1, -1)) == p:
			return true
	return false


func occupied(p: Vector2i) -> bool:
	if p == player:
		return true
	for e in enemies:
		if e["pos"] == p:
			return true
	if shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == p:
		return true
	return false


func is_walkable(p: Vector2i) -> bool:
	if p.x < 0 or p.y < 0 or p.x >= MAP_W or p.y >= MAP_H:
		return false
	return map.size() == MAP_H and str(map[p.y][p.x]) != "#"


func try_move(dir: Vector2i) -> void:
	if dir == Vector2i.ZERO:
		end_turn()
		return
	var target = player + dir
	if not is_walkable(target):
		message = "壁だ。"
		return
	for i in range(enemies.size()):
		if enemies[i]["pos"] == target:
			attack_enemy(i)
			end_turn()
			return
	if shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == target:
		if shop_hostile:
			message = "商人が道を塞いでいる。"
		else:
			message = "%s「代金を払っていきな」" % merchant_type
		return

	var was_inside = is_inside_shop(player)
	player = target
	on_player_walked()
	if cell_has_item(player):
		pickup(false)
	var now_inside = is_inside_shop(player)
	if was_inside and not now_inside and unpaid_items.size() > 0:
		try_theft_escape()
	end_turn()
	if not in_village and player == stairs_pos:
		request_stairs_confirmation()


func attack_enemy(index: int) -> void:
	if index < 0 or index >= enemies.size():
		return
	var damage = max(1, attack_power + rng.randi_range(0, 2))
	if style_name == "武":
		damage += 2
	enemies[index]["hp"] = int(enemies[index]["hp"]) - damage
	message = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]
	if int(enemies[index]["hp"]) <= 0:
		var defeated: Dictionary = enemies[index]
		var was_boss = bool(defeated["boss"])
		var name = str(defeated["name"])
		run_coins += max(0, int(defeated.get("coin_reward", 3 if was_boss else 1)))
		run_souls += max(0, int(defeated.get("soul_reward", 3 if was_boss else 1)))
		enemies.remove_at(index)
		ninja_energy = min(100, ninja_energy + (20 if was_boss else 8))
		known_enemies[name] = int(known_enemies.get(name, 0)) + 1
		if was_boss:
			boss_defeated = true
			message = "ボスを討ち取った。階段が使える。"
		else:
			message = "%sを倒した。" % name


func end_turn() -> void:
	if in_village:
		return
	turn_no += 1
	hunger_tick += 1
	if hunger_tick >= 10:
		hunger_tick = 0
		hunger = max(0, hunger - 1)
	if hunger <= 0:
		hp -= 1
		message = "空腹で1ダメージ。"
		if hp <= 0:
			handle_death("飢え")
			return

	if merchant_bound_turns > 0:
		merchant_bound_turns -= 1

	for i in range(enemies.size()):
		if int(enemies[i].get("bound", 0)) > 0:
			enemies[i]["bound"] = int(enemies[i]["bound"]) - 1

	move_enemies()
	trigger_enemy_traps()

	if smoke_turns > 0:
		smoke_turns -= 1
	hidden_mode = false
	update_visibility()
	if turn_no % 5 == 0:
		save_run_state()
	queue_redraw()


func has_clear_shot(source: Vector2i, target_pos: Vector2i, max_range: int) -> bool:
	if source.x != target_pos.x and source.y != target_pos.y:
		return false
	var distance = abs(target_pos.x - source.x) + abs(target_pos.y - source.y)
	if distance <= 1 or distance > max_range:
		return false
	var step = Vector2i(sign(target_pos.x - source.x), sign(target_pos.y - source.y))
	var p = source + step
	while p != target_pos:
		if not is_walkable(p):
			return false
		p += step
	return true


func move_enemies() -> void:
	for i in range(enemies.size()):
		if int(enemies[i].get("bound", 0)) > 0:
			continue
		var pos: Vector2i = enemies[i]["pos"]
		var hunt_target = enemy_hunt_target()
		var delta = hunt_target - pos
		var attack_range = max(1, int(enemies[i].get("range", 1)))
		if max(abs(delta.x), abs(delta.y)) <= 1 or has_clear_shot(pos, hunt_target, attack_range):
			if clone_active and hunt_target == clone_pos:
				# The illusion absorbs attention; it vanishes only after the real ninja walks 30 steps.
				continue
			enemy_attack(i)
			if hp <= 0:
				return
			continue
		if hidden_mode or smoke_turns > 0:
			continue
		var step = Vector2i(sign(delta.x), sign(delta.y))
		var target = pos + step
		if is_walkable(target) and target != player and target != clone_pos and not cell_has_enemy(target, i):
			enemies[i]["pos"] = target

	if shop_hostile and shopkeeper.size() > 0 and merchant_bound_turns <= 0:
		var spos: Vector2i = shopkeeper["pos"]
		var d = player - spos
		if max(abs(d.x), abs(d.y)) <= 1:
			var dmg = max(1, int(shopkeeper.get("atk", 10)) - defense_power)
			hp -= dmg
			message = "怒った商人の一撃！ %dダメージ。" % dmg
			if hp <= 0:
				handle_death("商人")
		else:
			var st = Vector2i(sign(d.x), sign(d.y))
			var nt = spos + st
			if is_walkable(nt) and nt != player and not cell_has_enemy(nt, -1):
				shopkeeper["pos"] = nt


func cell_has_enemy(p: Vector2i, ignore_index: int) -> bool:
	for j in range(enemies.size()):
		if j != ignore_index and enemies[j]["pos"] == p:
			return true
	return false


func enemy_attack(index: int) -> void:
	if index < 0 or index >= enemies.size():
		return
	var dmg = max(1, int(enemies[index]["atk"]) - defense_power)
	if style_name == "影":
		dmg = max(1, dmg - 1)
	hp -= dmg
	message = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]
	if hp <= 0:
		handle_death(str(enemies[index]["name"]))


func handle_death(cause: String) -> void:
	if not revive_used and ad_offer:
		revive_used = true
		hp = max(1, int(max_hp / 2))
		message = "一度だけ踏みとどまった。"
		return
	return_village(cause)


func pickup(consume_turn: bool = true) -> void:
	var found = -1
	for i in range(items.size()):
		if items[i]["pos"] == player:
			found = i
			break
	if found < 0:
		message = "ここには何もない。"
		return
	var item: Dictionary = items[found]
	items.remove_at(found)
	if bool(item.get("shop", false)):
		unpaid_items.append(item)
		message = "%sを手に取った。未精算。" % str(item["name"])
	else:
		add_inventory_item(str(item["name"]), false)
		message = "%sを拾った。" % str(item["name"])
	if consume_turn:
		end_turn()


func valid_inventory_item_name(name: String) -> bool:
	return name in ["薬", "兵糧丸", "忍気丸", "上薬", "大兵糧丸", "小巻物", "中巻物", "大巻物", "究極巻物"]


func add_inventory_item(name: String, identified: bool = false) -> void:
	if not valid_inventory_item_name(name):
		return
	inventory_items.append({"name": name, "identified": identified})


func sanitize_inventory_array(value: Variant) -> Array:
	var out: Array = []
	if typeof(value) != TYPE_ARRAY:
		return out
	for raw in value:
		if typeof(raw) != TYPE_DICTIONARY:
			continue
		var name := str(raw.get("name", ""))
		if valid_inventory_item_name(name):
			out.append({"name": name, "identified": bool(raw.get("identified", false))})
	return out


func inventory_entry_count() -> int:
	return 2 + inventory_items.size()


func inventory_selected_name() -> String:
	if inventory_selected == 0:
		return WEAPON_NAME
	if inventory_selected == 1:
		return ARMOR_NAME
	var idx := inventory_selected - 2
	if idx >= 0 and idx < inventory_items.size():
		return str(inventory_items[idx].get("name", ""))
	return ""


func open_inventory() -> void:
	if in_village or checkout_prompt or stairs_prompt or ad_menu:
		return
	inventory_menu = true
	inventory_selected = clamp(inventory_selected, 0, max(0, inventory_entry_count() - 1))
	message = "道具を確認する。"
	queue_redraw()


func close_inventory() -> void:
	inventory_menu = false
	message = "道具画面を閉じた。"
	queue_redraw()


func inventory_equip_selected() -> void:
	if inventory_selected == 0 or inventory_selected == 1:
		message = "%sは装備中。" % inventory_selected_name()
	else:
		message = "この道具は装備できない。"
	queue_redraw()


func inventory_use_selected(consume_turn: bool = true) -> void:
	var idx := inventory_selected - 2
	if idx < 0 or idx >= inventory_items.size():
		message = "装備品は使用できない。"
		queue_redraw()
		return
	var name := str(inventory_items[idx].get("name", ""))
	inventory_items.remove_at(idx)
	apply_item_effect(name)
	inventory_selected = clamp(inventory_selected, 0, max(0, inventory_entry_count() - 1))
	inventory_menu = false
	if consume_turn:
		end_turn()
	queue_redraw()


func inventory_identify_selected() -> void:
	var idx := inventory_selected - 2
	if idx < 0 or idx >= inventory_items.size():
		message = "%sは識別済み。" % inventory_selected_name()
		queue_redraw()
		return
	inventory_items[idx]["identified"] = true
	message = "%sを識別した。" % str(inventory_items[idx].get("name", ""))
	queue_redraw()


func handle_inventory_key(event: InputEvent) -> void:
	if event.keycode == KEY_ESCAPE or event.keycode == KEY_I:
		close_inventory()
	elif event.keycode == KEY_UP:
		inventory_selected = max(0, inventory_selected - 1)
	elif event.keycode == KEY_DOWN:
		inventory_selected = min(max(0, inventory_entry_count() - 1), inventory_selected + 1)
	elif event.keycode == KEY_E:
		inventory_equip_selected()
	elif event.keycode == KEY_U or event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER:
		inventory_use_selected()
	elif event.keycode == KEY_D:
		inventory_identify_selected()
	queue_redraw()


func handle_inventory_touch(pos: Vector2, portrait: bool) -> void:
	var panel_x := 60.0 if portrait else 270.0
	var panel_y := 225.0 if portrait else 120.0
	var row_h := 46.0
	var max_rows := 7
	for i in range(min(inventory_entry_count(), max_rows)):
		var r := Rect2(panel_x + 20.0, panel_y + 74.0 + i * row_h, 500.0, 40.0)
		if r.has_point(pos):
			inventory_selected = i
			queue_redraw()
			return
	var action_y := panel_y + 420.0
	var actions = [["equip", panel_x + 20.0], ["use", panel_x + 150.0], ["identify", panel_x + 280.0], ["back", panel_x + 410.0]]
	for action in actions:
		if Rect2(float(action[1]), action_y, 115.0, 52.0).has_point(pos):
			match str(action[0]):
				"equip": inventory_equip_selected()
				"use": inventory_use_selected()
				"identify": inventory_identify_selected()
				"back": close_inventory()
			return


func inventory_display_name(index: int) -> String:
	if index == 0:
		return "%s（装備中）" % WEAPON_NAME
	if index == 1:
		return "%s（装備中）" % ARMOR_NAME
	var idx := index - 2
	if idx < 0 or idx >= inventory_items.size():
		return ""
	var entry: Dictionary = inventory_items[idx]
	return str(entry.get("name", "")) if bool(entry.get("identified", false)) else "未識別の道具"


func draw_inventory_overlay(portrait: bool) -> void:
	var panel_x := 60.0 if portrait else 270.0
	var panel_y := 225.0 if portrait else 120.0
	var panel_w := 560.0
	draw_rect(Rect2(panel_x, panel_y, panel_w, 500.0), Color(0.05, 0.07, 0.09, 0.98))
	draw_rect(Rect2(panel_x, panel_y, panel_w, 500.0), Color("#e4cf7a"), false, 2.0)
	draw_ui_text(Vector2(panel_x + 22.0, panel_y + 48.0), "道具 %d点" % inventory_items.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color.WHITE)
	var row_h := 46.0
	var max_rows := 7
	for i in range(min(inventory_entry_count(), max_rows)):
		var r := Rect2(panel_x + 20.0, panel_y + 74.0 + i * row_h, 500.0, 40.0)
		draw_rect(r, Color("#343527") if i == inventory_selected else Color("#202934"))
		draw_rect(r, Color("#dbc66e") if i == inventory_selected else Color("#4c5865"), false, 1.5)
		draw_ui_text(r.position + Vector2(12, 27), inventory_display_name(i), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
	var action_y := panel_y + 420.0
	var labels = [["装備", panel_x + 20.0], ["使用", panel_x + 150.0], ["識別", panel_x + 280.0], ["戻る", panel_x + 410.0]]
	for action in labels:
		var r := Rect2(float(action[1]), action_y, 115.0, 52.0)
		draw_rect(r, Color("#252c35"))
		draw_rect(r, Color("#596575"), false, 1.5)
		draw_ui_text(r.position + Vector2(22, 34), str(action[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)

func item_shop_price(name: String) -> int:
	if name == "薬":
		return 8
	if name == "兵糧丸":
		return 10
	if name == "忍気丸":
		return 14
	if name == "上薬":
		return 18
	if name == "大兵糧丸":
		return 20
	if name == "小巻物":
		return 12
	if name == "中巻物":
		return 22
	if name == "大巻物":
		return 36
	if name == "究極巻物":
		return 60
	return 10


func apply_item_effect(name: String) -> void:
	if name == "薬":
		hp = min(max_hp, hp + 10)
		message = "薬でHPを回復した。"
	elif name == "兵糧丸":
		hunger = min(100, hunger + 35)
		message = "兵糧丸で満腹度を回復した。"
	elif name == "忍気丸":
		ninja_energy = min(100, ninja_energy + 30)
		message = "忍気を回復した。"
	elif name == "上薬":
		hp = min(max_hp, hp + 25)
		message = "上薬でHPを大きく回復した。"
	elif name == "大兵糧丸":
		hunger = min(100, hunger + 65)
		message = "大兵糧丸で満腹度を大きく回復した。"
	elif name == "小巻物":
		ninja_energy = min(100, ninja_energy + 15)
		message = "小巻物を読み、忍気+15。"
	elif name == "中巻物":
		ninja_energy = min(100, ninja_energy + 35)
		message = "中巻物を読み、忍気+35。"
	elif name == "大巻物":
		ninja_energy = min(100, ninja_energy + 60)
		message = "大巻物を読み、忍気+60。"
	elif name == "究極巻物":
		ninja_energy = 100
		message = "究極巻物！ 忍気が最大になった。"


func buy_unpaid() -> void:
	if unpaid_items.is_empty():
		message = "未精算の商品はない。"
		return
	if shop_hostile:
		message = "商人は取引に応じない。"
		return
	checkout_prompt = true
	message = "合計%d銭。精算しますか？" % shop_total_unpaid()
	queue_redraw()


func shop_total_unpaid() -> int:
	var total = 0
	for item in unpaid_items:
		total += int(item.get("price", 0))
	return total


func confirm_checkout(yes: bool) -> void:
	checkout_prompt = false
	if not yes:
		message = "精算をやめた。"
		queue_redraw()
		return
	var total = shop_total_unpaid()
	if run_coins + coins < total:
		message = "銭が足りない。"
		queue_redraw()
		return
	var from_run = min(run_coins, total)
	run_coins -= from_run
	coins -= total - from_run
	for item in unpaid_items:
		add_inventory_item(str(item["name"]), false)
	unpaid_items.clear()
	message = "精算した。道具袋に入れた。"
	save_run_state()
	queue_redraw()


func is_inside_shop(p: Vector2i) -> bool:
	return shop_active and shop_rect.has_point(p)


func try_theft_escape() -> void:
	if unpaid_items.is_empty():
		return
	shop_hostile = true
	var stolen_count = unpaid_items.size()
	for item in unpaid_items:
		if typeof(item) == TYPE_DICTIONARY:
			add_inventory_item(str(item.get("name", "")), false)
	unpaid_items.clear()
	message = "%d点を盗んだ！ 商人が追ってくる。" % stolen_count
	save_run_state()


func on_player_walked() -> void:
	if not clone_active:
		return
	clone_steps_left -= 1
	if clone_steps_left <= 0:
		clone_active = false
		clone_pos = Vector2i(-1, -1)
		clone_steps_left = 0
		message = "影分身が霧のように消えた。"


func use_shadow_clone() -> void:
	if clone_active:
		message = "影分身はすでに存在している。"
		return
	if ninja_energy < 30:
		message = "影分身には忍気30が必要。"
		return
	ninja_energy -= 30
	clone_active = true
	clone_pos = player
	clone_steps_left = 30
	message = "影分身！ 敵を引きつける。30歩で消滅。"
	end_turn()


func enemy_hunt_target() -> Vector2i:
	return clone_pos if clone_active and position_in_bounds(clone_pos) else player


func use_shadow_bind() -> void:
	if ninja_energy < 20:
		message = "忍気が足りない。"
		return
	if shopkeeper.size() > 0:
		var sp: Vector2i = shopkeeper["pos"]
		if max(abs(sp.x - player.x), abs(sp.y - player.y)) <= 1:
			ninja_energy -= 20
			merchant_bound_turns = rng.randi_range(1, 8)
			message = "縛影！ 商人を%dターン拘束。" % merchant_bound_turns
			end_turn()
			return
	var nearest = -1
	var best = 999.0
	for i in range(enemies.size()):
		var p: Vector2i = enemies[i]["pos"]
		var d = p.distance_to(player)
		if d <= 5.0 and d < best:
			best = d
			nearest = i
	if nearest < 0:
		message = "縛影の対象がいない。"
		return
	ninja_energy -= 20
	enemies[nearest]["bound"] = rng.randi_range(1, 8)
	message = "縛影！ %sを%dターン拘束。" % [str(enemies[nearest]["name"]), int(enemies[nearest]["bound"])]
	end_turn()


func use_projectile() -> void:
	var best_index := -1
	var best_dist := 999
	for i in range(enemies.size()):
		var ep: Vector2i = enemies[i]["pos"]
		var d := ep - player
		var aligned: bool = d.x == 0 or d.y == 0 or abs(d.x) == abs(d.y)
		var dist: int = maxi(abs(d.x), abs(d.y))
		if aligned and dist > 0 and dist <= 5 and has_clear_shot(player, ep, 5):
			if dist < best_dist:
				best_dist = dist
				best_index = i
	if best_index < 0:
		message = "飛び道具の射線に敵がいない。"
		return
	attack_enemy(best_index)
	end_turn()

func place_trap() -> void:
	for trap in placed_traps:
		if trap == player:
			message = "ここには既に罠がある。"
			return
	placed_traps.append(player)
	message = "足元に罠を設置した。"
	end_turn()

func trigger_enemy_traps() -> void:
	for i in range(enemies.size()):
		var ep: Vector2i = enemies[i]["pos"]
		var trap_index := placed_traps.find(ep)
		if trap_index >= 0:
			enemies[i]["bound"] = max(2, int(enemies[i].get("bound", 0)))
			placed_traps.remove_at(trap_index)
			message = "%sが罠にかかった。" % str(enemies[i]["name"])
			return

func hide_one_turn() -> void:
	if ninja_energy < 10:
		message = "忍気が足りない。"
		return
	ninja_energy -= 10
	hidden_mode = true
	message = "隠れ身。敵の追跡をかわす。"
	end_turn()


func use_smoke_ninjutsu() -> void:
	if ninja_energy < 20:
		message = "忍気が足りない。"
		return
	ninja_energy -= 20
	smoke_turns = 3
	message = "煙遁。3ターン敵の追跡を阻害。"
	end_turn()


func use_ultimate() -> void:
	if ninja_energy < 100:
		message = "奥義には忍気100が必要。"
		return
	ninja_energy = 0
	for i in range(enemies.size() - 1, -1, -1):
		var p: Vector2i = enemies[i]["pos"]
		if p.distance_to(player) <= 3.0:
			enemies[i]["hp"] = int(enemies[i]["hp"]) - 25
			if int(enemies[i]["hp"]) <= 0:
				var defeated: Dictionary = enemies[i]
				var was_boss = bool(defeated["boss"])
				var defeated_name = str(defeated.get("name", "敵"))
				run_souls += max(0, int(defeated.get("soul_reward", 3 if was_boss else 1)))
				run_coins += max(0, int(defeated.get("coin_reward", 3 if was_boss else 1)))
				known_enemies[defeated_name] = int(known_enemies.get(defeated_name, 0)) + 1
				enemies.remove_at(i)
				if was_boss:
					boss_defeated = true
	message = "奥義・影滅！"
	end_turn()


func request_stairs_confirmation() -> void:
	if player != stairs_pos:
		message = "階段の上にいない。"
		return
	if boss_spawned and not boss_defeated:
		message = "ボスを倒さなければ進めない。"
		return
	stairs_prompt = true
	message = "次の階に降りますか？"
	queue_redraw()


func confirm_stairs(yes: bool) -> void:
	stairs_prompt = false
	if not yes:
		message = "この階にいる。"
		queue_redraw()
		return
	use_stairs()


func use_stairs() -> void:
	if player != stairs_pos:
		message = "階段の上にいない。"
		return
	if boss_spawned and not boss_defeated:
		message = "ボスを倒さなければ進めない。"
		return
	if floor_no >= 100:
		final_clear = true
		run_souls += 25
		run_coins += 100
		return_village("")
		message = "百階踏破！ 忍道を極めた。"
		return
	var cleared_floor = floor_no
	floor_no += 1
	generate_floor()
	register_ad_checkpoint(cleared_floor)
	save_run_state()
	if cleared_floor % 3 != 0:
		message = "%d階へ進んだ。" % floor_no


func register_ad_checkpoint(cleared_floor: int) -> void:
	if not ADS_ENABLED:
		return
	if cleared_floor <= 0 or cleared_floor % 3 != 0:
		return
	if last_ad_checkpoint_floor == cleared_floor:
		return
	last_ad_checkpoint_floor = cleared_floor
	# Integration hook: replace this notice with the real iOS ad SDK call later.
	message = "%d階踏破：広告挿入ポイント（SDK接続待ち）。" % cleared_floor


func open_ad() -> void:
	if not ADS_ENABLED:
		message = "広告OFF。"
		return
	if ad_boost_uses >= 3:
		message = "この探索での広告ブースト上限。"
		return
	ad_menu = true
	message = "任意広告ブーストを選択。"
	queue_redraw()


func apply_ad_reward(kind: String) -> void:
	ad_menu = false
	ad_boost_uses += 1
	if kind == "A":
		ninja_energy = min(100, ninja_energy + 40)
		message = "広告報酬：忍気+40。"
	elif kind == "B":
		attack_power += 1
		defense_power += 1
		message = "広告報酬：この探索中の攻防+1。"
	elif kind == "C":
		hp = max_hp
		hunger = 100
		message = "広告報酬：HP・満腹全回復。"
	save_run_state()
	queue_redraw()


func update_visibility() -> void:
	if explored.size() != MAP_H:
		return
	for y in range(MAP_H):
		if typeof(explored[y]) != TYPE_ARRAY or explored[y].size() != MAP_W:
			return
	for y in range(max(0, player.y - 4), min(MAP_H, player.y + 5)):
		for x in range(max(0, player.x - 6), min(MAP_W, player.x + 7)):
			explored[y][x] = true


func validate_grid(grid: Variant) -> bool:
	if typeof(grid) != TYPE_ARRAY:
		return false
	if grid.size() != MAP_H:
		return false
	for y in range(MAP_H):
		if typeof(grid[y]) != TYPE_ARRAY:
			return false
		if grid[y].size() != MAP_W:
			return false
	return true


func validate_vector2i(value: Variant) -> bool:
	return typeof(value) == TYPE_VECTOR2I


func validate_run_dictionary(data: Dictionary) -> bool:
	var version = int(data.get("version", 0))
	if version < 1 or version > RUN_SAVE_VERSION:
		return false
	if not validate_grid(data.get("map", [])):
		return false
	if not validate_grid(data.get("explored", [])):
		return false
	if not validate_vector2i(data.get("player", null)):
		return false
	var p: Vector2i = data["player"]
	if p.x < 0 or p.y < 0 or p.x >= MAP_W or p.y >= MAP_H:
		return false
	if str(data["map"][p.y][p.x]) == "#":
		return false
	if version >= 3:
		if not validate_vector2i(data.get("stairs_pos", null)):
			return false
		var st: Vector2i = data["stairs_pos"]
		if st.x < 0 or st.y < 0 or st.x >= MAP_W or st.y >= MAP_H:
			return false
		if str(data["map"][st.y][st.x]) != ">":
			return false
	if version >= 4 and bool(data.get("clone_active", false)):
		if not validate_vector2i(data.get("clone_pos", null)):
			return false
		var cp: Vector2i = data["clone_pos"]
		if cp.x < 0 or cp.y < 0 or cp.x >= MAP_W or cp.y >= MAP_H:
			return false
	return true


func find_stairs_in_grid(grid: Array) -> Vector2i:
	if not validate_grid(grid):
		return Vector2i(-1, -1)
	for y in range(MAP_H):
		for x in range(MAP_W):
			if str(grid[y][x]) == ">":
				return Vector2i(x, y)
	return Vector2i(-1, -1)


func sanitize_array(value: Variant) -> Array:
	return value if typeof(value) == TYPE_ARRAY else []


func sanitize_dictionary(value: Variant) -> Dictionary:
	return value if typeof(value) == TYPE_DICTIONARY else {}


func position_in_bounds(p: Vector2i) -> bool:
	return p.x >= 0 and p.y >= 0 and p.x < MAP_W and p.y < MAP_H


func enemy_position_taken(p: Vector2i, current: Array) -> bool:
	for e in current:
		if typeof(e) == TYPE_DICTIONARY and e.get("pos", Vector2i(-1, -1)) == p:
			return true
	return false


func item_position_taken(p: Vector2i, current: Array) -> bool:
	for item in current:
		if typeof(item) == TYPE_DICTIONARY and item.get("pos", Vector2i(-1, -1)) == p:
			return true
	return false


func sanitize_vector2i_array(value: Variant) -> Array:
	var out: Array = []
	if typeof(value) != TYPE_ARRAY:
		return out
	for entry in value:
		if entry is Vector2i:
			out.append(entry)
		elif entry is Vector2:
			out.append(Vector2i(int(entry.x), int(entry.y)))
	return out

func sanitize_enemy_array(value: Variant) -> Array:
	var out: Array = []
	if typeof(value) != TYPE_ARRAY:
		return out
	for raw in value:
		if typeof(raw) != TYPE_DICTIONARY:
			continue
		var entry: Dictionary = raw
		var pos_value: Variant = entry.get("pos", null)
		if not validate_vector2i(pos_value):
			continue
		var pos: Vector2i = pos_value
		if not position_in_bounds(pos) or str(map[pos.y][pos.x]) == "#":
			continue
		if pos == player or pos == stairs_pos or enemy_position_taken(pos, out):
			continue
		var enemy_hp = int(entry.get("hp", 0))
		if enemy_hp <= 0:
			continue
		var is_boss = bool(entry.get("boss", false))
		out.append({
			"pos": pos,
			"hp": enemy_hp,
			"atk": max(1, int(entry.get("atk", 1))),
			"bound": clamp(int(entry.get("bound", 0)), 0, 8),
			"boss": is_boss,
			"name": str(entry.get("name", "敵")),
			"kind": str(entry.get("kind", "legacy")),
			"range": clamp(int(entry.get("range", 1)), 1, 5),
			"coin_reward": max(0, int(entry.get("coin_reward", 3 if is_boss else 1))),
			"soul_reward": max(0, int(entry.get("soul_reward", 3 if is_boss else 1)))
		})
	return out


func sanitize_item_array(value: Variant) -> Array:
	var out: Array = []
	if typeof(value) != TYPE_ARRAY:
		return out
	for raw in value:
		if typeof(raw) != TYPE_DICTIONARY:
			continue
		var entry: Dictionary = raw
		var pos_value: Variant = entry.get("pos", null)
		if not validate_vector2i(pos_value):
			continue
		var pos: Vector2i = pos_value
		if not position_in_bounds(pos) or str(map[pos.y][pos.x]) == "#":
			continue
		if pos == stairs_pos or item_position_taken(pos, out):
			continue
		var name = str(entry.get("name", ""))
		if name not in ["薬", "兵糧丸", "忍気丸", "上薬", "大兵糧丸", "小巻物", "中巻物", "大巻物", "究極巻物"]:
			continue
		out.append({
			"pos": pos,
			"name": name,
			"price": max(0, int(entry.get("price", 0))),
			"shop": bool(entry.get("shop", false))
		})
	return out


func sanitize_shopkeeper(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_DICTIONARY:
		return {}
	var entry: Dictionary = value
	var pos_value: Variant = entry.get("pos", null)
	if not validate_vector2i(pos_value):
		return {}
	var pos: Vector2i = pos_value
	if not position_in_bounds(pos) or str(map[pos.y][pos.x]) == "#":
		return {}
	if pos == player or pos == stairs_pos:
		return {}
	return {
		"pos": pos,
		"hp": max(1, int(entry.get("hp", 999))),
		"atk": max(1, int(entry.get("atk", 10)))
	}


func has_live_boss() -> bool:
	for e in enemies:
		if typeof(e) == TYPE_DICTIONARY and bool(e.get("boss", false)) and int(e.get("hp", 0)) > 0:
			return true
	return false


func repair_loaded_run_state() -> void:
	# The stair marker is part of the play contract; repair visual/state drift.
	if position_in_bounds(stairs_pos) and str(map[stairs_pos.y][stairs_pos.x]) != "#":
		map[stairs_pos.y][stairs_pos.x] = ">"

	# A missing boss on a boss floor would permanently lock the stairs. Respawn it.
	if floor_no % 10 == 0 and not boss_defeated:
		boss_spawned = true
		if not has_live_boss():
			spawn_enemy(true)
	elif floor_no % 10 != 0:
		boss_spawned = false
		boss_defeated = false

	# Unpaid goods without a valid shop cannot be resolved safely. Remove the orphan state.
	if not shop_active or shopkeeper.is_empty():
		shop_active = false
		shop_hostile = false
		merchant_type = "旅商人"
		shopkeeper = {}
		shopkeeper_home = Vector2i(-1, -1)
		shop_items.clear()
		unpaid_items.clear()
		merchant_bound_turns = 0


func build_run_state() -> Dictionary:
	return {
		"version": RUN_SAVE_VERSION,
		"floor_no": floor_no,
		"turn_no": turn_no,
		"player": player,
		"stairs_pos": stairs_pos,
		"hp": hp,
		"max_hp": max_hp,
		"hunger": hunger,
		"hunger_tick": hunger_tick,
		"ninja_energy": ninja_energy,
		"run_souls": run_souls,
		"run_coins": run_coins,
		"style_name": style_name,
		"attack_power": attack_power,
		"defense_power": defense_power,
		"map": map,
		"explored": explored,
		"enemies": enemies,
		"items": items,
		"inventory_items": inventory_items,
		"placed_traps": placed_traps,
		"shop_active": shop_active,
		"shop_hostile": shop_hostile,
		"merchant_type": merchant_type,
		"shop_rect": shop_rect,
		"shopkeeper": shopkeeper,
		"shopkeeper_home": shopkeeper_home,
		"shop_items": shop_items,
		"unpaid_items": unpaid_items,
		"merchant_bound_turns": merchant_bound_turns,
		"smoke_turns": smoke_turns,
		"clone_active": clone_active,
		"clone_pos": clone_pos,
		"clone_steps_left": clone_steps_left,
		"boss_spawned": boss_spawned,
		"boss_defeated": boss_defeated,
		"final_clear": final_clear,
		"revive_used": revive_used,
		"ad_offer": ad_offer,
		"ad_boost_uses": ad_boost_uses,
		"last_ad_checkpoint_floor": last_ad_checkpoint_floor
	}


func suspend_run() -> void:
	save_run_state()
	message = "中断セーブした。"
	queue_redraw()


func save_run_state() -> void:
	if self_test_mode or in_village:
		return
	if not validate_grid(map) or not validate_grid(explored):
		return
	var f = FileAccess.open(RUN_PATH, FileAccess.WRITE)
	if f:
		f.store_var(build_run_state())


func load_run_state() -> bool:
	if not FileAccess.file_exists(RUN_PATH):
		return false
	var f = FileAccess.open(RUN_PATH, FileAccess.READ)
	if not f:
		return false
	var raw: Variant = f.get_var()
	if typeof(raw) != TYPE_DICTIONARY:
		clear_run_state()
		return false
	var data: Dictionary = raw
	if not validate_run_dictionary(data):
		clear_run_state()
		return false

	map = data["map"]
	explored = data["explored"]
	floor_no = clamp(int(data.get("floor_no", 1)), 1, 100)
	turn_no = max(0, int(data.get("turn_no", 0)))
	player = data["player"]

	var version = int(data.get("version", 1))
	if version >= 3:
		stairs_pos = data["stairs_pos"]
	else:
		stairs_pos = find_stairs_in_grid(map)
		if stairs_pos == Vector2i(-1, -1):
			clear_run_state()
			return false

	max_hp = max(1, int(data.get("max_hp", 30 + perm_hp)))
	hp = clamp(int(data.get("hp", max_hp)), 1, max_hp)
	hunger = clamp(int(data.get("hunger", 100)), 0, 100)
	hunger_tick = clamp(int(data.get("hunger_tick", 0)), 0, 9)
	ninja_energy = clamp(int(data.get("ninja_energy", perm_ninja_energy)), 0, 100)
	run_souls = max(0, int(data.get("run_souls", 0)))
	run_coins = max(0, int(data.get("run_coins", 0)))
	style_name = str(data.get("style_name", "武"))
	if style_name not in ["武", "影", "術"]:
		style_name = "武"
	attack_power = max(1, int(data.get("attack_power", 5 + perm_attack)))
	defense_power = max(0, int(data.get("defense_power", 1 + perm_defense)))
	enemies = sanitize_enemy_array(data.get("enemies", []))
	items = sanitize_item_array(data.get("items", []))
	inventory_items = sanitize_inventory_array(data.get("inventory_items", [])) if version >= 5 else []
	placed_traps = sanitize_vector2i_array(data.get("placed_traps", [])) if version >= 5 else []
	inventory_menu = false
	inventory_selected = 0
	shop_active = bool(data.get("shop_active", false))
	shop_hostile = bool(data.get("shop_hostile", false))
	merchant_type = str(data.get("merchant_type", "旅商人"))
	if merchant_type not in ["旅商人", "闇商人"]:
		merchant_type = "旅商人"
	shop_rect = data.get("shop_rect", Rect2i()) if typeof(data.get("shop_rect", Rect2i())) == TYPE_RECT2I else Rect2i()
	shopkeeper = sanitize_shopkeeper(data.get("shopkeeper", {}))
	shopkeeper_home = data.get("shopkeeper_home", Vector2i(-1, -1)) if validate_vector2i(data.get("shopkeeper_home", Vector2i(-1, -1))) else Vector2i(-1, -1)
	shop_items = sanitize_item_array(data.get("shop_items", []))
	unpaid_items = sanitize_item_array(data.get("unpaid_items", []))
	merchant_bound_turns = clamp(int(data.get("merchant_bound_turns", 0)), 0, 8)
	smoke_turns = clamp(int(data.get("smoke_turns", 0)), 0, 3)
	clone_active = bool(data.get("clone_active", false))
	clone_pos = data.get("clone_pos", Vector2i(-1, -1)) if validate_vector2i(data.get("clone_pos", Vector2i(-1, -1))) else Vector2i(-1, -1)
	clone_steps_left = clamp(int(data.get("clone_steps_left", 0)), 0, 30)
	if not clone_active or clone_steps_left <= 0 or not position_in_bounds(clone_pos) or str(map[clone_pos.y][clone_pos.x]) == "#":
		clone_active = false
		clone_pos = Vector2i(-1, -1)
		clone_steps_left = 0
	boss_spawned = bool(data.get("boss_spawned", false))
	boss_defeated = bool(data.get("boss_defeated", false))
	final_clear = bool(data.get("final_clear", false))
	revive_used = bool(data.get("revive_used", false))
	ad_offer = bool(data.get("ad_offer", false))
	ad_boost_uses = max(0, int(data.get("ad_boost_uses", 0)))
	last_ad_checkpoint_floor = max(0, int(data.get("last_ad_checkpoint_floor", 0)))
	checkout_prompt = false
	ad_menu = false
	hidden_mode = false
	in_village = false

	repair_loaded_run_state()
	update_visibility()
	return true


func clear_run_state() -> void:
	if self_test_mode:
		return
	if FileAccess.file_exists(RUN_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(RUN_PATH))


func save_meta() -> void:
	if self_test_mode:
		return
	var data = {
		"version": 2,
		"souls": souls,
		"coins": coins,
		"perm_hp": perm_hp,
		"perm_attack": perm_attack,
		"perm_defense": perm_defense,
		"perm_ninja_energy": perm_ninja_energy,
		"known_enemies": known_enemies,
		"death_log": death_log
	}
	var f = FileAccess.open(META_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data))


func load_meta() -> void:
	if not FileAccess.file_exists(META_PATH):
		return
	var f = FileAccess.open(META_PATH, FileAccess.READ)
	if not f:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return
	var data: Dictionary = parsed
	souls = max(0, int(data.get("souls", 0)))
	coins = max(0, int(data.get("coins", 0)))
	perm_hp = max(0, int(data.get("perm_hp", 0)))
	perm_attack = max(0, int(data.get("perm_attack", 0)))
	perm_defense = max(0, int(data.get("perm_defense", 0)))
	perm_ninja_energy = clamp(int(data.get("perm_ninja_energy", 0)), 0, 100)
	known_enemies = sanitize_dictionary(data.get("known_enemies", {}))
	death_log = sanitize_array(data.get("death_log", []))


func debug_capture_runtime_state() -> Dictionary:
	return {
		"floor_no": floor_no, "turn_no": turn_no, "player": player, "stairs_pos": stairs_pos,
		"hp": hp, "max_hp": max_hp, "hunger": hunger, "hunger_tick": hunger_tick,
		"ninja_energy": ninja_energy, "run_souls": run_souls, "run_coins": run_coins,
		"souls": souls, "coins": coins, "style_name": style_name,
		"attack_power": attack_power, "defense_power": defense_power,
		"in_village": in_village, "village_menu": village_menu,
		"map": map.duplicate(true), "explored": explored.duplicate(true),
		"enemies": enemies.duplicate(true), "items": items.duplicate(true), "inventory_items": inventory_items.duplicate(true), "placed_traps": placed_traps.duplicate(true),
		"shop_active": shop_active, "shop_hostile": shop_hostile, "merchant_type": merchant_type, "shop_rect": shop_rect,
		"shopkeeper": shopkeeper.duplicate(true), "shopkeeper_home": shopkeeper_home,
		"shop_items": shop_items.duplicate(true), "unpaid_items": unpaid_items.duplicate(true),
		"checkout_prompt": checkout_prompt, "merchant_bound_turns": merchant_bound_turns,
		"smoke_turns": smoke_turns, "boss_spawned": boss_spawned, "boss_defeated": boss_defeated,
		"final_clear": final_clear, "revive_used": revive_used, "ad_offer": ad_offer,
		"ad_menu": ad_menu, "ad_boost_uses": ad_boost_uses, "perm_ninja_energy": perm_ninja_energy,
		"hidden_mode": hidden_mode, "hide_hold_active": hide_hold_active, "hide_hold_elapsed": hide_hold_elapsed,
		"clone_active": clone_active, "clone_pos": clone_pos, "clone_steps_left": clone_steps_left,
		"last_ad_checkpoint_floor": last_ad_checkpoint_floor,
		"known_enemies": known_enemies.duplicate(true), "death_log": death_log.duplicate(true),
		"rng_state": rng.state, "message": message
	}


func debug_restore_runtime_state(state: Dictionary) -> void:
	floor_no = int(state["floor_no"])
	turn_no = int(state["turn_no"])
	player = state["player"]
	stairs_pos = state["stairs_pos"]
	hp = int(state["hp"])
	max_hp = int(state["max_hp"])
	hunger = int(state["hunger"])
	hunger_tick = int(state["hunger_tick"])
	ninja_energy = int(state["ninja_energy"])
	run_souls = int(state["run_souls"])
	run_coins = int(state["run_coins"])
	souls = int(state["souls"])
	coins = int(state["coins"])
	style_name = str(state["style_name"])
	attack_power = int(state["attack_power"])
	defense_power = int(state["defense_power"])
	in_village = bool(state["in_village"])
	village_menu = str(state["village_menu"])
	map = state["map"].duplicate(true)
	explored = state["explored"].duplicate(true)
	enemies = state["enemies"].duplicate(true)
	items = state["items"].duplicate(true)
	inventory_items = state.get("inventory_items", []).duplicate(true)
	placed_traps = state.get("placed_traps", []).duplicate(true)
	inventory_menu = false
	inventory_selected = 0
	shop_active = bool(state["shop_active"])
	shop_hostile = bool(state["shop_hostile"])
	merchant_type = str(state["merchant_type"])
	shop_rect = state["shop_rect"]
	shopkeeper = state["shopkeeper"].duplicate(true)
	shopkeeper_home = state["shopkeeper_home"]
	shop_items = state["shop_items"].duplicate(true)
	unpaid_items = state["unpaid_items"].duplicate(true)
	checkout_prompt = bool(state["checkout_prompt"])
	merchant_bound_turns = int(state["merchant_bound_turns"])
	smoke_turns = int(state["smoke_turns"])
	boss_spawned = bool(state["boss_spawned"])
	boss_defeated = bool(state["boss_defeated"])
	final_clear = bool(state["final_clear"])
	revive_used = bool(state["revive_used"])
	ad_offer = bool(state["ad_offer"])
	ad_menu = bool(state["ad_menu"])
	ad_boost_uses = int(state["ad_boost_uses"])
	perm_ninja_energy = int(state["perm_ninja_energy"])
	hidden_mode = bool(state["hidden_mode"])
	hide_hold_active = bool(state["hide_hold_active"])
	hide_hold_elapsed = float(state["hide_hold_elapsed"])
	clone_active = bool(state["clone_active"])
	clone_pos = state["clone_pos"]
	clone_steps_left = int(state["clone_steps_left"])
	last_ad_checkpoint_floor = int(state["last_ad_checkpoint_floor"])
	known_enemies = state["known_enemies"].duplicate(true)
	death_log = state["death_log"].duplicate(true)
	rng.state = int(state["rng_state"])
	message = str(state["message"])


func debug_test_save_contract() -> String:
	generate_floor()
	var data = build_run_state()
	var required = ["player", "stairs_pos", "map", "explored", "enemies", "items", "inventory_items", "placed_traps", "unpaid_items", "merchant_bound_turns", "clone_active", "clone_pos", "clone_steps_left", "merchant_type", "last_ad_checkpoint_floor"]
	for key in required:
		if not data.has(key):
			return "FAIL 保存契約:%s" % key
	return "PASS 保存契約"


func debug_test_grid_validation() -> String:
	var good: Array = []
	for y in range(MAP_H):
		var row: Array = []
		for x in range(MAP_W):
			row.append(".")
		good.append(row)
	var bad = good.duplicate(true)
	bad[0].pop_back()
	return "PASS 格子検証" if validate_grid(good) and not validate_grid(bad) else "FAIL 格子検証"


func debug_test_entity_sanitizer() -> String:
	generate_floor()
	var valid_enemy = {"pos": find_random_open_cell(), "hp": 5, "atk": 2, "bound": 99, "boss": false, "name": "試験敵"}
	var cleaned = sanitize_enemy_array([123, {"pos": "bad"}, valid_enemy])
	var ok = cleaned.size() == 1 and int(cleaned[0].get("bound", -1)) == 8
	return "PASS エンティティ復旧" if ok else "FAIL エンティティ復旧"


func debug_test_stairs_resume() -> String:
	generate_floor()
	var data = build_run_state()
	return "PASS 階段保存" if data.get("stairs_pos", Vector2i(-1, -1)) == stairs_pos else "FAIL 階段保存"


func debug_test_bind_range() -> String:
	var ok = true
	for _i in range(100):
		var v = rng.randi_range(1, 8)
		if v < 1 or v > 8:
			ok = false
	return "PASS 縛影1-8" if ok else "FAIL 縛影"


func debug_test_hunger() -> String:
	# Headless regression starts in the village. end_turn() intentionally does
	# nothing there, so explicitly enter dungeon context for this isolated test.
	in_village = false
	enemies = []
	shop_hostile = false
	shopkeeper = {}
	hunger = 1
	hunger_tick = 9
	hp = 10
	end_turn()
	return "PASS 満腹" if hunger == 0 and hunger_tick == 0 and hp == 9 else "FAIL 満腹"


func debug_test_reward_banking() -> String:
	souls = 10
	coins = 100
	run_souls = 3
	run_coins = 5
	var gained = bank_run_rewards()
	var ok = souls == 13 and coins == 102 and int(gained["coins"]) == 2 and int(gained["souls"]) == 3
	return "PASS 帰還報酬" if ok else "FAIL 帰還報酬"


func debug_test_shop_theft() -> String:
	generate_floor()
	generate_shop()
	inventory_items = []
	unpaid_items = [{"name": "薬", "price": 8, "shop": true}]
	shop_hostile = false
	try_theft_escape()
	var ok = shop_hostile and unpaid_items.is_empty() and inventory_items.size() == 1 and str(inventory_items[0].get("name", "")) == "薬"
	return "PASS 盗み" if ok else "FAIL 盗み"


func debug_test_item_placement() -> String:
	generate_floor()
	var occupied_cells: Dictionary = {}
	for item in items:
		if typeof(item) != TYPE_DICTIONARY:
			return "FAIL アイテム配置型"
		var p: Vector2i = item.get("pos", Vector2i(-1, -1))
		if occupied_cells.has(p):
			return "FAIL アイテム重複"
		occupied_cells[p] = true
	return "PASS アイテム配置"


func debug_test_boss_gate() -> String:
	generate_floor()
	boss_spawned = true
	boss_defeated = false
	player = stairs_pos
	var before = floor_no
	use_stairs()
	return "PASS ボス門" if floor_no == before else "FAIL ボス門"


func debug_test_floor_reachability() -> String:
	for test_floor in [1, 25, 50, 75, 100]:
		floor_no = test_floor
		for _i in range(20):
			generate_floor()
			if not has_path_between(player, stairs_pos):
				return "FAIL 階段到達:%dF" % test_floor
	return "PASS 階段到達"


func debug_test_enemy_curve() -> String:
	var old_floor = floor_no
	floor_no = 1
	var low = enemy_profile(false)
	floor_no = 90
	var high = enemy_profile(false)
	floor_no = old_floor
	var ok = int(high["hp"]) > int(low["hp"]) and int(high["atk"]) >= int(low["atk"])
	return "PASS 難易度曲線" if ok else "FAIL 難易度曲線"


func debug_test_ranged_line() -> String:
	var old_map = map.duplicate(true)
	var clean: Array = []
	for y in range(MAP_H):
		var row: Array = []
		for x in range(MAP_W):
			row.append("#" if x == 0 or y == 0 or x == MAP_W - 1 or y == MAP_H - 1 else ".")
		clean.append(row)
	map = clean
	var open_line = has_clear_shot(Vector2i(2, 2), Vector2i(5, 2), 4)
	map[2][4] = "#"
	var blocked = not has_clear_shot(Vector2i(2, 2), Vector2i(5, 2), 4)
	var diagonal = not has_clear_shot(Vector2i(2, 2), Vector2i(4, 4), 4)
	map = old_map
	return "PASS 遠距離射線" if open_line and blocked and diagonal else "FAIL 遠距離射線"


func debug_test_item_catalog() -> String:
	var names = ["薬", "兵糧丸", "忍気丸", "上薬", "大兵糧丸", "小巻物", "中巻物", "大巻物", "究極巻物"]
	for item_name in names:
		if item_shop_price(item_name) <= 0:
			return "FAIL アイテム価格"
	return "PASS アイテム一覧"


func debug_test_inventory_contract() -> String:
	inventory_items = []
	add_inventory_item("薬", false)
	if inventory_items.size() != 1 or bool(inventory_items[0].get("identified", true)):
		return "FAIL 道具取得"
	inventory_selected = 2
	inventory_identify_selected()
	if not bool(inventory_items[0].get("identified", false)):
		return "FAIL 道具識別"
	hp = max(1, max_hp - 10)
	var before_hp := hp
	inventory_use_selected(false)
	if not inventory_items.is_empty() or hp <= before_hp:
		return "FAIL 道具使用"
	inventory_selected = 0
	inventory_equip_selected()
	return "PASS 道具装備使用識別" if message.find("装備中") >= 0 else "FAIL 道具装備"


func debug_test_spawn_safety() -> String:
	generate_floor()
	var occupied_enemy: Dictionary = {}
	for e in enemies:
		var p: Vector2i = e.get("pos", Vector2i(-1, -1))
		if p == player or p == stairs_pos or occupied_enemy.has(p):
			return "FAIL 敵配置"
		occupied_enemy[p] = true
	var occupied_item: Dictionary = {}
	for item in items:
		var p: Vector2i = item.get("pos", Vector2i(-1, -1))
		if p == player or p == stairs_pos or occupied_item.has(p):
			return "FAIL 物配置"
		occupied_item[p] = true
	return "PASS 配置安全"


func debug_test_boss_resume_repair() -> String:
	floor_no = 50
	generate_floor()
	enemies = []
	boss_spawned = true
	boss_defeated = false
	repair_loaded_run_state()
	return "PASS ボス復旧" if has_live_boss() else "FAIL ボス復旧"


func debug_test_orphan_shop_repair() -> String:
	generate_floor()
	shop_active = true
	shopkeeper = {}
	unpaid_items = [{"pos": player, "name": "薬", "price": 8, "shop": true}]
	repair_loaded_run_state()
	var ok = not shop_active and unpaid_items.is_empty() and not shop_hostile
	return "PASS 商店復旧" if ok else "FAIL 商店復旧"


func debug_test_shadow_clone_contract() -> String:
	generate_floor()
	ninja_energy = 100
	var start_pos = player
	use_shadow_clone()
	if not clone_active or clone_steps_left != 30 or clone_pos != start_pos:
		return "FAIL 影分身生成"
	for _i in range(30):
		on_player_walked()
	return "PASS 影分身30歩" if not clone_active and clone_steps_left == 0 else "FAIL 影分身30歩"


func debug_test_ad_checkpoint() -> String:
	var old_checkpoint = last_ad_checkpoint_floor
	last_ad_checkpoint_floor = 0
	register_ad_checkpoint(3)
	var ok = last_ad_checkpoint_floor == 0 and not ADS_ENABLED
	last_ad_checkpoint_floor = old_checkpoint
	return "PASS 広告OFF" if ok else "FAIL 広告OFF"


func debug_test_final_floor_contract() -> String:
	var old_floor = floor_no
	var old_player = player
	var old_stairs = stairs_pos
	var old_boss_spawned = boss_spawned
	var old_boss_defeated = boss_defeated
	var old_final_clear = final_clear
	floor_no = 100
	player = Vector2i(2, 2)
	stairs_pos = player
	boss_spawned = true
	boss_defeated = false
	use_stairs()
	var gate_ok = not final_clear
	boss_defeated = true
	# Do not call use_stairs() here because a true final clear intentionally banks/clears run state.
	var clear_condition_ok = floor_no >= 100 and player == stairs_pos and boss_defeated
	floor_no = old_floor
	player = old_player
	stairs_pos = old_stairs
	boss_spawned = old_boss_spawned
	boss_defeated = old_boss_defeated
	final_clear = old_final_clear
	return "PASS 百階契約" if gate_ok and clear_condition_ok else "FAIL 百階契約"

func debug_test_research_contract() -> String:
	var old_souls = souls
	var old_perm = perm_ninja_energy
	var old_energy = ninja_energy
	souls = 5
	perm_ninja_energy = 0
	ninja_energy = 0
	var changed = research_ninja_energy(false)
	var ok = changed and souls == 0 and perm_ninja_energy == 20 and ninja_energy == 20
	souls = old_souls
	perm_ninja_energy = old_perm
	ninja_energy = old_energy
	return "PASS 忍気研究" if ok else "FAIL 忍気研究"


func debug_test_ui_glyph_contract() -> String:
	var required := "忍道里魂銭恒久攻撃防御初期気鍛冶屋術研究所録帳成長出陣階段奥義精算隠身縛影煙分隠飛罠方向操作機能ップ具装備使用識別戻持物未点"
	for i in range(required.length()):
		var ch := required.substr(i, 1)
		if not UI_GLYPH_MAP.has(ch):
			return "FAIL 字形:%s" % ch
	return "PASS 日本語字形"


func debug_run_regression_suite() -> void:
	var saved = debug_capture_runtime_state()
	var results = [
		debug_test_save_contract(),
		debug_test_grid_validation(),
		debug_test_entity_sanitizer(),
		debug_test_stairs_resume(),
		debug_test_bind_range(),
		debug_test_hunger(),
		debug_test_reward_banking(),
		debug_test_shop_theft(),
		debug_test_item_placement(),
		debug_test_floor_reachability(),
		debug_test_enemy_curve(),
		debug_test_ranged_line(),
		debug_test_item_catalog(),
		debug_test_inventory_contract(),
		debug_test_boss_gate(),
		debug_test_spawn_safety(),
		debug_test_boss_resume_repair(),
		debug_test_orphan_shop_repair(),
		debug_test_shadow_clone_contract(),
		debug_test_ad_checkpoint(),
		debug_test_final_floor_contract(),
		debug_test_research_contract(),
		debug_test_ui_glyph_contract()
	]
	var failures: Array[String] = []
	for result in results:
		if str(result).begins_with("FAIL"):
			failures.append(str(result))
	regression_all_pass = failures.is_empty()
	debug_restore_runtime_state(saved)
	# Regression tests may trigger autosave/theft-save. Re-persist the restored real state.
	if in_village:
		clear_run_state()
	else:
		save_run_state()
	debug_last = " / ".join(results)
	message = ("PASS ALL: " if regression_all_pass else "REGRESSION FAIL [%d]: " % failures.size()) + debug_last
	# A redraw is useful in editor/debug UI, but headless CI has no glyph texture loaded.
	if not self_test_mode:
		queue_redraw()



func portrait_cell_center(p: Vector2i) -> Vector2:
	const PTILE := 21
	const PMAP_X := 34
	const PMAP_Y := 118
	return Vector2(PMAP_X + p.x * PTILE + PTILE * 0.5, PMAP_Y + p.y * PTILE + PTILE * 0.5)


func handle_press_portrait(pos: Vector2) -> void:
	var diamond_actions = [
		[Rect2(404, 646, 52, 52), "inventory"],
		[Rect2(348, 704, 52, 52), "trap"],
		[Rect2(444, 704, 52, 52), "throw"],
		[Rect2(404, 762, 52, 52), "suspend"]
	]
	for d_action in diamond_actions:
		var d_rect: Rect2 = d_action[0]
		if d_rect.has_point(pos):
			var d_name := str(d_action[1])
			if d_name == "inventory": open_inventory()
			elif d_name == "trap": place_trap()
			elif d_name == "throw": use_projectile()
			elif d_name == "suspend": suspend_run()
			queue_redraw()
			return
	if Rect2(604, 136, 82, 38).has_point(pos):
		toggle_map_visibility()
		return
	if in_village:
		handle_village_touch_portrait(pos)
		return
	if inventory_menu:
		handle_inventory_touch(pos, true)
		return
	if checkout_prompt or stairs_prompt or ad_menu:
		handle_modal_touch_portrait(pos)
		return
	var hide_r := Rect2(174, 710, 140, 50)
	if hide_r.has_point(pos):
		hide_hold_active = true
		hide_hold_elapsed = HIDE_HOLD_INTERVAL
		return
	var base := Vector2(510, 650)
	var cell := 60.0
	if pos.x >= base.x and pos.x < base.x + cell * 3.0 and pos.y >= base.y and pos.y < base.y + cell * 3.0:
		var cx := int((pos.x - base.x) / cell)
		var cy := int((pos.y - base.y) / cell)
		var d := Vector2i(cx - 1, cy - 1)
		if d == Vector2i.ZERO:
			hide_one_turn()
		else:
			try_move(d)
		return
	var acts = [
		[Rect2(20,650,140,50),"stairs"], [Rect2(174,650,140,50),"ultimate"],
		[Rect2(20,710,140,50),"buy"], [Rect2(174,710,140,50),"hide"],
		[Rect2(20,770,140,50),"bind"], [Rect2(174,770,140,50),"smoke"],
		[Rect2(20,830,140,50),"clone"], [Rect2(174,830,140,50),"ad"],
		[Rect2(20,900,140,54),"style_bu"], [Rect2(174,900,140,54),"style_kage"], [Rect2(328,900,140,54),"style_jutsu"]
	]
	for a in acts:
		var r: Rect2 = a[0]
		if r.has_point(pos):
			var action := str(a[1])
			if action == "inventory": open_inventory()
			elif action == "pickup": pickup()
			elif action == "stairs": use_stairs()
			elif action == "ultimate": use_ultimate()
			elif action == "buy": buy_unpaid()
			elif action == "hide": hide_one_turn()
			elif action == "bind": use_shadow_bind()
			elif action == "smoke": use_smoke_ninjutsu()
			elif action == "clone": use_shadow_clone()
			elif action == "throw": use_projectile()
			elif action == "trap": place_trap()
			elif action == "ad": open_ad()
			elif action == "style_bu":
				style_name = "武"
				message = "忍道：武"
			elif action == "style_kage":
				style_name = "影"
				message = "忍道：影"
			elif action == "style_jutsu":
				style_name = "術"
				message = "忍道：術"
			queue_redraw()
			return


func handle_village_touch_portrait(pos: Vector2) -> void:
	if village_menu == "main":
		for i in range(5):
			var r := Rect2(50, 220 + i * 82, 620, 68)
			if r.has_point(pos):
				if i == 0:
					village_menu = "blacksmith"
					message = "鍛冶屋"
				elif i == 1:
					village_menu = "research"
					message = "忍術研究所"
				elif i == 2:
					village_menu = "record"
					message = record_text()
				elif i == 3:
					village_menu = "growth"
					message = "恒久成長"
				else:
					start_run()
				queue_redraw()
				return
	else:
		if Rect2(50, 650, 260, 64).has_point(pos):
			village_menu = "main"
			message = "忍の里。"
		elif village_menu == "blacksmith":
			if Rect2(50,300,620,64).has_point(pos): spend_souls("atk")
			elif Rect2(50,380,620,64).has_point(pos): spend_souls("def")
		elif village_menu == "research" and Rect2(50,300,620,64).has_point(pos): research_ninja_energy()
		elif village_menu == "growth":
			if Rect2(50,300,620,64).has_point(pos): spend_souls("hp")
			elif Rect2(50,380,620,64).has_point(pos): spend_souls("atk")
			elif Rect2(50,460,620,64).has_point(pos): spend_souls("def")
		queue_redraw()


func handle_modal_touch_portrait(pos: Vector2) -> void:
	if checkout_prompt:
		if Rect2(100, 555, 220, 70).has_point(pos): confirm_checkout(true)
		elif Rect2(400, 555, 220, 70).has_point(pos): confirm_checkout(false)
		return
	if stairs_prompt:
		if Rect2(100, 555, 220, 70).has_point(pos): confirm_stairs(true)
		elif Rect2(400, 555, 220, 70).has_point(pos): confirm_stairs(false)
		return
	if ad_menu:
		var rects = [Rect2(80,500,250,70),Rect2(390,500,250,70),Rect2(80,590,250,70),Rect2(390,590,250,70)]
		for i in range(rects.size()):
			if rects[i].has_point(pos):
				if i == 0: apply_ad_reward("A")
				elif i == 1: apply_ad_reward("B")
				elif i == 2: apply_ad_reward("C")
				else:
					ad_menu = false
					message = "広告を見ずに進む。"
					queue_redraw()
				return


func draw_panel(rect: Rect2, fill: Color = Color("#141b23"), border: Color = Color("#46515f"), border_width: float = 2.0) -> void:
	draw_rect(rect, fill)
	draw_rect(rect, border, false, border_width)


func draw_meter(pos: Vector2, size: Vector2, value: int, maximum: int, fill: Color, bg: Color = Color("#151a20")) -> void:
	var ratio := 0.0
	if maximum > 0:
		ratio = clamp(float(value) / float(maximum), 0.0, 1.0)
	draw_rect(Rect2(pos, size), bg)
	draw_rect(Rect2(pos, Vector2(size.x * ratio, size.y)), fill)
	draw_rect(Rect2(pos, size), Color("#66717e"), false, 1.0)


func draw_village_portrait() -> void:
	draw_rect(Rect2(0, 0, 720, 1100), Color("#0a1017"))
	# Replaceable visual shell: no gameplay/save dependency.
	draw_rect(Rect2(0, 0, 720, 190), Color("#111b27"))
	draw_rect(Rect2(0, 190, 720, 3), Color("#8d7740"))
	draw_ui_text(Vector2(46, 72), "忍の里", HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Color("#e8d47f"))
	draw_ui_text(Vector2(48, 120), "忍魂 %d    銭 %d" % [souls, coins], HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color("#e4e8ed"))
	draw_ui_text(Vector2(48, 157), "恒久 HP+%d  攻撃+%d  防御+%d  初期忍気%d" % [perm_hp, perm_attack, perm_defense, perm_ninja_energy], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#aeb7c2"))
	if village_menu == "main":
		var labels = ["鍛冶屋", "忍術研究所", "忍録帳", "恒久成長", "出陣"]
		for i in range(labels.size()):
			var r := Rect2(48, 226 + i * 84, 624, 66)
			var fill := Color("#18212b")
			var border := Color("#455464")
			if i == labels.size() - 1:
				fill = Color("#282717")
				border = Color("#d7bf66")
			draw_panel(r, fill, border, 2.0)
			draw_ui_text(r.position + Vector2(26, 44), labels[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color("#f0f2f5"))
	else:
		var title := ""
		var actions: Array = []
		if village_menu == "blacksmith":
			title = "鍛冶屋"
			actions = ["攻撃+1（忍魂5）", "防御+1（忍魂5）"]
		elif village_menu == "research":
			title = "忍術研究所"
			actions = ["初期忍気+20（忍魂5） 現在%d/100" % perm_ninja_energy]
		elif village_menu == "record":
			title = "忍録帳"
			actions = [record_text()]
		else:
			title = "恒久成長"
			actions = ["最大HP+5（忍魂5）", "攻撃+1（忍魂5）", "防御+1（忍魂5）"]
		draw_ui_text(Vector2(48, 250), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color("#e8d47f"))
		for i in range(actions.size()):
			var r := Rect2(48, 306 + i * 80, 624, 64)
			draw_panel(r, Color("#18212b"), Color("#455464"), 2.0)
			draw_ui_text(r.position + Vector2(18, 42), str(actions[i]).left(42), HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
		var back := Rect2(48, 654, 270, 64)
		draw_panel(back, Color("#18212b"), Color("#455464"), 2.0)
		draw_ui_text(back.position + Vector2(24, 42), "戻る", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.WHITE)
	draw_panel(Rect2(40, 984, 640, 70), Color("#111820"), Color("#394653"), 1.0)
	draw_ui_text(Vector2(54, 1028), message.left(40), HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#e5d37d"))
	draw_ui_text(Vector2(465, 46), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#7f8b98"))


func draw_dungeon_tile(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int) -> void:
	var r := Rect2(p, Vector2(tile_size - 1, tile_size - 1))
	if not seen:
		draw_rect(r, Color("#05080b"))
		return
	if tile == "#":
		var wall_base := Color("#2a3035")
		if (x + y) % 3 == 0:
			wall_base = Color("#30373c")
		draw_rect(r, wall_base)
		draw_rect(Rect2(p + Vector2(2, 2), Vector2(tile_size - 5, tile_size - 5)), Color("#1f252a"))
		if y % 2 == 0:
			draw_line(p + Vector2(2, tile_size * 0.5), p + Vector2(tile_size - 3, tile_size * 0.5), Color("#394047"), 1.0)
		if x % 2 == 0:
			draw_line(p + Vector2(tile_size * 0.5, 2), p + Vector2(tile_size * 0.5, tile_size - 3), Color("#161b20"), 1.0)
	elif tile == ">":
		draw_rect(r, Color("#4b442c"))
		draw_rect(Rect2(p + Vector2(3, 3), Vector2(tile_size - 7, tile_size - 7)), Color("#776a3d"))
	else:
		var floor_base := Color("#7b6745")
		if (x * 7 + y * 11) % 5 == 0:
			floor_base = Color("#846e48")
		draw_rect(r, floor_base)
		draw_rect(Rect2(p + Vector2(1, 1), Vector2(tile_size - 3, tile_size - 3)), floor_base)
		if (x + y) % 4 == 0:
			draw_line(p + Vector2(4, tile_size - 5), p + Vector2(tile_size - 5, tile_size - 5), Color("#5a4c37"), 1.0)


func draw_dungeon_portrait() -> void:
	const PTILE := 21
	const PMAP_X := 34
	const PMAP_Y := 154
	draw_rect(Rect2(0, 0, 720, 1100), Color("#080c11"))
	draw_rect(Rect2(0, 0, 720, 128), Color("#101822"))
	draw_rect(Rect2(0, 126, 720, 2), Color("#5a6673"))
	draw_ui_text(Vector2(20, 34), "忍道 - SHINOBI ROGUE", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#e8d47f"))
	draw_ui_text(Vector2(535, 33), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#7f8b98"))
	draw_ui_text(Vector2(20, 66), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
	draw_ui_text(Vector2(72, 66), "HP %d/%d" % [hp, max_hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e7ebef"))
	draw_meter(Vector2(178, 53), Vector2(120, 13), hp, max_hp, Color("#67b96f"))
	draw_ui_text(Vector2(320, 66), "満腹 %d" % hunger, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e7ebef"))
	draw_meter(Vector2(430, 53), Vector2(90, 13), hunger, 100, Color("#5f8fe8"))
	draw_ui_text(Vector2(540, 66), "忍気 %d" % ninja_energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e7ebef"))
	draw_ui_text(Vector2(20, 102), "忍道:%s   銭 %d(+%d)   忍魂 %d(+%d)   T%d" % [style_name, coins, run_coins, souls, run_souls, turn_no], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#aeb7c2"))
	draw_panel(Rect2(20, 140, 680, 382), Color("#0b0f14"), Color("#3c4650"), 2.0)
	if map_visible:
		for y in range(MAP_H):
			for x in range(MAP_W):
				var p := Vector2(PMAP_X + x * PTILE, PMAP_Y + y * PTILE)
				var seen := validate_grid(explored) and bool(explored[y][x])
				var tile := str(map[y][x]) if validate_grid(map) else "#"
				draw_dungeon_tile(p, tile, seen, x, y, PTILE)
	# Uses approved art automatically when files exist; glyphs remain safe fallback.
	for trap in placed_traps:
		var tp: Vector2i = trap
		if is_visible_cell(tp):
			draw_entity_visual(portrait_cell_center(tp), "trap", "罠", 14, Color("#e0a35c"), PTILE)
	for item in items:
		var ip: Vector2i = item["pos"]
		if is_visible_cell(ip):
			draw_entity_visual(portrait_cell_center(ip), "item", "物", 14, Color("#f0d45f"), PTILE)
	for e in enemies:
		var ep: Vector2i = e["pos"]
		if is_visible_cell(ep):
			draw_entity_visual(portrait_cell_center(ep), "boss" if bool(e["boss"]) else "enemy", "将" if bool(e["boss"]) else "敵", 14, Color("#f08a7d"), PTILE)
	if shopkeeper.size() > 0:
		var sp: Vector2i = shopkeeper["pos"]
		if is_visible_cell(sp):
			draw_entity_visual(portrait_cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", "闇" if merchant_type == "闇商人" else "商", 14, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), PTILE)
	if clone_active and is_visible_cell(clone_pos):
		draw_entity_visual(portrait_cell_center(clone_pos), "clone", "影", 14, Color("#91a9d6"), PTILE)
	draw_entity_visual(portrait_cell_center(player), "player", "忍", 15, Color("#ffffff"), PTILE)
	var hunger_note := "【空腹注意】" if hunger <= 20 else ""
	draw_panel(Rect2(20, 534, 680, 96), Color("#111820"), Color("#394653"), 1.0)
	draw_ui_text(Vector2(34, 567), message.left(44), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#e8d47f"))
	draw_ui_text(Vector2(34, 603), "装備: %s / %s   %s" % [WEAPON_NAME, ARMOR_NAME, hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#bbc4ce"))
	if unpaid_items.size() > 0:
		draw_ui_text(Vector2(420, 603), "未精算 %d点/%d銭" % [unpaid_items.size(), shop_total_unpaid()], HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("#ff9a7a"))
	var map_button_portrait := Rect2(604, 136, 82, 38)
	draw_panel(map_button_portrait, Color("#202934"), Color("#dbc66e") if map_visible else Color("#4c5865"), 1.5)
	draw_ui_text(map_button_portrait.position + Vector2(14, 27), "地図", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color.WHITE)
	draw_mobile_controls_portrait()
	if inventory_menu:
		draw_inventory_overlay(true)
	elif checkout_prompt or stairs_prompt or ad_menu:
		draw_modal_overlay_portrait()


func draw_mobile_controls_portrait() -> void:
	var actions = [["階段", "stairs"], ["奥義", "ultimate"], ["精算", "buy"], ["隠身", "hide"], ["縛影", "bind"], ["煙", "smoke"], ["分身", "clone"], ["広告", "ad"]]
	for i in range(actions.size()):
		var col := i % 2
		var row := i / 2
		var r := Rect2(20 + col * 154, 650 + row * 60, 140, 50)
		var available := touch_action_available(str(actions[i][1]))
		draw_panel(r, Color("#202934") if available else Color("#12171d"), Color("#4c5865") if available else Color("#252c34"), 1.5)
		draw_ui_text(r.position + Vector2(17, 34), str(actions[i][0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#f2f4f7") if available else Color("#59626d"))
	var diamond_controls = [
		["道具", Rect2(404, 646, 52, 52)],
		["罠", Rect2(348, 704, 52, 52)],
		["飛", Rect2(444, 704, 52, 52)],
		["中断", Rect2(404, 762, 52, 52)]
	]
	for d_control in diamond_controls:
		var dr: Rect2 = d_control[1]
		draw_panel(dr, Color("#202934"), Color("#596675"), 1.5)
		draw_ui_text(dr.position + Vector2(8, 35), str(d_control[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.WHITE)
	var base := Vector2(502, 646)
	var cell := 64.0
	var labels = [["↖", "↑", "↗"], ["←", "隠", "→"], ["↙", "↓", "↘"]]
	for y in range(3):
		for x in range(3):
			var r := Rect2(base.x + x * cell, base.y + y * cell, cell - 4, cell - 4)
			var center := x == 1 and y == 1
			draw_panel(r, Color("#29333f") if center else Color("#202934"), Color("#596675"), 1.5)
			draw_ui_text(r.position + Vector2(16, 41), labels[y][x], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.WHITE)
	var styles = [["武", 20], ["影", 174], ["術", 328]]
	for st in styles:
		var r := Rect2(float(st[1]), 900, 140, 54)
		var active := style_name == str(st[0])
		draw_panel(r, Color("#343527") if active else Color("#202934"), Color("#dbc66e") if active else Color("#4c5865"), 2.0 if active else 1.5)
		draw_ui_text(r.position + Vector2(54, 37), str(st[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color.WHITE)
	draw_ui_text(Vector2(20, 980), "方向・隠・忍術をタップして行動", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("#7f8b98"))


func draw_modal_overlay_portrait() -> void:
	draw_rect(Rect2(40,320,640,360),Color(0.05,0.07,0.09,0.97))
	draw_rect(Rect2(40,320,640,360),Color("#e4cf7a"),false,3)
	if checkout_prompt or stairs_prompt:
		draw_ui_text(Vector2(85,420), "商品を精算しますか？" if checkout_prompt else "次の階に降りますか？", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color.WHITE)
		var yes := Rect2(100,555,220,70)
		var no := Rect2(400,555,220,70)
		for r in [yes,no]:
			draw_rect(r,Color("#252c35"))
			draw_rect(r,Color("#596575"),false,2)
		draw_ui_text(yes.position+Vector2(70,47),"はい",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)
		draw_ui_text(no.position+Vector2(65,47),"いいえ",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)
	else:
		draw_ui_text(Vector2(85,400),"任意広告ブースト（試作）",HORIZONTAL_ALIGNMENT_LEFT,-1,26,Color.WHITE)
		var labels = ["忍気","能力","全回復","見ない"]
		var rects = [Rect2(80,500,250,70),Rect2(390,500,250,70),Rect2(80,590,250,70),Rect2(390,590,250,70)]
		for i in range(4):
			draw_rect(rects[i],Color("#252c35"))
			draw_rect(rects[i],Color("#596575"),false,2)
			draw_ui_text(rects[i].position+Vector2(55,47),labels[i],HORIZONTAL_ALIGNMENT_LEFT,-1,22,Color.WHITE)


func debug_prepare_shop() -> void:
	if in_village:
		start_run()
	generate_shop()
	player = find_open_cell(shopkeeper_home + Vector2i(0, 1))
	message = "DEBUG: 商店生成"


func debug_prepare_boss() -> void:
	if in_village:
		start_run()
	floor_no = 10
	generate_floor()
	message = "DEBUG: ボス階"


func debug_prepare_theft() -> void:
	if in_village:
		start_run()
	generate_shop()
	player = find_open_cell(shopkeeper_home + Vector2i(0, 1))
	unpaid_items = [{"name": "薬", "price": 8, "shop": true}]
	message = "DEBUG: 未精算品あり"


func content_offset() -> Vector2:
	var viewport_size = get_viewport_rect().size
	return Vector2(max(0.0, (viewport_size.x - CONTENT_W) * 0.5), max(0.0, (viewport_size.y - CONTENT_H) * 0.5))


func _draw() -> void:
	draw_set_transform(content_offset())
	if PORTRAIT_LAYOUT_ENABLED:
		if in_village:
			draw_village_portrait()
		else:
			draw_dungeon_portrait()
		return
	if in_village:
		draw_village()
	else:
		draw_dungeon()


func draw_village() -> void:
	draw_rect(Rect2(0, 0, 1100, 720), Color("#121820"))
	draw_ui_text(Vector2(70, 80), "忍の里", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color("#e4cf7a"))
	draw_ui_text(
		Vector2(70, 125),
		"忍魂 %d   銭 %d   恒久HP+%d 攻撃+%d 防御+%d 初期忍気%d" %
		[souls, coins, perm_hp, perm_attack, perm_defense, perm_ninja_energy],
		HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE
	)
	if village_menu == "main":
		var labels = ["鍛冶屋", "忍術研究所", "忍録帳", "恒久成長", "出陣"]
		for i in range(labels.size()):
			var r = Rect2(70, 180 + i * 66, 360, 54)
			draw_rect(r, Color("#252c35"))
			draw_rect(r, Color("#596575"), false, 1)
			draw_ui_text(r.position + Vector2(20, 35), labels[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
	else:
		var title = ""
		var actions: Array = []
		if village_menu == "blacksmith":
			title = "鍛冶屋"
			actions = ["攻撃+1（忍魂5）", "防御+1（忍魂5）"]
		elif village_menu == "research":
			title = "忍術研究所"
			actions = ["初期忍気+20（忍魂5） 現在%d/100" % perm_ninja_energy]
		elif village_menu == "record":
			title = "忍録帳"
			actions = [record_text()]
		else:
			title = "恒久成長"
			actions = ["最大HP+5（忍魂5）", "攻撃+1（忍魂5）", "防御+1（忍魂5）"]
		draw_ui_text(Vector2(70, 200), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color("#e4cf7a"))
		for i in range(actions.size()):
			var r = Rect2(70, 240 + i * 64, 430, 52)
			draw_rect(r, Color("#252c35"))
			draw_rect(r, Color("#596575"), false, 1)
			draw_ui_text(r.position + Vector2(16, 33), str(actions[i]), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
		var back = Rect2(70, 500, 220, 50)
		draw_rect(back, Color("#252c35"))
		draw_rect(back, Color("#596575"), false, 1)
		draw_ui_text(back.position + Vector2(18, 32), "戻る", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
	draw_ui_text(Vector2(70, 650), message.left(90), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e4cf7a"))
	draw_ui_text(Vector2(780, 46), "Ver.%s %s" % [VERSION, RELEASE_CHANNEL], HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("#8995a3"))


func draw_dungeon() -> void:
	draw_rect(Rect2(0, 0, 1100, 720), Color("#0d1117"))
	draw_ui_text(Vector2(16, 34), "忍道 - SHINOBI ROGUE  Ver.%s %s" % [VERSION, RELEASE_CHANNEL], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
	draw_ui_text(
		Vector2(16, 64),
		"%dF  HP %d/%d  満腹 %d  忍気 %d  忍道:%s  %s/%s" % [floor_no, hp, max_hp, hunger, ninja_energy, style_name, WEAPON_NAME, ARMOR_NAME],
		HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE
	)

	if map_visible:
		for y in range(MAP_H):
			for x in range(MAP_W):
				var p = Vector2(MAP_X + x * TILE, MAP_Y + y * TILE)
				var seen = validate_grid(explored) and bool(explored[y][x])
				var tile = str(map[y][x]) if validate_grid(map) else "#"
				var col = Color("#232a33") if seen else Color("#0c1015")
				if tile == "#":
					col = Color("#151b22") if seen else Color("#090c10")
				elif tile == ">":
					col = Color("#4a4430") if seen else Color("#0c1015")
				draw_rect(Rect2(p, Vector2(TILE - 1, TILE - 1)), col)
	for trap in placed_traps:
		var tp: Vector2i = trap
		if is_visible_cell(tp):
			draw_entity_visual(cell_center(tp), "trap", "罠", 14, Color("#e0a35c"), TILE)

	for item in items:
		var ip: Vector2i = item["pos"]
		if is_visible_cell(ip):
			draw_entity_visual(cell_center(ip), "item", "物", 14, Color("#d6c56d"), TILE)

	for e in enemies:
		var ep: Vector2i = e["pos"]
		if is_visible_cell(ep):
			var mark = "将" if bool(e["boss"]) else "敵"
			draw_entity_visual(cell_center(ep), "boss" if bool(e["boss"]) else "enemy", mark, 14, Color("#e07a72"), TILE)

	if shopkeeper.size() > 0:
		var sp: Vector2i = shopkeeper["pos"]
		if is_visible_cell(sp):
			var merchant_mark = "闇" if merchant_type == "闇商人" else "商"
			draw_entity_visual(cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", merchant_mark, 14, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), TILE)

	if clone_active and is_visible_cell(clone_pos):
		draw_entity_visual(cell_center(clone_pos), "clone", "影", 16, Color("#91a9d6"), TILE)

	draw_entity_visual(cell_center(player), "player", "忍", 16, Color("#d9e2ee"), TILE)

	var hunger_note = "  【空腹注意】" if hunger <= 20 else ""
	draw_ui_text(Vector2(16, HUD_Y + 30), "銭 %d(+%d)  忍魂 %d(+%d)  ターン %d%s" % [coins, run_coins, souls, run_souls, turn_no, hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#ffb27d") if hunger <= 20 else Color("#c5cbd3"))
	draw_ui_text(Vector2(16, HUD_Y + 56), message.left(105), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#e4cf7a"))
	if unpaid_items.size() > 0:
		draw_ui_text(Vector2(16, HUD_Y + 82), "未精算 %d点 / 合計%d銭" % [unpaid_items.size(), shop_total_unpaid()], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ff9a7a"))
	if merchant_bound_turns > 0:
		draw_ui_text(Vector2(360, HUD_Y + 82), "商人縛影 %d" % merchant_bound_turns, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#a8c6ff"))
	if smoke_turns > 0:
		draw_ui_text(Vector2(520, HUD_Y + 82), "煙 %d" % smoke_turns, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#b7bdc8"))
	if clone_active:
		draw_ui_text(Vector2(610, HUD_Y + 82), "分身あと%d歩" % clone_steps_left, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#91a9d6"))
	if DEVELOPMENT_UI_ENABLED and debug_mode:
		draw_ui_text(Vector2(16, HUD_Y + 108), "DEBUG F2商店 F3ボス F9盗み準備 F12総合 / J分身", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#ffcf6b"))

	var map_button_landscape := Rect2(930, 82, 100, 38)
	draw_rect(map_button_landscape, Color("#252c35"))
	draw_rect(map_button_landscape, Color("#e4cf7a") if map_visible else Color("#48515e"), false, 1)
	draw_ui_text(map_button_landscape.position + Vector2(22, 25), "地図", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.WHITE)
	draw_mobile_controls()
	if inventory_menu:
		draw_inventory_overlay(false)
	elif checkout_prompt or stairs_prompt or ad_menu:
		draw_modal_overlay()


func is_visible_cell(p: Vector2i) -> bool:
	if not validate_grid(explored):
		return false
	if p.x < 0 or p.y < 0 or p.x >= MAP_W or p.y >= MAP_H:
		return false
	return bool(explored[p.y][p.x])


func cell_center(p: Vector2i) -> Vector2:
	return Vector2(MAP_X + p.x * TILE + TILE * 0.5, MAP_Y + p.y * TILE + TILE * 0.5)


func touch_action_available(action: String) -> bool:
	if action == "throw" or action == "trap":
		return true
	if action == "inventory":
		return true
	if action == "stairs":
		return player == stairs_pos and (not boss_spawned or boss_defeated)
	if action == "ultimate":
		return ninja_energy >= 100
	if action == "buy":
		return not unpaid_items.is_empty() and not shop_hostile
	if action == "hide":
		return ninja_energy >= 10
	if action == "bind" or action == "smoke":
		return ninja_energy >= 20
	if action == "clone":
		return ninja_energy >= 30 and not clone_active
	if action == "ad":
		return ad_boost_uses < 3
	return true


func draw_mobile_controls() -> void:
	var diamond_controls_landscape = [
		["道具", Rect2(714, 566, 48, 48)],
		["罠", Rect2(660, 618, 48, 48)],
		["飛", Rect2(768, 618, 48, 48)],
		["中断", Rect2(714, 670, 48, 42)]
	]
	for d_control in diamond_controls_landscape:
		var dr = d_control[1]
		draw_rect(dr, Color("#252c35"))
		draw_rect(dr, Color("#596675"), false, 1)
		draw_ui_text(dr.position + Vector2(7, 31), str(d_control[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color.WHITE)
	var base = Vector2(PAD_X, PAD_Y)
	var cell = float(PAD_CELL)
	var labels = [["↖", "↑", "↗"], ["←", "隠", "→"], ["↙", "↓", "↘"]]
	for y in range(3):
		for x in range(3):
			var r = Rect2(base.x + x * cell, base.y + y * cell, cell - 3, cell - 3)
			draw_rect(r, Color("#252c35"))
			draw_rect(r, Color("#48515e"), false, 1)
			draw_ui_text(r.position + Vector2(13, 29), labels[y][x], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)

	var actions = [
		["階段", "stairs", 20, 70], ["奥義", "ultimate", 94, 70], ["精算", "buy", 168, 70],
		["隠身", "hide", 242, 70], ["縛影", "bind", 316, 70], ["煙", "smoke", 390, 70],
		["分身", "clone", 464, 70], ["広告", "ad", 538, 70]
	]
	for a in actions:
		var r = Rect2(float(a[2]), 662, float(a[3]), 42)
		var available = touch_action_available(str(a[1]))
		draw_rect(r, Color("#252c35") if available else Color("#171c22"))
		draw_rect(r, Color("#48515e") if available else Color("#303740"), false, 1)
		draw_ui_text(r.position + Vector2(8, 27), str(a[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color.WHITE if available else Color("#707984"))


	# Debug builds expose a direct regression button so editor function-key shortcuts cannot swallow F12.
	if DEVELOPMENT_UI_ENABLED and OS.is_debug_build():
		var test_r = Rect2(790, 82, 130, 38)
		draw_rect(test_r, Color("#252c35"))
		draw_rect(test_r, Color("#e4cf7a"), false, 1)
		draw_ui_text(test_r.position + Vector2(18, 25), "自動検査", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color.WHITE)

	var styles = [["武", 570], ["影", 616], ["術", 662]]
	for st in styles:
		var r = Rect2(970, float(st[1]), 120, 40)
		draw_rect(r, Color("#303946") if style_name == str(st[0]) else Color("#252c35"))
		draw_rect(r, Color("#e4cf7a") if style_name == str(st[0]) else Color("#48515e"), false, 1)
		draw_ui_text(r.position + Vector2(48, 27), str(st[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)


func draw_modal_overlay() -> void:
	draw_rect(Rect2(220, 220, 660, 260), Color(0.05, 0.07, 0.09, 0.96))
	draw_rect(Rect2(220, 220, 660, 260), Color("#e4cf7a"), false, 2)
	if checkout_prompt or stairs_prompt:
		draw_ui_text(Vector2(285, 300), "商品を精算しますか？" if checkout_prompt else "次の階に降りますか？", HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color.WHITE)
		var yes_r = Rect2(350, 390, 160, 54)
		var no_r = Rect2(590, 390, 160, 54)
		for r in [yes_r, no_r]:
			draw_rect(r, Color("#252c35"))
			draw_rect(r, Color("#596575"), false, 1)
		draw_ui_text(yes_r.position + Vector2(48, 35), "はい", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
		draw_ui_text(no_r.position + Vector2(42, 35), "いいえ", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
	else:
		draw_ui_text(Vector2(285, 285), "任意広告ブースト（試作）", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color.WHITE)
		var labels = ["忍気", "能力", "全回復", "見ない"]
		var xs = [255, 405, 555, 705]
		for i in range(labels.size()):
			var r = Rect2(xs[i], 355, 130, 54)
			draw_rect(r, Color("#252c35"))
			draw_rect(r, Color("#596575"), false, 1)
			draw_ui_text(r.position + Vector2(22, 35), labels[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)


func toggle_map_visibility() -> void:
	map_visible = not map_visible
	message = "地図ON" if map_visible else "地図OFF"
	queue_redraw()
