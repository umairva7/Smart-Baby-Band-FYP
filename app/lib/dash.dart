import 'package:flutter/material.dart';
import 'history.dart';
import 'notification.dart';
import 'settings.dart';
import 'navigation.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int _selectedIndex = 0;

  // List of pages for bottom navigation
  final List<Widget> _pages = [];

  @override
  void initState() {
    super.initState();
    _pages.addAll([
      _buildDashboardUI(), // first tab is the dashboard itself
      const HistoryPage(),
      const NotificationsPage(),
      const SettingsPage(),
    ]);
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  Widget _buildDashboardUI() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const Text(
            'Dashboard',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 10),

          // Baby info
          Column(
            children: [
              const CircleAvatar(
                radius: 45,
                backgroundColor: Colors.white,
                backgroundImage: NetworkImage(
                  'https://d1iiooxwdowqwr.cloudfront.net/pub/appsubmissions/20170824171043_Iconfinal.jpg',
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Emma',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  color: Colors.black,
                ),
              ),
              const Text(
                'Last sync: 5 minutes ago',
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
            ],
          ),

          const SizedBox(height: 30),

          // Cry Classification Section
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Cry Classification',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 15),

                // Row of 3 Cry Types
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _cryTypeCard('assets/images/hunger.png', 'Hunger'),
                    _cryTypeCard('assets/images/sleep.png', 'Deep'),
                    _cryTypeCard('assets/images/cry.png', 'Pain'),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 25),

          // Environment Temperature Section
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Environment Temperature',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _tempCard('22.5℃', Colors.blue.shade50),
                    _tempCard('150tm', Colors.red.shade50),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // Helper widgets imagesss
  static Widget _cryTypeCard(String image, String label) {
    return Column(
      children: [
        Container(
          height: 70,
          width: 70,
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 6,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Image.asset(image),
        ),
        const SizedBox(height: 5),
        Text(label, style: const TextStyle(fontSize: 14)),
      ],
    );
  }

  static Widget _tempCard(String value, Color bgColor) {
    return Container(
      width: 120,
      padding: const EdgeInsets.symmetric(vertical: 20),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(15),
      ),
      alignment: Alignment.center,
      child: Text(
        value,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: Colors.black87,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5FBFF),
      body: SafeArea(child: _pages[_selectedIndex]),
      bottomNavigationBar: const AppBottomNav(currentIndex: 0),
    );
  }
}
