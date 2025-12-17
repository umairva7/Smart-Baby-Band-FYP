import 'package:flutter/material.dart';
import 'navigation.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool _notifications = true;
  bool _soundAlerts = true;
  bool _vibration = true;
  bool _autoSync = true;
  bool _babyDataSharing = false;
  String _temperatureUnit = '°C';
  String _distanceUnit = 'km';
  String _selectedLanguage = 'English';
  double _alertVolume = 0.8;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5FBFF),
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: Colors.white,
        centerTitle: true,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Profile Section
          _buildProfileSection(),
          const SizedBox(height: 30),

          // General Settings
          _buildSectionTitle('General Settings'),
          _buildSettingCard([
            _buildSettingTile(
              icon: Icons.notifications,
              title: 'Push Notifications',
              trailing: Switch(
                value: _notifications,
                onChanged: (value) {
                  setState(() {
                    _notifications = value;
                  });
                },
                activeColor: const Color(0xFF3BB9FF),
              ),
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.volume_up,
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
                  activeColor: const Color(0xFF3BB9FF),
                ),
              ),
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.vibration,
              title: 'Vibration Alerts',
              trailing: Switch(
                value: _vibration,
                onChanged: (value) {
                  setState(() {
                    _vibration = value;
                  });
                },
                activeColor: const Color(0xFF3BB9FF),
              ),
            ),
          ]),
          const SizedBox(height: 20),

          // Baby Monitor Settings
          _buildSectionTitle('Baby Monitor Settings'),
          _buildSettingCard([
            _buildSettingTile(
              icon: Icons.sync,
              title: 'Auto Sync Data',
              subtitle: 'Sync every 5 minutes',
              trailing: Switch(
                value: _autoSync,
                onChanged: (value) {
                  setState(() {
                    _autoSync = value;
                  });
                },
                activeColor: const Color(0xFF3BB9FF),
              ),
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.share,
              title: 'Share Baby Data',
              subtitle: 'With pediatrician',
              trailing: Switch(
                value: _babyDataSharing,
                onChanged: (value) {
                  setState(() {
                    _babyDataSharing = value;
                  });
                },
                activeColor: const Color(0xFF3BB9FF),
              ),
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.thermostat,
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
          _buildSectionTitle('Alert Settings'),
          _buildSettingCard([
            _buildSettingTile(
              icon: Icons.warning,
              title: 'Critical Alerts',
              subtitle: 'Heart rate > 150 BPM',
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                _showAlertSettings('Critical Alerts');
              },
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.thermostat,
              title: 'Temperature Alerts',
              subtitle: 'Above 37.5°C',
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                _showAlertSettings('Temperature Alerts');
              },
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.mic,
              title: 'Cry Detection Sensitivity',
              subtitle: 'Medium',
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                _showAlertSettings('Cry Detection');
              },
            ),
          ]),
          const SizedBox(height: 20),

          // App Settings
          _buildSectionTitle('App Settings'),
          _buildSettingCard([
            _buildSettingTile(
              icon: Icons.language,
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
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.straighten,
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
          _buildSectionTitle('Support'),
          _buildSettingCard([
            _buildSettingTile(
              icon: Icons.help_outline,
              title: 'Help & Support',
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                // Navigate to help page
              },
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.privacy_tip,
              title: 'Privacy Policy',
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                // Show privacy policy
              },
            ),
            _buildDivider(),
            _buildSettingTile(
              icon: Icons.description,
              title: 'Terms of Service',
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                // Show terms of service
              },
            ),
          ]),
          const SizedBox(height: 20),

          // About App
          _buildSettingCard([
            _buildSettingTile(
              icon: Icons.info_outline,
              title: 'About App',
              onTap: () {
                showAboutDialog(
                  context: context,
                  applicationName: 'Smart Baby Monitor',
                  applicationVersion: '1.2.0',
                  applicationIcon: const Icon(
                    Icons.child_care,
                    color: Color(0xFF3BB9FF),
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
                backgroundColor: Colors.red.withOpacity(0.1),
                foregroundColor: Colors.red,
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

  Widget _buildProfileSection() {
    return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
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
                color: const Color(0xFF3BB9FF).withOpacity(0.1),
                shape: BoxShape.circle,
                border: Border.all(
                  color: const Color(0xFF3BB9FF).withOpacity(0.3),
                  width: 2,
                ),
              ),
              child: const Icon(
                Icons.person,
                size: 35,
                color: Color(0xFF3BB9FF),
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'John & Sarah',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    'Parents of Emma',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFF3BB9FF).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Text(
                      'Premium Plan',
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF3BB9FF),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.edit_outlined, color: Color(0xFF3BB9FF)),
              onPressed: () {
                // Navigate to edit profile
              },
            ),
          ],
        ));
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
        padding: const EdgeInsets.only(bottom: 12.0),
        child: Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Color(0xFF3BB9FF),
          ),
        ));
  }

  Widget _buildSettingCard(List<Widget> children) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
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
          color: const Color(0xFF3BB9FF).withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(
          icon,
          color: const Color(0xFF3BB9FF),
          size: 22,
        ),
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          color: Colors.black,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey[600],
              ),
            )
          : null,
      trailing: trailing ??
          const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    );
  }

  Widget _buildDivider() {
    return Padding(
      padding: const EdgeInsets.only(left: 72.0, right: 16.0),
      child: Divider(
        height: 1,
        color: Colors.grey[300],
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
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Add your logout logic here
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Logged out successfully'),
                    duration: Duration(seconds: 2),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              child: const Text('Log Out'),
            ),
          ],
        );
      },
    );
  }
}
