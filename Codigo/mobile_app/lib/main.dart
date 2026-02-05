import 'package:flutter/material.dart';
import 'core/constants.dart';
import 'services/notification_service.dart';
import 'services/ghost_service.dart';
import 'ui/home_screen.dart';

/// 🚀 Punto de Entrada de la Aplicación VOID
void main() async {
  // Asegurar inicialización de Flutter
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializar servicio de notificaciones
  await NotificationService().initialize();

  // 👻 Inicializar Ghost Mode (Persistencia en segundo plano)
  await GhostService().initialize();

  // Ejecutar aplicación
  runApp(const VoidApp());
}

/// 🌌 Widget Principal de la Aplicación
class VoidApp extends StatelessWidget {
  const VoidApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VOID',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: AppColors.background,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
