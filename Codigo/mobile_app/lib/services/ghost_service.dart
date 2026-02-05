import 'package:just_audio/just_audio.dart';
import 'package:audio_session/audio_session.dart';
import 'package:flutter/foundation.dart';

/// 👻 Ghost Mode Service
///
/// Mantiene la app viva en segundo plano mediante un loop de audio silencioso.
/// Esto previene que el OS mate la app cuando la pantalla se bloquea.
///
/// **Técnica:** Silent Audio Loop
/// - Reproduce `silence.wav` en loop infinito con volumen 0
/// - Mantiene una sesión de audio activa que el OS respeta
/// - Compatible con Android (WAKE_LOCK) e iOS (UIBackgroundModes: audio)
class GhostService {
  // Singleton pattern
  static final GhostService _instance = GhostService._internal();
  factory GhostService() => _instance;
  GhostService._internal();

  // Audio player instance
  final AudioPlayer _player = AudioPlayer();
  bool _isInitialized = false;

  /// 🚀 Inicializa Ghost Mode
  ///
  /// Configura la sesión de audio y comienza el loop silencioso.
  /// Debe llamarse en main.dart antes de runApp().
  Future<void> initialize() async {
    if (_isInitialized) {
      debugPrint('👻 Ghost Mode ya está inicializado');
      return;
    }

    try {
      debugPrint('👻 Inicializando Ghost Mode...');

      // 1. Configurar AudioSession
      final session = await AudioSession.instance;
      await session.configure(
        const AudioSessionConfiguration(
          avAudioSessionCategory: AVAudioSessionCategory.playback,
          avAudioSessionCategoryOptions:
              AVAudioSessionCategoryOptions.mixWithOthers,
          avAudioSessionMode: AVAudioSessionMode.defaultMode,
          avAudioSessionRouteSharingPolicy:
              AVAudioSessionRouteSharingPolicy.defaultPolicy,
          avAudioSessionSetActiveOptions: AVAudioSessionSetActiveOptions.none,
          androidAudioAttributes: AndroidAudioAttributes(
            contentType: AndroidAudioContentType.music,
            flags: AndroidAudioFlags.none,
            usage: AndroidAudioUsage.media,
          ),
          androidAudioFocusGainType: AndroidAudioFocusGainType.gain,
          androidWillPauseWhenDucked: false,
        ),
      );
      debugPrint('👻 AudioSession configurada correctamente');

      // 2. Cargar el asset de silencio
      await _player.setAsset('assets/sounds/silence.wav');
      debugPrint('👻 Asset silence.wav cargado');

      // 3. Configurar loop infinito
      await _player.setLoopMode(LoopMode.all);
      debugPrint('👻 Loop mode configurado: LoopMode.all');

      // 4. CRÍTICO: Volumen a 0 para silencio absoluto
      await _player.setVolume(0.0);
      debugPrint('👻 Volumen configurado: 0.0 (silencio)');

      // 5. Iniciar reproducción
      await _player.play();
      debugPrint('👻 ✅ Ghost Mode inicializado exitosamente');

      _isInitialized = true;
    } catch (e, stackTrace) {
      debugPrint('👻 ❌ Error inicializando Ghost Mode: $e');
      debugPrint('👻 StackTrace: $stackTrace');
      // No lanzamos la excepción para no romper el inicio de la app
      // Ghost Mode es un feature opcional que mejora la experiencia
    }
  }

  /// 🛑 Detiene Ghost Mode y libera recursos
  ///
  /// Útil para testing o si se necesita desactivar temporalmente.
  Future<void> stop() async {
    try {
      debugPrint('👻 Deteniendo Ghost Mode...');
      await _player.stop();
      await _player.dispose();
      _isInitialized = false;
      debugPrint('👻 Ghost Mode detenido correctamente');
    } catch (e) {
      debugPrint('👻 Error deteniendo Ghost Mode: $e');
    }
  }

  /// 📊 Estado de inicialización
  bool get isInitialized => _isInitialized;
}
