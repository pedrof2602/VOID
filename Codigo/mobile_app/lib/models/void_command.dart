/// Categorías de comandos soportados por VOID OS
enum CommandCategory {
  order,
  transport,
  emergency,
  search;

  static CommandCategory fromString(String value) {
    switch (value.toUpperCase()) {
      case 'ORDER':
        return CommandCategory.order;
      case 'TRANSPORT':
        return CommandCategory.transport;
      case 'EMERGENCY':
        return CommandCategory.emergency;
      case 'SEARCH':
        return CommandCategory.search;
      default:
        return CommandCategory.search;
    }
  }

  String toJson() => name.toUpperCase();
}

/// Datos de acción asociados a un comando
class ActionData {
  final String? url;
  final String? query;

  const ActionData({this.url, this.query});

  factory ActionData.fromJson(Map<String, dynamic> json) {
    return ActionData(
      url: json['url'] as String?,
      query: json['query'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {'url': url, 'query': query};
  }
}

/// Modelo de comando VOID
class VoidCommand {
  final String id;
  final CommandCategory category;
  final ActionData actionData;
  final String summary;
  final DateTime createdAt;

  const VoidCommand({
    required this.id,
    required this.category,
    required this.actionData,
    required this.summary,
    required this.createdAt,
  });

  factory VoidCommand.fromJson(Map<String, dynamic> json) {
    return VoidCommand(
      id: json['id'].toString(),
      category: CommandCategory.fromString(
        json['category'] as String? ?? 'SEARCH',
      ),
      actionData: ActionData.fromJson(
        json['action_data'] as Map<String, dynamic>? ?? {},
      ),
      summary: json['summary'] as String? ?? 'Sin descripción',
      createdAt: DateTime.parse(
        json['created_at'] as String? ?? DateTime.now().toIso8601String(),
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'category': category.toJson(),
      'action_data': actionData.toJson(),
      'summary': summary,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
