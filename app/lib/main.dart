import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'theme_provider.dart';
import 'login.dart';
import 'dash.dart';
import 'history.dart';
import 'notification.dart';
import 'settings.dart';

/// Global [ThemeProvider] instance shared across the app.
/// Screens can access it via [MyApp.themeProvider].
final ThemeProvider _themeProvider = ThemeProvider();

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  /// Public accessor so any screen can toggle the theme
  /// via `MyApp.themeProvider.toggleTheme(...)`.
  static ThemeProvider get themeProvider => _themeProvider;

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _themeProvider,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Smart Baby Band',
          themeMode: _themeProvider.themeMode,
          theme: AppTheme.light,
          darkTheme: AppTheme.dark,
          initialRoute: '/login',
          routes: {
            '/login': (context) => const LoginPage(),
            '/dashboard': (context) => const DashboardPage(),
            '/history': (context) => const HistoryPage(),
            '/notifications': (context) => const NotificationsPage(),
            '/settings': (context) => const SettingsPage(),
          },
        );
      },
    );
  }
}
