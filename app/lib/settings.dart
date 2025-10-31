import 'package:flutter/material.dart';
import 'navigation.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5FBFF),
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: const Color(0xFF3BB9FF),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'General Settings',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          SwitchListTile(
            title: const Text('Notifications'),
            value: true,
            onChanged: (value) {},
          ),
          SwitchListTile(
            title: const Text('Dark Mode'),
            value: false,
            onChanged: (value) {},
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About App'),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'Smart Baby Band',
                applicationVersion: '1.0.0',
                applicationIcon: const Icon(Icons.child_care),
                children: const [
                  Text('This app monitors baby cry patterns and environment.'),
                ],
              );
            },
          ),
        ],
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 3),
    );
  }
}
