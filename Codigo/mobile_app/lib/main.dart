import 'dart:async';
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'models/void_command.dart';
import 'services/action_handler.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: 'https://trdkreqbyoulzsgepojd.supabase.co',
    anonKey:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRyZGtyZXFieW91bHpzZ2Vwb2pkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjI0NDAxMCwiZXhwIjoyMDgxODIwMDEwfQ.2kM2tc6wHU_I8yqgLS1Szao3uWDVDIDfUDl4A1PZyyg',
  );

  runApp(const VoidApp());
}

class VoidApp extends StatelessWidget {
  const VoidApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'VOID',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Colors.black,
        colorScheme: const ColorScheme.dark(primary: Colors.white),
      ),
      home: const VoidFeed(),
    );
  }
}

class VoidFeed extends StatefulWidget {
  const VoidFeed({super.key});

  @override
  State<VoidFeed> createState() => _VoidFeedState();
}

class _VoidFeedState extends State<VoidFeed> {
  // Servicio para ejecutar acciones
  final _actionHandler = ActionHandler();

  // Variable para controlar la escucha en segundo plano
  StreamSubscription? _commandSubscription;

  // Timer para polling activo
  Timer? _pollingTimer;

  // Guardamos el ID del último comando procesado para no repetirlo en bucle
  String? _lastProcessedId;

  // Stream para la UI (La lista visual)
  final _uiStream = Supabase.instance.client
      .from('recordings')
      .stream(primaryKey: ['id'])
      .order('created_at', ascending: false);

  @override
  void initState() {
    super.initState();
    _activarModoMayordomo();
    // Verificar comandos pendientes inmediatamente al abrir la app
    _verificarComandosPendientes();
    // Iniciar polling cada 3 segundos
    _iniciarPolling();
  }

  @override
  void dispose() {
    _commandSubscription?.cancel();
    _pollingTimer?.cancel();
    super.dispose();
  }

  // Inicia polling activo para detectar comandos rápidamente
  void _iniciarPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      _verificarComandosPendientes();
    });
  }

  // Verifica si hay comandos nuevos al abrir la app
  Future<void> _verificarComandosPendientes() async {
    try {
      final response = await Supabase.instance.client
          .from('recordings')
          .select()
          .order('created_at', ascending: false)
          .limit(1);

      if (response.isNotEmpty) {
        final ultimoComando = response[0];
        final id = ultimoComando['id'].toString();

        // Ejecutar si es nuevo
        if (_lastProcessedId == null || id != _lastProcessedId) {
          debugPrint("⚡ Comando pendiente detectado al iniciar");
          _ejecutarComandoAutomaticamente(ultimoComando);
          _lastProcessedId = id;
        }
      }
    } catch (e) {
      debugPrint("Error verificando comandos pendientes: $e");
    }
  }

  // --- LÓGICA DEL "MAYORDOMO" (Escucha y actúa) ---
  void _activarModoMayordomo() {
    debugPrint("🤖 VOID OS: Escuchando comandos...");

    _commandSubscription = Supabase.instance.client
        .from('recordings')
        .stream(primaryKey: ['id'])
        .order('created_at', ascending: false)
        .limit(1)
        .listen((List<Map<String, dynamic>> data) {
          if (data.isEmpty) return;

          final ultimoComando = data.first;
          final id = ultimoComando['id'].toString();

          // SI es un comando nuevo que no hemos ejecutado aún...
          if (_lastProcessedId != null && id != _lastProcessedId) {
            debugPrint(
              "⚡ NUEVO COMANDO DETECTADO: ${ultimoComando['summary']}",
            );
            _ejecutarComandoAutomaticamente(ultimoComando);
          }

          // Actualizamos el ID de referencia
          _lastProcessedId = id;
        });
  }

  void _ejecutarComandoAutomaticamente(Map<String, dynamic> memory) {
    // Pequeño delay para asegurar que la UI no bloquee la acción
    Future.delayed(const Duration(milliseconds: 500), () {
      try {
        final category = memory['category'] ?? 'NOTE';
        final entities = memory['entities'] ?? {};
        final summary = memory['summary'] ?? '';

        debugPrint('🎯 Procesando: $category');

        // Ejecutar acción según categoría
        switch (category) {
          case 'EMERGENCY':
            _actionHandler.sendWhatsApp('911', 'Emergencia: $summary');
            break;

          case 'TRANSPORT':
            final destination = entities['destination'] ?? entities['item'];
            if (destination != null) {
              _actionHandler.openUber(destination: destination);
            }
            break;

          case 'NAVIGATE':
            final place = entities['destination'] ?? entities['item'];
            if (place != null) {
              _actionHandler.openGoogleMaps(place);
            }
            break;

          case 'ORDER':
            final item = entities['item'];
            if (item != null) {
              _actionHandler.searchMercadoLibre(item);
            }
            break;

          case 'CALENDAR':
            _actionHandler.addCalendarEvent(summary);
            break;

          case 'NOTE':
            _actionHandler.createNote(summary);
            break;

          case 'MESSAGE':
            final contact = entities['contact'];
            if (contact != null) {
              // Aquí necesitarías mapear contactos a números
              _actionHandler.sendWhatsApp(contact, summary);
            }
            break;

          case 'QUERY':
            _actionHandler.searchGoogle(summary);
            break;

          default:
            // Fallback: intentar ejecutar como VoidCommand si tiene action_data
            final command = VoidCommand.fromJson(memory);
            if (command.actionData.url != null &&
                command.actionData.url!.isNotEmpty) {
              _actionHandler.executeCommand(command);
            } else {
              debugPrint('⚠️ Categoría no soportada: $category');
            }
        }
      } catch (e) {
        debugPrint('❌ Error al procesar comando: $e');
      }
    });
  }

  // --- UI (VISUALIZACIÓN) ---
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("VOID OS v1"),
        backgroundColor: Colors.black,
        elevation: 0,
        actions: [
          // Indicador visual de que está escuchando
          Container(
            margin: const EdgeInsets.all(15),
            width: 10,
            height: 10,
            decoration: const BoxDecoration(
              color: Colors.greenAccent,
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
      body: StreamBuilder<List<Map<String, dynamic>>>(
        stream: _uiStream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final memories = snapshot.data!;

          return ListView.builder(
            itemCount: memories.length,
            itemBuilder: (context, index) {
              final memory = memories[index];
              return _buildMemoryCard(memory);
            },
          );
        },
      ),
    );
  }

  Widget _buildMemoryCard(Map<String, dynamic> memory) {
    // Mantenemos tu diseño visual igual, es útil para ver el log
    final summary = memory['summary'] ?? '...';
    final category = memory['category'] ?? 'NOTE';

    Color cardColor = Colors.grey[900]!;
    if (category == 'EMERGENCY') cardColor = Colors.red[900]!;
    if (category == 'TRANSPORT') cardColor = Colors.blue[900]!;
    if (category == 'ORDER') cardColor = Colors.green[900]!;

    return Card(
      color: cardColor,
      margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      child: ListTile(
        title: Text(
          summary,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(category, style: const TextStyle(color: Colors.white70)),
      ),
    );
  }
}
