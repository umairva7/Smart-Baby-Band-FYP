import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class HeartbeatPage extends StatelessWidget {
  const HeartbeatPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Heart Rate with Live Animation
            _buildHeartRateLive(),
            const SizedBox(height: 20),

            // Sparkline Mini Charts
            _buildSparklineCharts(),
            const SizedBox(height: 20),

            // Heart Rate Distribution (Bar Chart)
            _buildHeartRateDistribution(),
            const SizedBox(height: 20),

            // Heart Rate Zones (Pie Chart)
            _buildHeartRateZones(),
            const SizedBox(height: 20),

            // Detailed Statistics
            _buildDetailedStats(),
        ],
      ),
    );
  }

  Widget _buildHeartRateLive() {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'Live Heart Rate',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),

            Stack(
              alignment: Alignment.center,
              children: [
                // Pulsing Circle Animation
                Container(
                  width: 150,
                  height: 150,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.red.withValues(alpha: 0.1),
                  ),
                  child: Center(
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.red.withValues(alpha: 0.2),
                      ),
                      child: Center(
                        child: Container(
                          width: 90,
                          height: 90,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.red.withValues(alpha: 0.3),
                          ),
                          child: Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  crossAxisAlignment:
                                      CrossAxisAlignment.baseline,
                                  textBaseline: TextBaseline.alphabetic,
                                  children: [
                                    Text(
                                      '128',
                                      style: const TextStyle(
                                        fontSize: 36,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.red,
                                      ),
                                    ),
                                    const SizedBox(width: 5),
                                    const Text(
                                      'BPM',
                                      style: TextStyle(
                                        fontSize: 16,
                                        color: Colors.red,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 5),
                                const Text(
                                  'Normal',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.green,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),

                // Heart Icon with Beat Animation
                const Icon(
                  Icons.favorite,
                  color: Colors.red,
                  size: 40,
                ),
              ],
            ),

            const SizedBox(height: 15),

            // Heart Rate Trend Line
            SizedBox(
              height: 40,
              child: LineChart(
                LineChartData(
                  gridData: const FlGridData(show: false),
                  titlesData: const FlTitlesData(show: false),
                  borderData: FlBorderData(show: false),
                  minX: 0,
                  maxX: 10,
                  minY: 120,
                  maxY: 140,
                  lineBarsData: [
                    LineChartBarData(
                      spots: const [
                        FlSpot(0, 125),
                        FlSpot(2, 130),
                        FlSpot(4, 128),
                        FlSpot(6, 132),
                        FlSpot(8, 128),
                        FlSpot(10, 125),
                      ],
                      isCurved: true,
                      color: Colors.red,
                      barWidth: 2,
                      dotData: const FlDotData(show: false),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 10),
            const Text(
              'Last 10 minutes trend',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSparklineCharts() {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Heart Rate Patterns',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildMiniSparkline(
                    'Morning', [120, 125, 128, 130, 125], Colors.blue),
                _buildMiniSparkline(
                    'Afternoon', [130, 135, 132, 128, 130], Colors.orange),
                _buildMiniSparkline(
                    'Evening', [125, 128, 130, 132, 128], Colors.purple),
                _buildMiniSparkline(
                    'Night', [120, 118, 115, 118, 120], Colors.indigo),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniSparkline(String label, List<int> data, Color color) {
    return Column(
      children: [
        SizedBox(
          width: 70,
          height: 40,
          child: LineChart(
            LineChartData(
              gridData: const FlGridData(show: false),
              titlesData: const FlTitlesData(show: false),
              borderData: FlBorderData(show: false),
              minX: 0,
              maxX: data.length.toDouble() - 1,
              minY: data.reduce((a, b) => a < b ? a : b).toDouble() - 5,
              maxY: data.reduce((a, b) => a > b ? a : b).toDouble() + 5,
              lineBarsData: [
                LineChartBarData(
                  spots: List.generate(
                      data.length,
                      (index) =>
                          FlSpot(index.toDouble(), data[index].toDouble())),
                  isCurved: true,
                  color: color,
                  barWidth: 1.5,
                  dotData: const FlDotData(show: false),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 5),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
        Text(
          '${data.last} BPM',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildHeartRateDistribution() {
    final List<double> hrData = [
      120,
      125,
      130,
      135,
      128,
      132,
      125,
      130,
      128,
      122
    ];
    final Map<int, int> frequency = {};

    for (var hr in hrData) {
      int rounded = (hr ~/ 5) * 5; // Group by 5 BPM intervals
      frequency[rounded] = (frequency[rounded] ?? 0) + 1;
    }

    final List<BarChartGroupData> barGroups = [];
    int x = 0;

    frequency.forEach((hrValue, count) {
      barGroups.add(
        BarChartGroupData(
          x: x,
          barRods: [
            BarChartRodData(
              toY: count.toDouble(),
              color: _getHRColor(hrValue.toDouble()),
              width: 12,
              borderRadius: BorderRadius.circular(2),
            ),
          ],
        ),
      );
      x++;
    });

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Heart Rate Distribution',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 150,
              child: BarChart(
                BarChartData(
                  barTouchData: BarTouchData(
                    touchTooltipData: BarTouchTooltipData(
                      getTooltipItem: (group, groupIndex, rod, rodIndex) {
                        final hrValue = frequency.keys.toList()[groupIndex];
                        return BarTooltipItem(
                          '${frequency[hrValue]} times\nat ${hrValue}-${hrValue + 4} BPM',
                          const TextStyle(color: Colors.white),
                        );
                      },
                    ),
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          final hrValues = frequency.keys.toList();
                          final hrValue = hrValues[value.toInt()];
                          return Padding(
                            padding: const EdgeInsets.only(top: 4.0),
                            child: Text(
                              '$hrValue',
                              style: const TextStyle(fontSize: 10),
                            ),
                          );
                        },
                        reservedSize: 20,
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toInt().toString(),
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                        reservedSize: 30,
                      ),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border.all(color: Colors.grey[300]!),
                  ),
                  barGroups: barGroups,
                  gridData: const FlGridData(show: true),
                  alignment: BarChartAlignment.spaceBetween,
                  maxY: frequency.values
                          .reduce((a, b) => a > b ? a : b)
                          .toDouble() +
                      1,
                ),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Shows frequency of heart rate readings at different levels',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeartRateZones() {
    final List<PieChartSectionData> pieSections = [
      PieChartSectionData(
        color: Colors.green,
        value: 70,
        title: '70%',
        radius: 50,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      PieChartSectionData(
        color: Colors.orange,
        value: 20,
        title: '20%',
        radius: 50,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      PieChartSectionData(
        color: Colors.red,
        value: 10,
        title: '10%',
        radius: 50,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    ];

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Heart Rate Zones',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                // Pie Chart
                SizedBox(
                  width: 150,
                  height: 150,
                  child: PieChart(
                    PieChartData(
                      sections: pieSections,
                      centerSpaceRadius: 30,
                      sectionsSpace: 2,
                    ),
                  ),
                ),

                const SizedBox(width: 20),

                // Zone Legend
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildZoneLegend(
                          'Normal Zone', '110-140 BPM', Colors.green, 70),
                      _buildZoneLegend(
                          'Elevated Zone', '140-150 BPM', Colors.orange, 20),
                      _buildZoneLegend('High Zone', '150+ BPM', Colors.red, 10),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildZoneLegend(
      String label, String range, Color color, int percentage) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            color: color,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(fontSize: 14),
                ),
                Text(
                  range,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
          Text(
            '$percentage%',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailedStats() {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Detailed Statistics',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),

            Table(
              columnWidths: const {
                0: FlexColumnWidth(1.5),
                1: FlexColumnWidth(1),
                2: FlexColumnWidth(1),
              },
              children: [
                _buildTableRow('Metric', 'Value', const Text('Status')),
                _buildTableRow('Average HR', '128 BPM',
                    _buildStatusBadge('Normal', Colors.green)),
                _buildTableRow('Maximum HR', '142 BPM',
                    _buildStatusBadge('High', Colors.orange)),
                _buildTableRow('Minimum HR', '115 BPM',
                    _buildStatusBadge('Normal', Colors.green)),
                _buildTableRow('Variability', '12 BPM',
                    _buildStatusBadge('Good', Colors.blue)),
                _buildTableRow('Resting HR', '120 BPM',
                    _buildStatusBadge('Normal', Colors.green)),
              ],
            ),

            const SizedBox(height: 15),

            // Resting Heart Rate Trend
            const Text(
              'Resting Heart Rate Trend:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 40,
              child: LineChart(
                LineChartData(
                  gridData: const FlGridData(show: false),
                  titlesData: const FlTitlesData(show: false),
                  borderData: FlBorderData(show: false),
                  minX: 0,
                  maxX: 6,
                  minY: 115,
                  maxY: 125,
                  lineBarsData: [
                    LineChartBarData(
                      spots: const [
                        FlSpot(0, 122),
                        FlSpot(1, 120),
                        FlSpot(2, 118),
                        FlSpot(3, 120),
                        FlSpot(4, 121),
                        FlSpot(5, 119),
                        FlSpot(6, 120),
                      ],
                      isCurved: true,
                      color: Colors.blue,
                      barWidth: 2,
                      dotData: const FlDotData(show: true),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  TableRow _buildTableRow(String metric, String value, Widget status) {
    return TableRow(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Text(metric),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: status,
        ),
      ],
    );
  }

  Widget _buildStatusBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12,
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Color _getHRColor(double hr) {
    if (hr < 110) return Colors.blue;
    if (hr >= 110 && hr <= 140) return Colors.green;
    if (hr > 140 && hr <= 150) return Colors.orange;
    return Colors.red;
  }
}
