import 'dart:async';
import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../services/api_service.dart';
import '../services/feedback_service.dart';
import '../services/notification_service.dart';
import '../services/recorder_service.dart';
import 'widgets/status_hud.dart';
import 'widgets/action_log.dart';

/// 🏠 Pantalla Principal de VOID
///
/// Interfaz de voz con feedback sensorial y animaciones.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  // ————————————————————————————————————————————————
  // 🎬 CONTROLADORES DE ANIMACIÓN
  // ————————————————————————————————————————————————
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  // ————————————————————————————————————————————————
  // 🔧 SERVICIOS
  // ————————————————————————————————————————————————
  final _apiService = ApiService();
  final _feedbackService = FeedbackService();
  final _notificationService = NotificationService();
  final _recorderService = RecorderService();

  // ————————————————————————————————————————————————
  // 📊 ESTADO
  // ————————————————————————————————————————————————
  bool _isRecording = false;
  bool _isProcessing = false;

  // Estado de HUD
  //todo: implementar HUD dinamico segun conexion
  final List<String> _actionLogs = [];
  bool _isConnected = true;
  String _latency = "12ms";

  @override
  void initState() {
    super.initState();
    _setupAnimation();
    _initializeServices();
  }

  /// Configura la animación de respiración del anillo
  void _setupAnimation() {
    _controller = AnimationController(
      vsync: this,
      duration: AppDurations.breathingAnimation,
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  /// Inicializa todos los servicios
  Future<void> _initializeServices() async {
    await _feedbackService.initialize();
    await _recorderService.initialize();
    await _notificationService.requestPermissions();

    // Log inicial
    _addLog("System initialized");
  }

  // ————————————————————————————————————————————————
  // 📝 GESTIÓN DE LOGS
  // ————————————————————————————————————————————————

  /// Agrega un mensaje al log de acciones
  ///
  /// - Limita a 3 mensajes máximo
  /// - Auto-elimina el mensaje después de 5 segundos
  void _addLog(String message) {
    setState(() {
      _actionLogs.add(message);

      // Limitar a 3 mensajes
      if (_actionLogs.length > 3) {
        _actionLogs.removeAt(0);
      }
    });

    // Auto-eliminar después de 5 segundos
    Timer(const Duration(seconds: 5), () {
      if (mounted && _actionLogs.contains(message)) {
        setState(() {
          _actionLogs.remove(message);
        });
      }
    });
  }

  // ————————————————————————————————————————————————
  // 🎙️ LÓGICA DE GRABACIÓN
  // ————————————————————————————————————————————————

  /// Inicia la grabación de audio
  Future<void> _startRecording() async {
    try {
      _addLog("🎙️ Recording audio...");

      final started = await _recorderService.startRecording();

      if (started) {
        setState(() => _isRecording = true);
        await _feedbackService.playSubtle();
      }
    } on RecorderException catch (e) {
      debugPrint('Error al iniciar grabación: $e');
      _addLog("❌ Recording failed");
      await _feedbackService.playError();
      await _notificationService.show(
        title: 'VOID Error',
        body: 'No se pudo iniciar la grabación',
      );
    }
  }

  /// Detiene la grabación y envía el audio al backend
  Future<void> _stopAndSend() async {
    try {
      final path = await _recorderService.stopRecording();

      setState(() {
        _isRecording = false;
        _isProcessing = true;
      });

      await _feedbackService.playProcessing();
      _addLog("🔐 Encrypting audio packet...");

      if (path != null) {
        await _uploadAudio(path);
      }
    } on RecorderException catch (e) {
      debugPrint('Error al detener grabación: $e');
      _addLog("❌ Error: Recording stopped");
      setState(() => _isProcessing = false);
      await _feedbackService.playError();
    }
  }

  /// Sube el audio al backend
  Future<void> _uploadAudio(String filePath) async {
    try {
      _addLog("📤 Transmitting to VOID...");

      final response = await _apiService.uploadAudio(filePath);

      // ✅ ÉXITO
      setState(() {
        _isConnected = true;
        _latency = "${12 + (response.statusCode % 30)}ms"; // Simulado
      });

      _addLog("✅ Command executed: #${response.statusCode}");
      await _feedbackService.playSuccess();
      await _notificationService.show(
        title: 'VOID',
        body: 'Comando ejecutado correctamente',
        payload: response.message,
      );
    } on ApiException catch (e) {
      // ❌ ERROR
      debugPrint('Error de API: $e');

      setState(() => _isConnected = false);
      _addLog("❌ Error: Connection lost");

      await _feedbackService.playError();
      await _notificationService.show(title: 'VOID Error', body: e.message);
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _feedbackService.dispose();
    _recorderService.dispose();
    super.dispose();
  }

  // ————————————————————————————————————————————————
  // 🎨 UI - GLASS COCKPIT
  // ————————————————————————————————————————————————

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          // ————————————————————————————————————————————————
          // CAPA 1: NÚCLEO CENTRAL (Orbe + Gesture Detection)
          // ————————————————————————————————————————————————
          GestureDetector(
            behavior: HitTestBehavior.opaque,
            onLongPressStart: (_) => _startRecording(),
            onLongPressEnd: (_) => _stopAndSend(),
            child: Center(
              child: AnimatedBuilder(
                animation: _controller,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _isProcessing ? 1.0 : _scaleAnimation.value,
                    child: _buildVoidRing(),
                  );
                },
              ),
            ),
          ),

          // ————————————————————————————————————————————————
          // CAPA 2: HUD SUPERIOR (Status + Latency)
          // ————————————————————————————————————————————————
          Positioned(
            top: 50,
            left: 20,
            right: 20,
            child: StatusHud(isConnected: _isConnected, latency: _latency),
          ),

          // ————————————————————————————————————————————————
          // CAPA 3: LOG INFERIOR (Action History)
          // ————————————————————————————————————————————————
          Positioned(
            bottom: 100,
            left: 20,
            right: 20,
            child: ActionLog(logs: _actionLogs, maxVisibleLogs: 3),
          ),
        ],
      ),
    );
  }

  /// Construye el anillo visual de VOID
  Widget _buildVoidRing() {
    // Determinar colores según el estado
    Color ringColor;
    Color glowColor;
    double size;
    double borderWidth;

    if (_isRecording) {
      // 🔴 GRABANDO
      ringColor = AppColors.red.withValues(alpha: 0.8);
      glowColor = AppColors.red.withValues(alpha: 0.3);
      size = 140;
      borderWidth = 2;
    } else if (_isProcessing) {
      // 🔵 PROCESANDO (mismo tamaño, efecto neón cyan)
      ringColor = AppColors.cyan.withValues(alpha: 0.8);
      glowColor = AppColors.cyan.withValues(alpha: 0.3);
      size = 140;
      borderWidth = 2;
    } else {
      // ⚪ REPOSO
      ringColor = AppColors.white.withValues(alpha: 0.05);
      glowColor = AppColors.cyan.withValues(alpha: 0.05);
      size = 140;
      borderWidth = 2;
    }

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: ringColor, width: borderWidth),
        boxShadow: _isProcessing
            ? [
                // Capa 1: Glow interno intenso
                BoxShadow(
                  color: glowColor.withValues(alpha: 0.6),
                  blurRadius: 30,
                  spreadRadius: 3,
                ),
                // Capa 2: Glow medio difuso
                BoxShadow(
                  color: glowColor.withValues(alpha: 0.4),
                  blurRadius: 60,
                  spreadRadius: 8,
                ),
                // Capa 3: Glow externo muy difuso (aura)
                BoxShadow(
                  color: glowColor.withValues(alpha: 0.2),
                  blurRadius: 100,
                  spreadRadius: 15,
                ),
              ]
            : [
                // Glow sutil para reposo/grabando
                BoxShadow(color: glowColor, blurRadius: 40, spreadRadius: 2),
              ],
      ),
    );
  }
}
