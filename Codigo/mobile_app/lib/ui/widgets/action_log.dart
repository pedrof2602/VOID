import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/constants.dart';

/// 📝 Action Log - Lista Efímera de Mensajes
///
/// Muestra un historial de acciones/eventos en la parte inferior de la pantalla.
/// Los mensajes más recientes son más brillantes, los antiguos se desvanecen.
/// Usa IgnorePointer para no bloquear interacciones con la UI principal.
class ActionLog extends StatelessWidget {
  /// Lista de mensajes de log (máximo recomendado: 5-7)
  /// El último elemento es el más reciente
  final List<String> logs;

  /// Número máximo de logs a mostrar
  final int maxVisibleLogs;

  const ActionLog({super.key, required this.logs, this.maxVisibleLogs = 5});

  @override
  Widget build(BuildContext context) {
    // Tomar solo los últimos N logs
    final visibleLogs = logs.length > maxVisibleLogs
        ? logs.sublist(logs.length - maxVisibleLogs)
        : logs;

    return IgnorePointer(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: SafeArea(
          top: false,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Renderizar logs en orden inverso (más reciente abajo)
              ...List.generate(
                visibleLogs.length,
                (index) => _buildLogEntry(
                  visibleLogs[index],
                  index,
                  visibleLogs.length,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Construye una entrada individual de log
  Widget _buildLogEntry(String message, int index, int totalLogs) {
    // Calcular opacidad: el más reciente (último) tiene opacidad 1.0
    // Los anteriores se desvanecen gradualmente
    final opacity = _calculateOpacity(index, totalLogs);

    // Calcular color: más reciente = cyan brillante, antiguos = blanco tenue
    final color = _calculateColor(index, totalLogs);

    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Opacity(
        opacity: opacity,
        child: Center(
          child: Text(
            message,
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 11,
              fontWeight: FontWeight.w300,
              color: color,
              letterSpacing: 0.2,
              height: 1.5,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
    );
  }

  /// Calcula la opacidad basada en la posición del log
  /// El más reciente (index más alto) tiene opacidad 1.0
  double _calculateOpacity(int index, int totalLogs) {
    if (totalLogs == 1) return 1.0;

    // Gradiente de opacidad: 0.3 (más antiguo) → 1.0 (más reciente)
    final normalizedPosition = index / (totalLogs - 1);
    return 0.3 + (normalizedPosition * 0.7);
  }

  /// Calcula el color basado en la posición del log
  /// El más reciente es cyan brillante, los antiguos son blancos tenues
  Color _calculateColor(int index, int totalLogs) {
    if (totalLogs == 1) return AppColors.cyan;

    // Gradiente de color: blanco (antiguo) → cyan (reciente)
    final normalizedPosition = index / (totalLogs - 1);

    if (normalizedPosition > 0.7) {
      // Los 2-3 más recientes: cyan
      return AppColors.cyan;
    } else if (normalizedPosition > 0.4) {
      // Intermedios: blanco
      return AppColors.white;
    } else {
      // Antiguos: blanco tenue
      return AppColors.white.withValues(alpha: 0.6);
    }
  }
}
