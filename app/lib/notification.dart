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

    return Scaffold(
      body: SafeArea(
        child: globalDeviceId.isEmpty 
          ? const Center(child: Text('Device not linked. Please configure a baby profile.'))
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
              return Center(child: Text('Error loading alerts: ${snapshot.error}'));
            }

            if (!snapshot.hasData || snapshot.data == null) {
              return const Center(child: Text('No active alerts. Everything is fine.'));
            }

            final alert = snapshot.data!;
            final type = alert['alert_type'] ?? 'Unknown';
            final temp = alert['temperature']?.toString() ?? '--';
            final hum = alert['humidity']?.toString() ?? '--';

            return Center(
              child: Container(
                width: 280,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: colorScheme.surface,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: colorScheme.shadow,
                      blurRadius: 12,
                      offset: const Offset(0, 4),
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
                      child: ElevatedButton.icon(
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
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.error,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
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
