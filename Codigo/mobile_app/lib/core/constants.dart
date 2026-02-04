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

/// 🎨 Paleta de Colores de VOID (Apple Premium Style)
class AppColors {
  // Prevenir instanciación
  AppColors._();

  /// Color de fondo principal (Midnight Matte)
  static const Color background = Color(0xFF0F0F0F);

  /// Color coral para estado de grabación (Listening)
  static const Color coral = Color(0xFFFF5A5F);

  /// Color etéreo para procesamiento (Processing)
  static const Color ethereal = Color(0xFFE0E0FF);

  /// Color ámbar para errores
  static const Color amber = Color(0xFFFFB84D);

  /// Color blanco para estado de reposo
  static const Color white = Colors.white;

  // Alias para compatibilidad con código existente
  static const Color cyan = ethereal;
  static const Color red = coral;
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
