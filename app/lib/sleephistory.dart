import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'services/firestore_service.dart';
import 'globals.dart';

class SleepPage extends StatelessWidget {
  const SleepPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: StreamBuilder<List<Map<String, dynamic>>>(
        stream: FirestoreService.getSleepSessions(globalDeviceId),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Text('Error loading data: ${snapshot.error}');
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Text('No data yet');
          }

          final data = snapshot.data!;
          final latest = data.first;
          final state = latest['sleep_state'] ?? 'awake';

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Real-Time Sleep Summary
              Card(
                elevation: 3,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Current Sleep State',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
                          ),
                          const SizedBox(height: 5),
                          Text(
                            state.toString().toUpperCase(),
                            style: TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: state == 'deep' ? Colors.indigo : (state == 'light' ? Colors.blue : Colors.orange),
                            ),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.indigo.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.nights_stay,
                          color: Colors.indigo,
                          size: 40,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Recent Sleep Log
              const Text(
                'Recent Sleep Logs',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Column(
                children: data.map((session) {
                  final sState = session['sleep_state'] ?? 'awake';
                  
                  String timeStr = '--:--';
                  final ts = session['timestamp'];
                  if (ts != null) {
                    DateTime dt;
                    if (ts is int) {
                      dt = DateTime.fromMillisecondsSinceEpoch(ts);
                    } else {
                      dt = ts.toDate();
                    }
                    timeStr = '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
                  }

                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    child: ListTile(
                      leading: Icon(
                        Icons.bed, 
                        color: sState == 'deep' ? Colors.indigo : (sState == 'light' ? Colors.blue : Colors.orange)
                      ),
                      title: Text(sState.toString().toUpperCase(), style: const TextStyle(fontWeight: FontWeight.bold)),
                      trailing: Text(timeStr),
                    ),
                  );
                }).toList(),
              ),
            ],
          );
        },
      ),
    );
  }
}
