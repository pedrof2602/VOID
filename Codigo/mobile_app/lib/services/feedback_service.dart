import 'package:audioplayers/audioplayers.dart';
import 'package:vibration/vibration.dart';
import 'package:flutter/foundation.dart';
import '../core/constants.dart';

/// 🎮 Servicio de Feedback Sensorial
///
/// Maneja audio y feedback háptico (vibración) para mejorar la experiencia del usuario.
/// Implementado como Singleton para reutilización global.
class FeedbackService {
  // Singleton pattern
  static final FeedbackService _instance = FeedbackService._internal();
  factory FeedbackService() => _instance;
  FeedbackService._internal();

  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isInitialized = false;

  /// Inicializa el servicio y precarga los sonidos
  ///
  /// Debe llamarse en el inicio de la aplicación para reducir latencia
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Precarga de sonidos para baja latencia
      await _audioPlayer.setSource(AssetSource(AudioAssets.success));
      await _audioPlayer.setSource(AssetSource(AudioAssets.error));

      _isInitialized = true;
      debugPrint('✅ FeedbackService inicializado');
    } catch (e) {
      debugPrint('⚠️ Advertencia: No se encontraron los sonidos en assets.');
      debugPrint('Error: $e');
    }
  }

  /// Reproduce feedback de éxito
  ///
  /// - Sonido cristalino
  /// - Doble vibración (patrón: pausa, vibra 80ms, pausa 50ms, vibra 80ms)
  Future<void> playSuccess() async {
    try {
      // Reproducir sonido de éxito
      await _audioPlayer.play(
        AssetSource(AudioAssets.success),
        mode: PlayerMode.lowLatency,
      );

      // Vibración de éxito (doble latido)
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(pattern: AppDurations.successVibrationPattern);
      }
    } catch (e) {
      debugPrint('Error en feedback de éxito: $e');
    }
  }

  /// Reproduce feedback de error
  ///
  /// - Sonido grave
  /// - Vibración larga (400ms)
  Future<void> playError() async {
    try {
      // Reproducir sonido de error
      await _audioPlayer.play(
        AssetSource(AudioAssets.error),
        mode: PlayerMode.lowLatency,
      );

      // Vibración de error (larga)
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(duration: AppDurations.errorVibration);
      }
    } catch (e) {
      debugPrint('Error en feedback de error: $e');
    }
  }

  /// Reproduce vibración sutil
  ///
  /// Usado al iniciar la grabación (30ms)
  Future<void> playSubtle() async {
    try {
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(duration: AppDurations.subtleVibration);
      }
    } catch (e) {
      debugPrint('Error en vibración sutil: $e');
    }
  }

  /// Reproduce vibración de procesamiento
  ///
  /// Usado al detener la grabación y comenzar el procesamiento (20ms)
  Future<void> playProcessing() async {
    try {
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(duration: AppDurations.processingVibration);
      }
    } catch (e) {
      debugPrint('Error en vibración de procesamiento: $e');
    }
  }

  /// Libera los recursos del servicio
  void dispose() {
    _audioPlayer.dispose();
    _isInitialized = false;
  }
}
