import 'package:flutter/material.dart';

/// 🌐 Configuración Global de la Aplicación VOID
class AppConfig {
  // Prevenir instanciación
  AppConfig._();

  /// URL del backend (ngrok o producción)
  static const String backendUrl =
      'https://isis-ungraspable-beatris.ngrok-free.dev';

  /// ID único del usuario
  static const String userId = '98181061-0369-4267-9a9a-72f480744a2b';

  /// Endpoint de la API de voz
  static const String voiceEndpoint = '/input/voice';
}

/// 🎨 Paleta de Colores de VOID
class AppColors {
  // Prevenir instanciación
  AppColors._();

  /// Color de fondo principal (Deep Void Blue)
  static const Color background = Color(0xFF050A14);

  /// Color cyan para estados activos y procesamiento
  static const Color cyan = Color(0xFF00F0FF);

  /// Color rojo para grabación
  static const Color red = Color(0xFFFF4444);

  /// Color blanco para estado de reposo
  static const Color white = Colors.white;
}

/// ⏱️ Duraciones de Animaciones y Feedback
class AppDurations {
  // Prevenir instanciación
  AppDurations._();

  /// Duración de la animación de respiración del anillo
  static const Duration breathingAnimation = Duration(seconds: 4);

  /// Vibración sutil al iniciar grabación
  static const int subtleVibration = 30;

  /// Vibración de procesamiento
  static const int processingVibration = 20;

  /// Vibración larga de error
  static const int errorVibration = 400;

  /// Patrón de vibración de éxito: [pausa, vibra, pausa, vibra]
  static const List<int> successVibrationPattern = [0, 80, 50, 80];
}

/// 🔔 Configuración de Notificaciones
class NotificationConfig {
  // Prevenir instanciación
  NotificationConfig._();

  /// ID del canal de notificaciones Android
  static const String channelId = 'void_ops_channel';

  /// Nombre del canal
  static const String channelName = 'VOID Operations';

  /// Descripción del canal
  static const String channelDescription = 'Estado operativo de la IA';

  /// Color de las notificaciones
  static const Color notificationColor = AppColors.cyan;

  /// Icono de la app para notificaciones Android
  static const String androidIcon = '@mipmap/ic_launcher';
}

/// 🎵 Configuración de Assets de Audio
class AudioAssets {
  // Prevenir instanciación
  AudioAssets._();

  /// Sonido de éxito
  static const String success = 'sounds/success.mp3';

  /// Sonido de error
  static const String error = 'sounds/error.mp3';
}
