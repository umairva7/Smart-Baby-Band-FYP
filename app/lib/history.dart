import 'package:flutter/material.dart';
import 'navigation.dart';
import 'cryhistory.dart';
import 'sleephistory.dart';
import 'tempraturehistory.dart';
import 'heartratehistory.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5FBFF),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          "History",
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.black,
          unselectedLabelColor: Colors.grey,
          indicatorColor: const Color(0xFF3BB9FF),
          tabs: const [
            Tab(text: "Cry"),
            Tab(text: "Sleep"),
            Tab(text: "Temperature"),
            Tab(text: "Heartbeat"),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          CryPage(),
          SleepPage(),
          TemperaturePage(),
          HeartbeatPage(),
        ],
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 1),
    );
  }
}
