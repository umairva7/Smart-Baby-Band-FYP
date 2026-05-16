import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'core/theme/app_colors.dart';
import 'history.dart';
import 'notification.dart';
import 'settings.dart';
import 'navigation.dart';
import 'services/firestore_service.dart';
import 'globals.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Build page list inside build() so it can rebuild on state changes
    final pages = <Widget>[
      _DashboardContent(),
      const HistoryPage(),
      const NotificationsPage(),
      const SettingsPage(),
    ];

    return Scaffold(
      body: SafeArea(child: pages[_selectedIndex]),
      bottomNavigationBar: const AppBottomNav(currentIndex: 0),
    );
  }
}

/// Extracted dashboard content as a separate widget to keep things clean.
class _DashboardContent extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final user = FirebaseAuth.instance.currentUser;

    if (user == null) {
      return const Center(child: Text("Please log in again."));
    }

    return StreamBuilder<DocumentSnapshot>(
      stream: FirebaseFirestore.instance.collection('users').doc(user.uid).snapshots(),
      builder: (context, snapshot) {
        String babyName = '...';

        if (snapshot.hasData && snapshot.data != null && snapshot.data!.exists) {
          final data = snapshot.data!.data() as Map<String, dynamic>?;
          babyName = data?['baby_name'] ?? 'Baby';
        } else if (snapshot.hasError) {
          babyName = 'Error loading name';
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                'Dashboard',
                style: theme.textTheme.headlineMedium,
              ),
              const SizedBox(height: 16),

              // Baby info
              Column(
                children: [
                  Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        colors: [
                          colorScheme.primary.withValues(alpha: 0.15),
                          colorScheme.tertiary.withValues(alpha: 0.10),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                    child: Icon(
                      Icons.child_care_rounded,
                      size: 44,
                      color: colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    babyName,
                    style: theme.textTheme.headlineSmall,
                  ),
                  Text(
                    'Last sync: 5 minutes ago',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 28),

              // Cry Classification Section
              _buildSectionCard(
                context,
                title: 'Cry Classification',
                child: StreamBuilder<Map<String, dynamic>?>(
                  stream: FirestoreService.getCryClassifications(globalDeviceId),
                  builder: (context, crySnap) {
                    String cryType = 'unknown';
                    if (crySnap.hasData && crySnap.data != null) {
                      cryType = crySnap.data!['cry_label'] ?? 'unknown';
                    }
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _cryTypeCard(
                            context,
                            'images/hunger.jpg',
                            'Hunger',
                            cryType == 'hungry' ? AppColors.chartOrange : Colors.grey),
                        _cryTypeCard(
                            context,
                            'images/sleep.jpeg',
                            'Deep',
                            cryType == 'tired' ? AppColors.chartIndigo : Colors.grey), // tired = deep/sleepy
                        _cryTypeCard(
                            context,
                            'images/cry.jpeg',
                            'Pain',
                            cryType == 'discomfort' ? AppColors.chartRed : Colors.grey),
                      ],
                    );
                  },
                ),
              ),

              const SizedBox(height: 16),
              
              // Sleep State Section
              _buildSectionCard(
                context,
                title: 'Current Sleep State',
                child: StreamBuilder<List<Map<String, dynamic>>>(
                  stream: FirestoreService.getSleepSessions(globalDeviceId),
                  builder: (context, sleepSnap) {
                    String sleepState = 'Loading...';
                    if (sleepSnap.hasData && sleepSnap.data!.isNotEmpty) {
                      sleepState = sleepSnap.data!.first['sleep_state'] ?? 'awake';
                    } else if (sleepSnap.hasData && sleepSnap.data!.isEmpty) {
                      sleepState = 'No data';
                    }
                    return Center(
                      child: Text(
                        sleepState.toUpperCase(),
                        style: theme.textTheme.headlineSmall?.copyWith(
                          color: sleepState == 'deep' ? AppColors.chartIndigo : 
                                 sleepState == 'light' ? AppColors.chartBlue : AppColors.chartOrange,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 16),

              // Environment Temperature Section
              _buildSectionCard(
                context,
                title: 'Environment Temperature',
                child: StreamBuilder<List<Map<String, dynamic>>>(
                  stream: FirestoreService.getEnvironmentLogs(globalDeviceId),
                  builder: (context, envSnap) {
                    String temp = '--℃';
                    String hum = '--%';
                    Color tempColor = AppColors.chartBlue;
                    if (envSnap.hasData && envSnap.data!.isNotEmpty) {
                      final latest = envSnap.data!.first;
                      temp = '${latest['temperature']}℃';
                      hum = '${latest['humidity']}%';
                      if (latest['overall'] == 'danger') tempColor = AppColors.error;
                      else if (latest['overall'] == 'warning') tempColor = AppColors.chartOrange;
                      else tempColor = AppColors.chartTeal;
                    }
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _tempCard(context, temp, tempColor),
                        _tempCard(context, hum, AppColors.chartTeal),
                      ],
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionCard(
    BuildContext context, {
    required String title,
    required Widget child,
  }) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: colorScheme.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: theme.textTheme.titleMedium),
          const SizedBox(height: 15),
          child,
        ],
      ),
    );
  }

  Widget _cryTypeCard(
      BuildContext context, String image, String label, Color accentColor) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Container(
          height: 70,
          width: 70,
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: accentColor.withValues(alpha: 0.10),
            shape: BoxShape.circle,
            border: Border.all(
              color: accentColor.withValues(alpha: 0.25),
              width: 1.5,
            ),
          ),
          child: Image.asset(image),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _tempCard(BuildContext context, String value, Color accentColor) {
    final theme = Theme.of(context);

    return Container(
      width: 130,
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
      decoration: BoxDecoration(
        color: accentColor.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: accentColor.withValues(alpha: 0.20),
          width: 1,
        ),
      ),
      alignment: Alignment.center,
      child: Text(
        value,
        style: theme.textTheme.titleMedium?.copyWith(
          color: accentColor,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}
