import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:vibration/vibration.dart';

const String BACKEND_URL = 'https://isis-ungraspable-beatris.ngrok-free.dev';

void main() {
  runApp(const VoidApp());
}

class VoidApp extends StatelessWidget {
  const VoidApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VOID',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF050A14), // Deep Void Blue
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    // Animación de "Respiración" lenta
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));

    _initPermissions();
  }

  Future<void> _initPermissions() async {
    await Permission.microphone.request();
  }

  // 👇 INICIAR GRABACIÓN
  Future<void> _startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final directory = await getTemporaryDirectory();
        final path = '${directory.path}/void_temp.m4a';

        // Haptic: Vibración corta
        if (await Vibration.hasVibrator() ?? false) {
          Vibration.vibrate(duration: 50);
        }

        await _audioRecorder.start(const RecordConfig(), path: path);
        setState(() => _isRecording = true);
        print("🎙️ Grabando...");
      }
    } catch (e) {
      print("❌ Error al grabar: $e");
    }
  }

  // 👇 DETENER Y ENVIAR
  Future<void> _stopAndSend() async {
    try {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
        _isProcessing = true; // Modo "Pensando"
      });

      // Haptic: Doble vibración (Confirmación de envío)
      if (await Vibration.hasVibrator() ?? false) {
        Vibration.vibrate(pattern: [0, 50, 50, 50]);
      }

      if (path != null) {
        print("📤 Enviando a VOID...");
        await _uploadAudio(path);
      }
    } catch (e) {
      print("❌ Error al detener: $e");
      setState(() => _isProcessing = false);
    }
  }

  // 👇 SUBIDA AL BACKEND
  Future<void> _uploadAudio(String filePath) async {
    // Si olvidaste poner la URL, avisamos en consola
    if (BACKEND_URL.contains('AQUÍ_VA')) {
      print("⚠️ ERROR: No pusiste la URL de Ngrok en main.dart");
      setState(() => _isProcessing = false);
      return;
    }

    try {
      var uri = Uri.parse('$BACKEND_URL/input/voice');
      var request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      var response = await request.send();

      if (response.statusCode == 200) {
        print("✅ ÉXITO: VOID recibió la orden.");
        // Haptic: Vibración larga de éxito
        if (await Vibration.hasVibrator() ?? false) {
          Vibration.vibrate(duration: 200);
        }
      } else {
        print("⚠️ Error del servidor: ${response.statusCode}");
      }
    } catch (e) {
      print("❌ Error de conexión: $e");
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _audioRecorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Definimos colores según el estado
    Color ringColor = Colors.white.withOpacity(0.05); // Reposo (Casi invisible)
    Color glowColor = const Color(
      0xFF00F0FF,
    ).withOpacity(0.05); // Azul Cyan sutil

    if (_isRecording) {
      ringColor = const Color(0xFFFF4444).withOpacity(0.8); // Rojo Grabando
      glowColor = const Color(0xFFFF4444).withOpacity(0.3);
    } else if (_isProcessing) {
      ringColor = const Color(0xFF00F0FF).withOpacity(0.8); // Azul Procesando
      glowColor = const Color(0xFF00F0FF).withOpacity(0.3);
    }

    return Scaffold(
      // GestureDetector cubre TODA la pantalla
      body: GestureDetector(
        behavior:
            HitTestBehavior.opaque, // Importante para detectar toques en vacío
        onLongPressStart: (_) => _startRecording(),
        onLongPressEnd: (_) => _stopAndSend(),

        child: Center(
          child: AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              // Si está procesando, dejamos el tamaño fijo, si no, respira
              double scale = _isProcessing ? 1.0 : _scaleAnimation.value;

              return Transform.scale(
                scale: scale,
                child: _isProcessing
                    ? const SizedBox(
                        width: 80,
                        height: 80,
                        child: CircularProgressIndicator(
                          color: Color(0xFF00F0FF),
                          strokeWidth: 2,
                        ),
                      )
                    : Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: ringColor, width: 1.5),
                          boxShadow: [
                            BoxShadow(
                              color: glowColor,
                              blurRadius: 30,
                              spreadRadius: 1,
                            ),
                          ],
                        ),
                      ),
              );
            },
          ),
        ),
      ),
    );
  }
}
