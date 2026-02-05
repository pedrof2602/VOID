import 'dart:async';
import 'package:audio_service/audio_service.dart';
import 'package:just_audio/just_audio.dart';
import 'package:flutter/foundation.dart';

/// 🎧 Headset Service
///
/// Servicio unificado que combina:
/// 1. Persistencia en segundo plano (silent audio loop)
/// 2. Control por botones físicos de auriculares (Play/Pause/Click)
///
/// Reemplaza a GhostService con una solución más robusta basada en audio_service.
class HeadsetService {
  // Singleton pattern
  static final HeadsetService _instance = HeadsetService._internal();
  factory HeadsetService() => _instance;
  HeadsetService._internal();

  // Stream para emitir eventos de botón
  final StreamController<void> _buttonPressController =
      StreamController<void>.broadcast();

  // Audio handler
  _MyAudioHandler? _audioHandler;
  bool _isInitialized = false;

  /// 🚀 Inicializa el servicio de auriculares
  ///
  /// Configura audio_service con un handler personalizado que:
  /// - Reproduce audio silencioso en loop (mantiene app viva)
  /// - Escucha eventos de botones físicos
  Future<void> initialize() async {
    if (_isInitialized) {
      debugPrint('🎧 HeadsetService ya está inicializado');
      return;
    }

    try {
      debugPrint('🎧 Inicializando HeadsetService...');

      // Inicializar audio_service con nuestro handler personalizado
      _audioHandler = await AudioService.init(
        builder: () => _MyAudioHandler(_buttonPressController),
        config: const AudioServiceConfig(
          androidNotificationChannelId: 'com.void.app.audio',
          androidNotificationChannelName: 'VOID Audio Service',
          androidNotificationOngoing: false,
          androidShowNotificationBadge: false,
          androidStopForegroundOnPause: false,
        ),
      );

      debugPrint('🎧 ✅ HeadsetService inicializado exitosamente');
      _isInitialized = true;
    } catch (e, stackTrace) {
      debugPrint('🎧 ❌ Error inicializando HeadsetService: $e');
      debugPrint('🎧 StackTrace: $stackTrace');
      // No lanzamos la excepción para no romper el inicio de la app
    }
  }

  /// 📡 Stream de eventos de botón
  ///
  /// Emite un evento cada vez que se presiona un botón físico
  Stream<void> get onButtonPress => _buttonPressController.stream;

  /// 🛑 Detiene el servicio y libera recursos
  Future<void> dispose() async {
    try {
      debugPrint('🎧 Deteniendo HeadsetService...');
      await _audioHandler?.stop();
      await _buttonPressController.close();
      _isInitialized = false;
      debugPrint('🎧 HeadsetService detenido correctamente');
    } catch (e) {
      debugPrint('🎧 Error deteniendo HeadsetService: $e');
    }
  }

  /// 📊 Estado de inicialización
  bool get isInitialized => _isInitialized;
}

/// 🎵 Audio Handler Personalizado
///
/// Maneja la reproducción de audio silencioso y los eventos de botones físicos.
class _MyAudioHandler extends BaseAudioHandler {
  final StreamController<void> _buttonPressController;
  final AudioPlayer _player = AudioPlayer();

  _MyAudioHandler(this._buttonPressController) {
    _initAudio();
  }

  /// Inicializa el reproductor de audio silencioso
  Future<void> _initAudio() async {
    try {
      debugPrint('🎵 Cargando audio silencioso...');

      // Cargar el asset de silencio
      await _player.setAsset('assets/sounds/silence.wav');

      // Configurar loop infinito
      await _player.setLoopMode(LoopMode.all);

      // CRÍTICO: Volumen a 0 para silencio absoluto
      await _player.setVolume(0.0);

      // Iniciar reproducción
      await _player.play();

      debugPrint('🎵 Audio silencioso iniciado correctamente');
    } catch (e) {
      debugPrint('🎵 Error inicializando audio: $e');
    }
  }

  /// 🎯 Handler para clic simple (botón central de auriculares)
  @override
  Future<void> click([MediaButton button = MediaButton.media]) async {
    debugPrint('🎧 Botón presionado: click()');
    _buttonPressController.add(null);
  }

  /// ▶️ Handler para botón Play
  @override
  Future<void> play() async {
    debugPrint('🎧 Botón presionado: play()');
    _buttonPressController.add(null);
  }

  /// ⏸️ Handler para botón Pause
  @override
  Future<void> pause() async {
    debugPrint('🎧 Botón presionado: pause()');
    _buttonPressController.add(null);
  }

  /// ⏹️ Handler para botón Stop
  @override
  Future<void> stop() async {
    debugPrint('🎧 Botón presionado: stop()');
    await _player.stop();
    await _player.dispose();
    return super.stop();
  }
}
