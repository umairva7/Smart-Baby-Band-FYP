import 'package:flutter/material.dart';
import 'navigation.dart';

class HistoryPage extends StatelessWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5FBFF),
      appBar: AppBar(
        title: const Text('History'),
        backgroundColor: const Color(0xFF3BB9FF),
        centerTitle: true,
      ),
      body: const Center(
        child: Text(
          'No history data available yet!',
          style: TextStyle(fontSize: 18, color: Colors.grey),
        ),
      ),

      // navigation bar at the bottom
      bottomNavigationBar: const AppBottomNav(currentIndex: 1),
    );
  }
}
