import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../core/constants.dart';

/// 🌐 Servicio de Comunicación con el Backend
///
/// Maneja todas las peticiones HTTP al servidor VOID.
/// Implementado como Singleton para reutilización global.
class ApiService {
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  /// Sube un archivo de audio al backend
  ///
  /// [filePath] Ruta absoluta del archivo de audio a subir
  ///
  /// Retorna [ApiResponse] con el resultado de la operación
  ///
  /// Lanza [ApiException] en caso de error
  Future<ApiResponse> uploadAudio(String filePath) async {
    // Validar URL del backend
    if (!AppConfig.backendUrl.contains('http')) {
      throw ApiException('URL de Backend inválida', statusCode: 0);
    }

    try {
      // Construir URI del endpoint
      final uri = Uri.parse(
        '${AppConfig.backendUrl}${AppConfig.voiceEndpoint}',
      );

      // Crear request multipart
      final request = http.MultipartRequest('POST', uri);

      // Agregar archivo de audio
      final audioFile = await http.MultipartFile.fromPath(
        'file',
        filePath,
        contentType: MediaType('audio', 'm4a'),
      );

      request.files.add(audioFile);
      request.fields['user_id'] = AppConfig.userId;

      // Log de debug
      debugPrint('📤 Enviando ${audioFile.length} bytes a $uri');

      // Enviar request
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      // Procesar respuesta
      if (response.statusCode == 200) {
        debugPrint('✅ VOID: $responseBody');
        return ApiResponse(
          success: true,
          statusCode: response.statusCode,
          message: responseBody,
        );
      } else {
        debugPrint('⚠️ Error (${response.statusCode}): $responseBody');
        throw ApiException(
          'Error del servidor: ${response.statusCode}',
          statusCode: response.statusCode,
          details: responseBody,
        );
      }
    } on SocketException {
      throw ApiException(
        'Fallo de conexión',
        statusCode: 0,
        details: 'No se pudo conectar al servidor',
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        'Error inesperado',
        statusCode: 0,
        details: e.toString(),
      );
    }
  }
}

/// Respuesta de la API
class ApiResponse {
  final bool success;
  final int statusCode;
  final String message;

  ApiResponse({
    required this.success,
    required this.statusCode,
    required this.message,
  });
}

/// Excepción personalizada para errores de API
class ApiException implements Exception {
  final String message;
  final int statusCode;
  final String? details;

  ApiException(this.message, {required this.statusCode, this.details});

  @override
  String toString() {
    if (details != null) {
      return 'ApiException: $message (Status: $statusCode)\nDetails: $details';
    }
    return 'ApiException: $message (Status: $statusCode)';
  }
}
