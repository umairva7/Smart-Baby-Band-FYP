import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class SleepPage extends StatelessWidget {
  const SleepPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Sleep Summary
            _buildSleepSummary(),
            const SizedBox(height: 20),

            // Sleep Chart
            _buildSleepChart(),
            const SizedBox(height: 20),

            // Sleep Stages
            _buildSleepStages(),
            const SizedBox(height: 20),

            // Sleep Statistics
            _buildSleepStats(),
          ],
        ),
      ),
    );
  }

  Widget _buildSleepSummary() {
    return Card(
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
                  'Last Night\'s Sleep',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 5),
                const Text(
                  '8h 24m',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.indigo,
                  ),
                ),
                const SizedBox(height: 5),
                Row(
                  children: [
                    Icon(Icons.check_circle,
                        color: Colors.green[400], size: 16),
                    const SizedBox(width: 5),
                    const Text(
                      'Good Sleep Quality',
                      style: TextStyle(color: Colors.green),
                    ),
                  ],
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.indigo.withOpacity(0.1),
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
    );
  }

  Widget _buildSleepChart() {
    final List<FlSpot> sleepData = [
      const FlSpot(0, 0), // 9PM
      const FlSpot(1, 10), // 10PM
      const FlSpot(2, 85), // 11PM (Deep Sleep)
      const FlSpot(3, 90), // 12AM (Deep Sleep)
      const FlSpot(4, 95), // 1AM (Deep Sleep)
      const FlSpot(5, 60), // 2AM (Light Sleep)
      const FlSpot(6, 40), // 3AM (Light Sleep)
      const FlSpot(7, 80), // 4AM (Deep Sleep)
      const FlSpot(8, 70), // 5AM (REM)
      const FlSpot(9, 30), // 6AM (Light Sleep)
      const FlSpot(10, 0), // 7AM (Awake)
    ];

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sleep Pattern',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: true,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(
                        color: Colors.grey[300]!,
                        strokeWidth: 1,
                      );
                    },
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
                        getTitlesWidget: (value, meta) {
                          List<String> times = [
                            '9PM',
                            '11PM',
                            '1AM',
                            '3AM',
                            '5AM',
                            '7AM'
                          ];
                          int index = value.toInt();
                          return index >= 0 && index < times.length
                              ? Padding(
                                  padding: const EdgeInsets.only(top: 8.0),
                                  child: Text(times[index]),
                                )
                              : const SizedBox();
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          if (value == 0) return const Text('Awake');
                          if (value == 50) return const Text('Light');
                          if (value == 100) return const Text('Deep');
                          return const SizedBox();
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border.all(color: Colors.grey[300]!),
                  ),
                  minX: 0,
                  maxX: 10,
                  minY: 0,
                  maxY: 100,
                  lineBarsData: [
                    LineChartBarData(
                      spots: sleepData,
                      isCurved: true,
                      color: Colors.indigo,
                      barWidth: 3,
                      isStrokeCapRound: true,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.indigo.withOpacity(0.3),
                            Colors.indigo.withOpacity(0.1),
                          ],
                        ),
                      ),
                      dotData: const FlDotData(show: false),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Sleep Depth', style: TextStyle(color: Colors.grey)),
                Text('Time', style: TextStyle(color: Colors.grey)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSleepStages() {
    final Map<String, Map<String, dynamic>> stages = {
      'Deep Sleep': {
        'duration': '3h 45m',
        'percentage': 45,
        'color': Colors.indigo
      },
      'Light Sleep': {
        'duration': '3h 15m',
        'percentage': 39,
        'color': Colors.blue
      },
      'REM Sleep': {
        'duration': '1h 24m',
        'percentage': 16,
        'color': Colors.purple
      },
    };

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sleep Stages',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Column(
              children: stages.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 12,
                                height: 12,
                                decoration: BoxDecoration(
                                  color: entry.value['color'] as Color,
                                  borderRadius: BorderRadius.circular(3),
                                ),
                              ),
                              const SizedBox(width: 10),
                              Text(entry.key),
                            ],
                          ),
                          Text(
                              '${entry.value['duration']} (${entry.value['percentage']}%)'),
                        ],
                      ),
                      const SizedBox(height: 5),
                      LinearProgressIndicator(
                        value: (entry.value['percentage'] as int) / 100,
                        backgroundColor: Colors.grey[200],
                        color: entry.value['color'] as Color,
                        minHeight: 6,
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSleepStats() {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Weekly Sleep Statistics',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildStatItem(
                    'Avg Sleep', '8.2h', Icons.nights_stay, Colors.indigo),
                _buildStatItem(
                    'Bed Time', '9:45 PM', Icons.schedule, Colors.blue),
                _buildStatItem(
                    'Wake Time', '6:15 AM', Icons.wb_sunny, Colors.orange),
              ],
            ),
            const SizedBox(height: 15),
            const Divider(),
            const SizedBox(height: 10),
            const Text(
              'Sleep Quality: 82/100',
              style: TextStyle(color: Colors.green),
            ),
            const SizedBox(height: 5),
            LinearProgressIndicator(
              value: 0.82,
              backgroundColor: Colors.grey[200],
              color: Colors.green,
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(
      String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }
}
