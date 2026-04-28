import 'package:flutter/material.dart';

/// Centralized color palette for the Smart Baby Band app.
/// All colors in the app should reference this file — never hardcode colors.
class AppColors {
  AppColors._(); // Prevent instantiation

  // ─── Brand Primary (Calming Sky Blue) ───
  static const Color primaryLight = Color(0xFF4AADE8);
  static const Color primary = Color(0xFF2196F3);
  static const Color primaryDark = Color(0xFF1976D2);

  // ─── Brand Secondary (Warm Coral) ───
  static const Color secondaryLight = Color(0xFFFF9E80);
  static const Color secondary = Color(0xFFFF6E40);
  static const Color secondaryDark = Color(0xFFE64A19);

  // ─── Brand Tertiary (Soft Lavender) ───
  static const Color tertiary = Color(0xFF9C7CF4);
  static const Color tertiaryLight = Color(0xFFB9A0F8);

  // ─── Semantic Colors ───
  static const Color success = Color(0xFF4CAF50);
  static const Color successLight = Color(0xFFE8F5E9);
  static const Color warning = Color(0xFFFFA726);
  static const Color warningLight = Color(0xFFFFF3E0);
  static const Color error = Color(0xFFEF5350);
  static const Color errorLight = Color(0xFFFFEBEE);
  static const Color info = Color(0xFF42A5F5);
  static const Color infoLight = Color(0xFFE3F2FD);

  // ─── Light Theme Surface Colors ───
  static const Color lightBackground = Color(0xFFF4F7FB);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightSurfaceVariant = Color(0xFFF0F4F8);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightDivider = Color(0xFFE8ECF0);

  // ─── Light Theme Text Colors ───
  static const Color lightTextPrimary = Color(0xFF1A1D26);
  static const Color lightTextSecondary = Color(0xFF5A6072);
  static const Color lightTextTertiary = Color(0xFF8E95A9);
  static const Color lightTextOnPrimary = Color(0xFFFFFFFF);

  // ─── Dark Theme Surface Colors ───
  static const Color darkBackground = Color(0xFF0F1119);
  static const Color darkSurface = Color(0xFF1A1D2E);
  static const Color darkSurfaceVariant = Color(0xFF222639);
  static const Color darkCard = Color(0xFF1E2235);
  static const Color darkDivider = Color(0xFF2E3347);

  // ─── Dark Theme Text Colors ───
  static const Color darkTextPrimary = Color(0xFFECEFF4);
  static const Color darkTextSecondary = Color(0xFFA0A8BE);
  static const Color darkTextTertiary = Color(0xFF6B7394);
  static const Color darkTextOnPrimary = Color(0xFFFFFFFF);

  // ─── Chart / Data Visualization Colors ───
  static const Color chartBlue = Color(0xFF42A5F5);
  static const Color chartPurple = Color(0xFF9C7CF4);
  static const Color chartOrange = Color(0xFFFF9800);
  static const Color chartGreen = Color(0xFF66BB6A);
  static const Color chartRed = Color(0xFFEF5350);
  static const Color chartIndigo = Color(0xFF5C6BC0);
  static const Color chartTeal = Color(0xFF26A69A);

  // ─── Baby-specific Semantic Colors ───
  static const Color heartRate = Color(0xFFEF5350);
  static const Color heartRateBg = Color(0xFFFFEBEE);
  static const Color temperature = Color(0xFFFF9800);
  static const Color temperatureBg = Color(0xFFFFF3E0);
  static const Color sleep = Color(0xFF5C6BC0);
  static const Color sleepBg = Color(0xFFE8EAF6);
  static const Color cry = Color(0xFF9C7CF4);
  static const Color cryBg = Color(0xFFF3E5F5);

  // ─── Gradient Presets ───
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF42A5F5), Color(0xFF1E88E5)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient accentGradient = LinearGradient(
    colors: [Color(0xFF9C7CF4), Color(0xFF6C5CE7)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient warmGradient = LinearGradient(
    colors: [Color(0xFFFF9E80), Color(0xFFFF6E40)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient darkCardGradient = LinearGradient(
    colors: [Color(0xFF1E2235), Color(0xFF252A40)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
