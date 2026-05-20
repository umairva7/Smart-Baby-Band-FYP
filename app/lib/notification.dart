import 'package:flutter/material.dart';
import 'core/theme/app_colors.dart';
import 'navigation.dart';
import 'services/api_service.dart';
import 'globals.dart';

class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text('Notifications', style: theme.textTheme.headlineMedium),
      ),
      body: SafeArea(
        child: globalDeviceId.isEmpty 
          ? FutureBuilder(
              future: loadDeviceId(),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (globalDeviceId.isEmpty) {
                  return Center(
                    child: Text(
                      'Device not linked. Please configure a baby profile.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  );
                }
                // Device ID recovered — rebuild the whole widget
                return build(context);
              },
            )
          : StreamBuilder<Map<String, dynamic>?>(
          // Simple poll stream since it's an HTTP GET endpoint
          stream: Stream.periodic(const Duration(seconds: 5))
              .asyncMap((_) => ApiService.getAlerts(globalDeviceId))
              .map((alerts) => (alerts != null && alerts.isNotEmpty) ? alerts : null),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'Error loading alerts: ${snapshot.error}',
                  style: theme.textTheme.bodyMedium,
                ),
              );
            }

            if (!snapshot.hasData || snapshot.data == null) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.check_circle_outline_rounded,
                      size: 64,
                      color: AppColors.success.withValues(alpha: 0.6),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'All Clear',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        color: AppColors.success,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'No active alerts. Everything is fine.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              );
            }

            final alert = snapshot.data!;
            final type = alert['alert_type'] ?? 'Unknown';
            final temp = alert['temperature']?.toString() ?? '--';
            final hum = alert['humidity']?.toString() ?? '--';

            return Center(
              child: Container(
                width: 300,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: isDark
                      ? AppColors.darkCardGradient
                      : const LinearGradient(
                          colors: [Colors.white, Color(0xFFFFF5F5)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.error.withValues(alpha: 0.15),
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.error.withValues(alpha: isDark ? 0.10 : 0.08),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Emergency Alert',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 18),
                    Container(
                      height: 72,
                      width: 72,
                      decoration: BoxDecoration(
                        color: AppColors.heartRateBg,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: AppColors.error.withValues(alpha: 0.2),
                          width: 2,
                        ),
                      ),
                      child: const Icon(
                        Icons.warning_rounded,
                        color: AppColors.heartRate,
                        size: 40,
                      ),
                    ),
                    const SizedBox(height: 15),
                    Text(
                      type.replaceAll('_', ' ').toUpperCase(),
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                    Text(
                      'Temp: $temp℃\nHum: $hum%',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    Text(
                      'Danger Detected',
                      style: theme.textTheme.titleSmall?.copyWith(
                        color: AppColors.error,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 22),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Calling Doctor...'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                        icon: const Icon(Icons.phone_rounded, size: 20),
                        label: const Text('Call Doctor'),
                        style: FilledButton.styleFrom(
                          backgroundColor: AppColors.error,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),

      // navigation bar should be OUTSIDE the body
      bottomNavigationBar: const AppBottomNav(currentIndex: 2),
    );
  }
}
