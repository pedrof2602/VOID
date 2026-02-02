import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:vibration/vibration.dart';
import 'package:http_parser/http_parser.dart';

// ⚠️ REVISA QUE ESTA SEA TU URL ACTUAL DE NGROK
const String backendUrl = 'https://isis-ungraspable-beatris.ngrok-free.dev';

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
    // Animación de respiración
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
    // Verificación de seguridad para evitar errores en compilación cruzada
    if (!Platform.isLinux && !Platform.isWindows && !Platform.isMacOS) {
      await Permission.microphone.request();
    }
  }

  Future<void> _startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final directory = await getTemporaryDirectory();
        final path = '${directory.path}/void_temp.m4a';

        if (await Vibration.hasVibrator() ?? false) {
          Vibration.vibrate(duration: 50);
        }

        await _audioRecorder.start(const RecordConfig(), path: path);
        setState(() => _isRecording = true);
        debugPrint("🎙️ Grabando...");
      }
    } catch (e) {
      debugPrint("❌ Error al grabar: $e");
    }
  }

  Future<void> _stopAndSend() async {
    try {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
        _isProcessing = true; // Modo "Thinking"
      });

      if (await Vibration.hasVibrator() ?? false) {
        Vibration.vibrate(pattern: [0, 50, 50, 50]);
      }

      if (path != null) {
        debugPrint("📤 Enviando a VOID...");
        await _uploadAudio(path);
      }
    } catch (e) {
      debugPrint("❌ Error al detener: $e");
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _uploadAudio(String filePath) async {
    // Validación rápida
    if (!backendUrl.contains('http')) {
      debugPrint("⚠️ ERROR: URL de Ngrok inválida");
      setState(() => _isProcessing = false);
      return;
    }

    try {
      var uri = Uri.parse('$backendUrl/input/voice');
      var request = http.MultipartRequest('POST', uri);

      // Definimos explícitamente el tipo de contenido (MIME Type)
      var audioFile = await http.MultipartFile.fromPath(
        'file',
        filePath,
        contentType: MediaType('audio', 'm4a'),
      );

      request.files.add(audioFile);

      request.fields['user_id'] = '98181061-0369-4267-9a9a-72f480744a2b';

      debugPrint("📤 Enviando archivo de ${await audioFile.length} bytes...");

      var response = await request.send();
      var responseBody = await response.stream
          .bytesToString(); // Leemos la respuesta

      if (response.statusCode == 200) {
        debugPrint("✅ ÉXITO: VOID respondió: $responseBody");
        if (await Vibration.hasVibrator() ?? false) {
          Vibration.vibrate(duration: 200);
        }
      } else {
        // Ahora veremos exactamente qué le molestó al servidor si falla
        debugPrint(
          "⚠️ Error del servidor (${response.statusCode}): $responseBody",
        );
      }
    } catch (e) {
      debugPrint("❌ Error de conexión: $e");
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
    // 🛡️ MODO SEGURO: Usamos withOpacity para garantizar compatibilidad con tu versión
    // Si te sale tachado en el editor, IGNÓRALO, funcionará igual.
    Color ringColor = Colors.white.withOpacity(0.05);
    Color glowColor = const Color(0xFF00F0FF).withOpacity(0.05);

    if (_isRecording) {
      ringColor = const Color(0xFFFF4444).withOpacity(0.8);
      glowColor = const Color(0xFFFF4444).withOpacity(0.3);
    } else if (_isProcessing) {
      ringColor = const Color(0xFF00F0FF).withOpacity(0.8);
      glowColor = const Color(0xFF00F0FF).withOpacity(0.3);
    }

    return Scaffold(
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onLongPressStart: (_) => _startRecording(),
        onLongPressEnd: (_) => _stopAndSend(),
        child: Center(
          child: AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
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
