import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';

/// 🎙️ Servicio de Grabación de Audio
///
/// Maneja la grabación de audio, permisos y gestión de archivos temporales.
/// Implementado como Singleton para reutilización global.
class RecorderService {
  // Singleton pattern
  static final RecorderService _instance = RecorderService._internal();
  factory RecorderService() => _instance;
  RecorderService._internal();

  final AudioRecorder _recorder = AudioRecorder();
  bool _isInitialized = false;
  String? _currentRecordingPath;

  /// Inicializa el servicio y solicita permisos
  ///
  /// Debe llamarse antes de usar el servicio
  Future<void> initialize() async {
    if (_isInitialized) return;

    // Solicitar permisos solo en plataformas móviles
    if (!Platform.isLinux && !Platform.isWindows && !Platform.isMacOS) {
      await Permission.microphone.request();
    }

    _isInitialized = true;
    debugPrint('✅ RecorderService inicializado');
  }

  /// Verifica si el servicio tiene permisos de micrófono
  ///
  /// Retorna true si tiene permisos
  Future<bool> hasPermission() async {
    return await _recorder.hasPermission();
  }

  /// Inicia la grabación de audio
  ///
  /// Retorna true si la grabación comenzó exitosamente
  ///
  /// Lanza [RecorderException] si no hay permisos o hay un error
  Future<bool> startRecording() async {
    try {
      // Verificar permisos
      if (!await hasPermission()) {
        throw RecorderException('No hay permisos de micrófono');
      }

      // Obtener directorio temporal
      final directory = await getTemporaryDirectory();
      _currentRecordingPath = '${directory.path}/void_temp.m4a';

      // Iniciar grabación
      await _recorder.start(const RecordConfig(), path: _currentRecordingPath!);

      debugPrint('🎙️ Grabando en: $_currentRecordingPath');
      return true;
    } catch (e) {
      debugPrint('❌ Error al iniciar grabación: $e');
      if (e is RecorderException) rethrow;
      throw RecorderException('Error al iniciar grabación: $e');
    }
  }

  /// Detiene la grabación de audio
  ///
  /// Retorna la ruta del archivo grabado o null si no hay grabación activa
  ///
  /// Lanza [RecorderException] si hay un error al detener
  Future<String?> stopRecording() async {
    try {
      final path = await _recorder.stop();

      if (path != null) {
        debugPrint('✅ Grabación detenida: $path');
      } else {
        debugPrint('⚠️ No había grabación activa');
      }

      return path;
    } catch (e) {
      debugPrint('❌ Error al detener grabación: $e');
      throw RecorderException('Error al detener grabación: $e');
    }
  }

  /// Verifica si hay una grabación en curso
  Future<bool> isRecording() async {
    return await _recorder.isRecording();
  }

  /// Cancela la grabación actual sin guardar
  Future<void> cancel() async {
    try {
      await _recorder.stop();

      // Eliminar archivo temporal si existe
      if (_currentRecordingPath != null) {
        final file = File(_currentRecordingPath!);
        if (await file.exists()) {
          await file.delete();
          debugPrint('🗑️ Archivo temporal eliminado');
        }
      }
    } catch (e) {
      debugPrint('Error al cancelar grabación: $e');
    }
  }

  /// Libera los recursos del servicio
  void dispose() {
    _recorder.dispose();
    _isInitialized = false;
  }
}

/// Excepción personalizada para errores de grabación
class RecorderException implements Exception {
  final String message;

  RecorderException(this.message);

  @override
  String toString() => 'RecorderException: $message';
}
