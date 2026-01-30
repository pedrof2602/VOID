import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/void_command.dart';

/// Servicio responsable de ejecutar acciones de comandos VOID
/// Soporta deep linking con apps populares
class ActionHandler {
  // ============================================================================
  // NAVEGACIÓN
  // ============================================================================

  /// Abre Google Maps para navegar a un destino
  Future<void> openGoogleMaps(
    String destination, {
    bool navigate = true,
  }) async {
    final encodedDest = Uri.encodeComponent(destination);
    final url = navigate
        ? 'https://www.google.com/maps/dir/?api=1&destination=$encodedDest'
        : 'https://www.google.com/maps/search/?api=1&query=$encodedDest';

    debugPrint('🗺️ Abriendo Google Maps: $destination');
    await _launchURL(url);
  }

  /// Abre Waze para navegar a un destino
  Future<void> openWaze(String destination) async {
    final encodedDest = Uri.encodeComponent(destination);
    final url = 'https://waze.com/ul?q=$encodedDest&navigate=yes';

    debugPrint('🚗 Abriendo Waze: $destination');
    await _launchURL(url);
  }

  // ============================================================================
  // TRANSPORTE
  // ============================================================================

  /// Abre Uber con pickup y destino pre-cargados
  /// Si pickup es null, usa ubicación actual
  Future<void> openUber({String? pickup, required String destination}) async {
    final pickupParam = pickup != null
        ? 'pickup[formatted_address]=${Uri.encodeComponent(pickup)}'
        : 'pickup=my_location';

    final dropoffParam =
        'dropoff[formatted_address]=${Uri.encodeComponent(destination)}';

    final url =
        'https://m.uber.com/ul/?action=setPickup&$pickupParam&$dropoffParam';

    debugPrint(
      '🚕 Abriendo Uber: ${pickup ?? "ubicación actual"} → $destination',
    );
    await _launchURL(url);
  }

  /// Abre Cabify (similar a Uber)
  Future<void> openCabify(String destination) async {
    final encodedDest = Uri.encodeComponent(destination);
    final url = 'https://cabify.com/ride?destination=$encodedDest';

    debugPrint('🚖 Abriendo Cabify: $destination');
    await _launchURL(url);
  }

  // ============================================================================
  // PRODUCTIVIDAD
  // ============================================================================

  /// Agrega un evento al calendario
  Future<void> addCalendarEvent(String title, {DateTime? startTime}) async {
    final start = startTime ?? DateTime.now().add(const Duration(hours: 1));
    final end = start.add(const Duration(hours: 1));

    // Formato: yyyyMMddTHHmmss
    final startStr = _formatDateTimeForCalendar(start);
    final endStr = _formatDateTimeForCalendar(end);

    final encodedTitle = Uri.encodeComponent(title);
    final url =
        'https://www.google.com/calendar/render?action=TEMPLATE&text=$encodedTitle&dates=$startStr/$endStr';

    debugPrint('📅 Agregando evento al calendario: $title');
    await _launchURL(url);
  }

  /// Crea una nota en Google Keep
  Future<void> createNote(String content) async {
    final encodedContent = Uri.encodeComponent(content);
    final url = 'https://keep.google.com/u/0/#NOTE/$encodedContent';

    debugPrint('📝 Creando nota: $content');
    await _launchURL(url);
  }

  // ============================================================================
  // COMUNICACIÓN
  // ============================================================================

  /// Envía un mensaje por WhatsApp
  /// phoneNumber debe estar en formato internacional sin +
  Future<void> sendWhatsApp(String phoneNumber, String message) async {
    final encodedMessage = Uri.encodeComponent(message);
    final cleanPhone = phoneNumber.replaceAll(RegExp(r'[^\d]'), '');
    final url = 'https://wa.me/$cleanPhone?text=$encodedMessage';

    debugPrint('💬 Abriendo WhatsApp: $phoneNumber');
    await _launchURL(url);
  }

  /// Compone un email
  Future<void> composeEmail(String to, String subject, String body) async {
    final encodedSubject = Uri.encodeComponent(subject);
    final encodedBody = Uri.encodeComponent(body);
    final url = 'mailto:$to?subject=$encodedSubject&body=$encodedBody';

    debugPrint('📧 Componiendo email a: $to');
    await _launchURL(url);
  }

  // ============================================================================
  // ENTRETENIMIENTO
  // ============================================================================

  /// Busca y reproduce en Spotify
  Future<void> playSpotify(String query) async {
    final encodedQuery = Uri.encodeComponent(query);
    final url = 'spotify:search:$encodedQuery';

    debugPrint('🎵 Buscando en Spotify: $query');
    await _launchURL(url);
  }

  /// Busca en YouTube
  Future<void> searchYouTube(String query) async {
    final encodedQuery = Uri.encodeComponent(query);
    final url = 'https://www.youtube.com/results?search_query=$encodedQuery';

    debugPrint('📺 Buscando en YouTube: $query');
    await _launchURL(url);
  }

  // ============================================================================
  // COMPRAS
  // ============================================================================

  /// Busca en MercadoLibre Argentina
  Future<void> searchMercadoLibre(String query) async {
    final encodedQuery = Uri.encodeComponent(query);
    final url = 'https://listado.mercadolibre.com.ar/$encodedQuery';

    debugPrint('🛒 Buscando en MercadoLibre: $query');
    await _launchURL(url);
  }

  /// Busca en Google
  Future<void> searchGoogle(String query) async {
    final encodedQuery = Uri.encodeComponent(query);
    final url = 'https://www.google.com/search?q=$encodedQuery';

    debugPrint('🔍 Buscando en Google: $query');
    await _launchURL(url);
  }

  // ============================================================================
  // EJECUCIÓN GENÉRICA (Para compatibilidad con VoidCommand)
  // ============================================================================

  /// Ejecuta un comando VOID
  Future<void> executeCommand(VoidCommand command) async {
    debugPrint('🚀 VOID OS: Ejecutando comando "${command.summary}"');
    debugPrint('   Categoría: ${command.category.name}');
    debugPrint('   URL: ${command.actionData.url}');

    final urlString = command.actionData.url;

    if (urlString == null || urlString.isEmpty) {
      debugPrint('❌ Error: No hay URL para ejecutar');
      _handleError(
        command,
        'No se proporcionó una URL para ejecutar la acción',
      );
      return;
    }

    final Uri? uri = Uri.tryParse(urlString);
    if (uri == null) {
      debugPrint('❌ Error: URL inválida: $urlString');
      _handleError(command, 'La URL proporcionada no es válida');
      return;
    }

    await _launchURL(urlString);
  }

  // ============================================================================
  // HELPERS PRIVADOS
  // ============================================================================

  /// Lanza una URL con manejo robusto de errores
  Future<void> _launchURL(String urlString) async {
    final Uri? uri = Uri.tryParse(urlString);

    if (uri == null) {
      debugPrint('❌ URL inválida: $urlString');
      return;
    }

    try {
      final canLaunch = await canLaunchUrl(uri);

      if (canLaunch) {
        final success = await launchUrl(
          uri,
          mode: LaunchMode.externalApplication,
        );
        if (success) {
          debugPrint('✅ Acción ejecutada exitosamente');
        } else {
          debugPrint('⚠️ launchUrl retornó false');
        }
      } else {
        debugPrint(
          '⚠️ canLaunchUrl retornó false, intentando de todas formas...',
        );
        try {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
          debugPrint('✅ Acción ejecutada (intento forzado)');
        } catch (e) {
          debugPrint('❌ Error en intento forzado: $e');
        }
      }
    } catch (e) {
      debugPrint('❌ Error crítico al ejecutar acción: $e');
    }
  }

  /// Formatea DateTime para Google Calendar
  String _formatDateTimeForCalendar(DateTime dt) {
    return '${dt.year}${_pad(dt.month)}${_pad(dt.day)}T${_pad(dt.hour)}${_pad(dt.minute)}00';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');

  /// Maneja errores de ejecución
  void _handleError(VoidCommand command, String errorMessage) {
    debugPrint('🔴 ERROR en comando ${command.id}: $errorMessage');
  }
}
