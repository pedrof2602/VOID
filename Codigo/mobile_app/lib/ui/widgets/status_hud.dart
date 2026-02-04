import 'package:flutter/material.dart';
import '../../core/constants.dart';

/// 📊 Status HUD - Barra Superior Minimalista
///
/// Muestra el estado de conexión y latencia en un diseño técnico.
/// Usa glassmorphism sutil para no obstruir la vista.
/// El indicador de conexión parpadea lentamente cuando está online.
class StatusHud extends StatefulWidget {
  /// Indica si hay conexión activa con el backend
  final bool isConnected;

  /// Latencia de la conexión (ej: "45ms", "120ms")
  final String latency;

  const StatusHud({
    super.key,
    required this.isConnected,
    required this.latency,
  });

  @override
  State<StatusHud> createState() => _StatusHudState();
}

class _StatusHudState extends State<StatusHud>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    // Animación de pulso lento (2 segundos)
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        // Glassmorphism sutil
        color: AppColors.background.withValues(alpha: 0.3),
        border: Border(
          bottom: BorderSide(
            color: AppColors.white.withValues(alpha: 0.05),
            width: 1,
          ),
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Indicador de conexión
            _buildConnectionIndicator(),

            // Latencia
            _buildLatencyIndicator(),
          ],
        ),
      ),
    );
  }

  /// Construye el indicador de estado de conexión con parpadeo
  Widget _buildConnectionIndicator() {
    final statusColor = widget.isConnected ? AppColors.cyan : AppColors.red;

    final statusText = widget.isConnected ? 'ONLINE' : 'OFFLINE';

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Punto de estado (pulsante si está conectado)
        widget.isConnected
            ? AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: statusColor.withValues(
                        alpha: _pulseAnimation.value,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: statusColor.withValues(
                            alpha: _pulseAnimation.value * 0.6,
                          ),
                          blurRadius: 8 + (_pulseAnimation.value * 4),
                          spreadRadius: 2 + (_pulseAnimation.value * 2),
                        ),
                      ],
                    ),
                  );
                },
              )
            : Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: statusColor,
                ),
              ),
        const SizedBox(width: 8),

        // Texto de estado
        Text(
          statusText,
          style: TextStyle(
            fontFamily: 'Courier',
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: statusColor.withValues(alpha: 0.9),
            letterSpacing: 1.2,
          ),
        ),
      ],
    );
  }

  /// Construye el indicador de latencia
  Widget _buildLatencyIndicator() {
    // Determinar color según latencia
    Color latencyColor;
    final latencyValue = int.tryParse(widget.latency.replaceAll('ms', '')) ?? 0;

    if (latencyValue < 50) {
      latencyColor = AppColors.cyan; // Excelente
    } else if (latencyValue < 100) {
      latencyColor = AppColors.white; // Bueno
    } else {
      latencyColor = AppColors.red; // Lento
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Icono de señal
        Icon(
          Icons.signal_cellular_alt,
          size: 14,
          color: latencyColor.withValues(alpha: 0.7),
        ),
        const SizedBox(width: 6),

        // Valor de latencia
        Text(
          widget.latency,
          style: TextStyle(
            fontFamily: 'Courier',
            fontSize: 11,
            fontWeight: FontWeight.w500,
            color: latencyColor.withValues(alpha: 0.8),
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }
}
