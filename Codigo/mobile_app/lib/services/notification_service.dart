import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../core/constants.dart';

/// 🔔 Servicio de Notificaciones Locales
///
/// Maneja la configuración y despliegue de notificaciones push locales.
/// Implementado como Singleton para reutilización global.
class NotificationService {
  // Singleton pattern
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();

  bool _isInitialized = false;

  /// Inicializa el servicio de notificaciones
  ///
  /// Debe llamarse en el main() antes de runApp()
  Future<void> initialize() async {
    if (_isInitialized) return;

    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings(NotificationConfig.androidIcon);

    const DarwinInitializationSettings initializationSettingsDarwin =
        DarwinInitializationSettings();

    const InitializationSettings initializationSettings =
        InitializationSettings(
          android: initializationSettingsAndroid,
          iOS: initializationSettingsDarwin,
        );

    await _plugin.initialize(
      settings: initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    _isInitialized = true;
    debugPrint('✅ NotificationService inicializado');
  }

  /// Callback cuando el usuario toca una notificación
  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('Notificación recibida: ${response.payload}');
    // Aquí se puede agregar navegación o lógica adicional
  }

  /// Solicita permisos de notificaciones (Android 13+)
  ///
  /// Retorna true si se otorgaron los permisos
  Future<bool> requestPermissions() async {
    if (Platform.isAndroid) {
      final androidImplementation = _plugin
          .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin
          >();

      final granted = await androidImplementation
          ?.requestNotificationsPermission();
      return granted ?? false;
    }
    return true; // iOS maneja permisos automáticamente
  }

  /// Muestra una notificación
  ///
  /// [title] Título de la notificación
  /// [body] Cuerpo del mensaje
  /// [payload] Datos opcionales para pasar al callback
  Future<void> show({
    required String title,
    required String body,
    String? payload,
  }) async {
    if (!_isInitialized) {
      debugPrint('⚠️ NotificationService no inicializado');
      return;
    }

    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
          NotificationConfig.channelId,
          NotificationConfig.channelName,
          channelDescription: NotificationConfig.channelDescription,
          importance: Importance.max,
          priority: Priority.high,
          color: NotificationConfig.notificationColor,
        );

    const NotificationDetails notificationDetails = NotificationDetails(
      android: androidDetails,
    );

    await _plugin.show(
      id: 0,
      title: title,
      body: body,
      notificationDetails: notificationDetails,
      payload: payload,
    );
  }

  /// Cancela todas las notificaciones
  Future<void> cancelAll() async {
    await _plugin.cancelAll();
  }

  /// Cancela una notificación específica
  Future<void> cancel(int id) async {
    await _plugin.cancel(id: id);
  }
}
