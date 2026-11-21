# AudioSynth.gd
# Sintetizador procedural de audio en tiempo de carga (sin archivos externos con derechos).
# Genera efectos realistas para disparos de M4 y AK-47, caída metálica de casquillos,
# clics mecánicos de recarga, apertura de puertas e impactos.

extends Node

const SAMPLE_RATE := 22050

var _wav_m4_shot: AudioStreamWAV
var _wav_ak_shot: AudioStreamWAV
var _wav_shell_clink: AudioStreamWAV
var _wav_mag_out: AudioStreamWAV
var _wav_mag_in: AudioStreamWAV
var _wav_bolt_rack: AudioStreamWAV
var _wav_door_open: AudioStreamWAV
var _wav_hitmarker: AudioStreamWAV

var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	_wav_m4_shot = _build_gunshot_wav(0.16, 170.0, 72.0, 0.95)
	_wav_ak_shot = _build_gunshot_wav(0.20, 125.0, 52.0, 1.0)
	_wav_shell_clink = _build_ping_wav(0.09, 4400.0, 5900.0, 0.35)
	_wav_mag_out = _build_mech_click_wav(0.11, 520.0, 260.0)
	_wav_mag_in = _build_mech_click_wav(0.12, 340.0, 760.0)
	_wav_bolt_rack = _build_mech_click_wav(0.16, 880.0, 1180.0)
	_wav_door_open = _build_mech_click_wav(0.26, 160.0, 110.0)
	_wav_hitmarker = _build_ping_wav(0.055, 2200.0, 1800.0, 0.45)


func play_m4_shot() -> void:
	_play_2d(_wav_m4_shot, _rng.randf_range(0.95, 1.06), -2.0)


func play_ak_shot_3d(world_pos: Vector3) -> void:
	_play_3d(_wav_ak_shot, world_pos, _rng.randf_range(0.92, 1.04), -3.0, 32.0)


func play_shell_clink_3d(world_pos: Vector3) -> void:
	_play_3d(_wav_shell_clink, world_pos, _rng.randf_range(0.88, 1.18), -11.0, 10.0)


func play_mag_out() -> void:
	_play_2d(_wav_mag_out, 1.0, -5.0)


func play_mag_in() -> void:
	_play_2d(_wav_mag_in, 1.0, -4.0)


func play_bolt_rack() -> void:
	_play_2d(_wav_bolt_rack, 1.0, -4.0)


func play_door_3d(world_pos: Vector3) -> void:
	_play_3d(_wav_door_open, world_pos, _rng.randf_range(0.92, 1.08), -5.0, 18.0)


func play_hitmarker(is_headshot: bool = false) -> void:
	_play_2d(_wav_hitmarker, 1.35 if is_headshot else 1.0, -4.0)


const MAX_CONCURRENT_VOICES := 14

func _play_2d(stream: AudioStreamWAV, pitch: float, volume_db: float) -> void:
	if stream == null or get_child_count() >= MAX_CONCURRENT_VOICES:
		return
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.pitch_scale = pitch
	p.volume_db = volume_db
	add_child(p)
	p.finished.connect(p.queue_free)
	p.play()


func _play_3d(stream: AudioStreamWAV, pos: Vector3, pitch: float, volume_db: float, max_dist: float) -> void:
	if stream == null or not is_inside_tree() or get_child_count() >= MAX_CONCURRENT_VOICES:
		return
	var p := AudioStreamPlayer3D.new()
	p.stream = stream
	p.pitch_scale = pitch
	p.volume_db = volume_db
	p.max_distance = max_dist
	add_child(p)
	p.global_position = pos
	p.finished.connect(p.queue_free)
	p.play()


func _encode_samples_16bit(samples: PackedFloat32Array) -> AudioStreamWAV:
	var bytes := PackedByteArray()
	bytes.resize(samples.size() * 2)
	for i in samples.size():
		var clamped := clampf(samples[i], -1.0, 1.0)
		var val := int(clamped * 32767.0)
		bytes.encode_s16(i * 2, val)
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = SAMPLE_RATE
	wav.stereo = false
	wav.data = bytes
	return wav


func _build_gunshot_wav(duration: float, f_start: float, f_end: float, punch: float) -> AudioStreamWAV:
	var count := int(SAMPLE_RATE * duration)
	var buf := PackedFloat32Array()
	buf.resize(count)
	var phase := 0.0
	for i in count:
		var t := float(i) / float(SAMPLE_RATE)
		var norm := t / duration
		var env := exp(-norm * 14.0)
		var snap := exp(-norm * 42.0)
		var freq := lerpf(f_start, f_end, minf(1.0, norm * 2.5))
		phase += TAU * freq / float(SAMPLE_RATE)
		var noise := _rng.randf_range(-1.0, 1.0) * (0.78 * env + 0.35 * snap)
		var thump := sin(phase) * 0.65 * exp(-norm * 22.0)
		buf[i] = clampf((noise + thump) * punch, -1.0, 1.0)
	return _encode_samples_16bit(buf)


func _build_ping_wav(duration: float, f1: float, f2: float, gain: float) -> AudioStreamWAV:
	var count := int(SAMPLE_RATE * duration)
	var buf := PackedFloat32Array()
	buf.resize(count)
	for i in count:
		var t := float(i) / float(SAMPLE_RATE)
		var env := exp(-t / (duration * 0.28))
		var sig := (sin(TAU * f1 * t) * 0.6 + sin(TAU * f2 * t) * 0.4) * env * gain
		buf[i] = sig
	return _encode_samples_16bit(buf)


func _build_mech_click_wav(duration: float, f_low: float, f_high: float) -> AudioStreamWAV:
	var count := int(SAMPLE_RATE * duration)
	var buf := PackedFloat32Array()
	buf.resize(count)
	for i in count:
		var t := float(i) / float(SAMPLE_RATE)
		var norm := t / duration
		var env := exp(-norm * 16.0)
		var transient := _rng.randf_range(-1.0, 1.0) * exp(-norm * 35.0) * 0.45
		var body := (sin(TAU * f_low * t) * 0.5 + sin(TAU * f_high * t) * 0.35) * env
		buf[i] = clampf((transient + body) * 0.75, -1.0, 1.0)
	return _encode_samples_16bit(buf)
