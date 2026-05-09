import 'package:flutter/material.dart';
import 'core/theme/app_colors.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'main.dart';
import 'navigation.dart';
import 'login.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool _notifications = true;
  bool _vibration = true;
  bool _autoSync = true;
  bool _babyDataSharing = false;
  String _temperatureUnit = '°C';
  String _distanceUnit = 'km';
  String _selectedLanguage = 'English';
  double _alertVolume = 0.8;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = MyApp.themeProvider.isDarkMode;

    return Scaffold(
      appBar: AppBar(
        title: Text('Settings', style: theme.textTheme.headlineMedium),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Profile Section
          _buildProfileSection(theme, colorScheme),
          const SizedBox(height: 30),

          // Appearance
          _buildSectionTitle('Appearance', colorScheme),
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.dark_mode_rounded,
              title: 'Dark Mode',
              trailing: Switch(
                value: isDark,
                onChanged: (value) {
                  MyApp.themeProvider.toggleTheme(value);
                  setState(() {});
                },
              ),
            ),
          ]),
          const SizedBox(height: 20),

          // General Settings
          _buildSectionTitle('General Settings', colorScheme),
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.notifications_rounded,
              title: 'Push Notifications',
              trailing: Switch(
                value: _notifications,
                onChanged: (value) {
                  setState(() {
                    _notifications = value;
                  });
                },
              ),
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.volume_up_rounded,
              title: 'Alert Volume',
              subtitle: '${(_alertVolume * 100).toInt()}%',
              trailing: SizedBox(
                width: 120,
                child: Slider(
                  value: _alertVolume,
                  onChanged: (value) {
                    setState(() {
                      _alertVolume = value;
                    });
                  },
                  min: 0.0,
                  max: 1.0,
                  divisions: 10,
                ),
              ),
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.vibration_rounded,
              title: 'Vibration Alerts',
              trailing: Switch(
                value: _vibration,
                onChanged: (value) {
                  setState(() {
                    _vibration = value;
                  });
                },
              ),
            ),
          ]),
          const SizedBox(height: 20),

          // Baby Monitor Settings
          _buildSectionTitle('Baby Monitor Settings', colorScheme),
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.sync_rounded,
              title: 'Auto Sync Data',
              subtitle: 'Sync every 5 minutes',
              trailing: Switch(
                value: _autoSync,
                onChanged: (value) {
                  setState(() {
                    _autoSync = value;
                  });
                },
              ),
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.share_rounded,
              title: 'Share Baby Data',
              subtitle: 'With pediatrician',
              trailing: Switch(
                value: _babyDataSharing,
                onChanged: (value) {
                  setState(() {
                    _babyDataSharing = value;
                  });
                },
              ),
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.thermostat_rounded,
              title: 'Temperature Unit',
              subtitle: _temperatureUnit,
              trailing: DropdownButton<String>(
                value: _temperatureUnit,
                onChanged: (String? newValue) {
                  setState(() {
                    _temperatureUnit = newValue!;
                  });
                },
                items: <String>['°C', '°F']
                    .map<DropdownMenuItem<String>>((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                underline: Container(),
              ),
            ),
          ]),
          const SizedBox(height: 20),

          // Alert Settings
          _buildSectionTitle('Alert Settings', colorScheme),
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.warning_rounded,
              title: 'Critical Alerts',
              subtitle: 'Heart rate > 150 BPM',
              trailing: Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              onTap: () {
                _showAlertSettings('Critical Alerts');
              },
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.thermostat_rounded,
              title: 'Temperature Alerts',
              subtitle: 'Above 37.5°C',
              trailing: Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              onTap: () {
                _showAlertSettings('Temperature Alerts');
              },
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.mic_rounded,
              title: 'Cry Detection Sensitivity',
              subtitle: 'Medium',
              trailing: Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              onTap: () {
                _showAlertSettings('Cry Detection');
              },
            ),
          ]),
          const SizedBox(height: 20),

          // App Settings
          _buildSectionTitle('App Settings', colorScheme),
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.language_rounded,
              title: 'Language',
              subtitle: _selectedLanguage,
              trailing: DropdownButton<String>(
                value: _selectedLanguage,
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedLanguage = newValue!;
                  });
                },
                items: <String>['English', 'Spanish', 'French', 'German']
                    .map<DropdownMenuItem<String>>((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                underline: Container(),
              ),
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.straighten_rounded,
              title: 'Distance Unit',
              subtitle: _distanceUnit,
              trailing: DropdownButton<String>(
                value: _distanceUnit,
                onChanged: (String? newValue) {
                  setState(() {
                    _distanceUnit = newValue!;
                  });
                },
                items: <String>['km', 'mi']
                    .map<DropdownMenuItem<String>>((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                underline: Container(),
              ),
            ),
          ]),
          const SizedBox(height: 20),

          // Support Section
          _buildSectionTitle('Support', colorScheme),
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.help_outline_rounded,
              title: 'Help & Support',
              trailing: Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              onTap: () {
                // Navigate to help page
              },
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.privacy_tip_rounded,
              title: 'Privacy Policy',
              trailing: Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              onTap: () {
                // Show privacy policy
              },
            ),
            _buildDivider(theme),
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.description_rounded,
              title: 'Terms of Service',
              trailing: Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              onTap: () {
                // Show terms of service
              },
            ),
          ]),
          const SizedBox(height: 20),

          // About App
          _buildSettingCard(theme, [
            _buildSettingTile(
              theme: theme,
              colorScheme: colorScheme,
              icon: Icons.info_outline_rounded,
              title: 'About App',
              onTap: () {
                showAboutDialog(
                  context: context,
                  applicationName: 'Smart Baby Monitor',
                  applicationVersion: '1.2.0',
                  applicationIcon: Icon(
                    Icons.child_care_rounded,
                    color: colorScheme.primary,
                    size: 48,
                  ),
                  children: [
                    const SizedBox(height: 10),
                    const Text(
                      'Monitor your baby\'s health and well-being with real-time tracking of temperature, heart rate, and cry patterns.',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 15),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.star, color: Colors.amber[600], size: 16),
                        Icon(Icons.star, color: Colors.amber[600], size: 16),
                        Icon(Icons.star, color: Colors.amber[600], size: 16),
                        Icon(Icons.star, color: Colors.amber[600], size: 16),
                        Icon(Icons.star_half,
                            color: Colors.amber[600], size: 16),
                      ],
                    ),
                    const SizedBox(height: 10),
                    const Text('4.5 • 2.8K reviews'),
                  ],
                );
              },
            ),
          ]),
          const SizedBox(height: 30),

          // Logout Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                _showLogoutConfirmation();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.error.withValues(alpha: 0.1),
                foregroundColor: AppColors.error,
                elevation: 0,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Log Out',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 3),
    );
  }

  Widget _buildProfileSection(ThemeData theme, ColorScheme colorScheme) {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return const SizedBox.shrink();

    return StreamBuilder<DocumentSnapshot>(
      stream: FirebaseFirestore.instance.collection('users').doc(user.uid).snapshots(),
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return Center(
            child: Text(
              'Database Error: ${snapshot.error}',
              style: TextStyle(color: colorScheme.error),
            ),
          );
        }

        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Padding(
            padding: EdgeInsets.all(20),
            child: Center(child: CircularProgressIndicator()),
          );
        }

        final doc = snapshot.data;
        final userData = (doc != null && doc.exists) 
            ? doc.data() as Map<String, dynamic>? ?? {} 
            : {};
            
        final String parentName = userData['name'] ?? 'Parent';
        final String babyName = userData['baby_name'] ?? 'Baby';

        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: colorScheme.shadow,
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                  color: colorScheme.primary.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: colorScheme.primary.withValues(alpha: 0.3),
                    width: 2,
                  ),
                ),
                child: Icon(
                  Icons.person_rounded,
                  size: 35,
                  color: colorScheme.primary,
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      parentName,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      'Parent of $babyName',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Container(
                      padding:
                          const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: colorScheme.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        'Premium Plan',
                        style: theme.textTheme.labelMedium?.copyWith(
                          color: colorScheme.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: Icon(Icons.edit_outlined, color: colorScheme.primary),
                onPressed: () => _showEditProfileDialog(parentName, babyName),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionTitle(String title, ColorScheme colorScheme) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: colorScheme.primary,
        ),
      ),
    );
  }

  Widget _buildSettingCard(ThemeData theme, List<Widget> children) {
    final colorScheme = theme.colorScheme;

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: colorScheme.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: children,
      ),
    );
  }

  Widget _buildSettingTile({
    required ThemeData theme,
    required ColorScheme colorScheme,
    required IconData icon,
    required String title,
    String? subtitle,
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: colorScheme.primary.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(
          icon,
          color: colorScheme.primary,
          size: 22,
        ),
      ),
      title: Text(
        title,
        style: theme.textTheme.bodyLarge?.copyWith(
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle,
              style: theme.textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            )
          : null,
      trailing: trailing ??
          Icon(
            Icons.arrow_forward_ios,
            size: 16,
            color: colorScheme.onSurfaceVariant,
          ),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    );
  }

  Widget _buildDivider(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.only(left: 72.0, right: 16.0),
      child: Divider(
        height: 1,
        color: theme.dividerColor,
      ),
    );
  }

  void _showAlertSettings(String title) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(title),
          content: const Text(
              'Alert settings customization will be available in the next update.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  void _showLogoutConfirmation() {
    final colorScheme = Theme.of(context).colorScheme;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text(
            'Log Out',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          content: const Text('Are you sure you want to log out?'),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(
                'Cancel',
                style: TextStyle(color: colorScheme.onSurfaceVariant),
              ),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.of(context).pop(); // close the dialog
                
                try {
                  final user = FirebaseAuth.instance.currentUser;
                  if (user != null) {
                    // 1. Delete the FCM token so this device stops receiving push notifications
                    await FirebaseFirestore.instance.collection('users').doc(user.uid).update({
                      'fcm_token': FieldValue.delete(),
                    });
                    
                    // 2. Sign out of Firebase
                    await FirebaseAuth.instance.signOut();
                  }
                  
                  if (context.mounted) {
                    // 3. Navigate back to the Login Page and clear navigation history
                    Navigator.of(context).pushAndRemoveUntil(
                      MaterialPageRoute(builder: (context) => const LoginPage()),
                      (Route<dynamic> route) => false,
                    );
                    
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Logged out successfully'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error logging out: $e')),
                    );
                  }
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.error,
                foregroundColor: Colors.white,
              ),
              child: const Text('Log Out'),
            ),
          ],
        );
      },
    );
  }

  void _showEditProfileDialog(String currentName, String currentBabyName) {
    final nameController = TextEditingController(text: currentName);
    final babyNameController = TextEditingController(text: currentBabyName);

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Edit Profile', style: TextStyle(fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: 'Parent Name'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: babyNameController,
                decoration: const InputDecoration(labelText: 'Baby Name'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                final user = FirebaseAuth.instance.currentUser;
                if (user != null) {
                  await FirebaseFirestore.instance.collection('users').doc(user.uid).update({
                    'name': nameController.text.trim(),
                    'baby_name': babyNameController.text.trim(),
                  });
                }
                if (context.mounted) Navigator.pop(context);
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    );
  }
}

