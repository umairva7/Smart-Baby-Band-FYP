import 'package:flutter/material.dart';

/// Manages app-wide theme mode (light / dark / system).
///
/// Wrap your [MaterialApp] with a [ListenableBuilder] or use a
/// state-management solution to react to changes.
class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;

  ThemeMode get themeMode => _themeMode;

  bool get isDarkMode => _themeMode == ThemeMode.dark;

  /// Toggle between light and dark mode.
  void toggleTheme(bool enableDark) {
    _themeMode = enableDark ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
  }

  /// Set a specific theme mode.
  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    notifyListeners();
  }
}
