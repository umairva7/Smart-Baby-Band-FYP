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
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text("History", style: theme.textTheme.headlineMedium),
        bottom: TabBar(
          controller: _tabController,
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
