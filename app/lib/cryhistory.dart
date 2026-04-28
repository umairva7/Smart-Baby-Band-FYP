import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'core/theme/app_colors.dart';

class CryPage extends StatelessWidget {
  const CryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Summary Cards
            _buildSummaryCards(),
            const SizedBox(height: 20),

            // Line Chart
            _buildLineChart(),
            const SizedBox(height: 20),

            // Bar Chart for Cry Reasons
            _buildReasonChart(),
            const SizedBox(height: 20),

            // Recent Cries List
            _buildRecentCries(context),
          ],
        ),
      );
  }

  Widget _buildSummaryCards() {
    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            'Today\'s Cries',
            '8',
            Icons.mic,
            AppColors.chartPurple,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildSummaryCard(
            'Avg Duration',
            '4.2 min',
            Icons.timer,
            AppColors.chartBlue,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildSummaryCard(
            'Most Reason',
            'Hunger',
            Icons.local_dining,
            AppColors.chartOrange,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: const TextStyle(fontSize: 12, color: Colors.grey),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildLineChart() {
    final List<FlSpot> cryData = [
      const FlSpot(0, 20),
      const FlSpot(2, 45),
      const FlSpot(4, 15),
      const FlSpot(6, 85),
      const FlSpot(8, 40),
      const FlSpot(10, 25),
      const FlSpot(12, 60),
      const FlSpot(14, 35),
      const FlSpot(16, 90),
      const FlSpot(18, 50),
      const FlSpot(20, 30),
      const FlSpot(22, 70),
      const FlSpot(24, 40),
    ];

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Cry Pattern (Last 24 Hours)',
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
                    getDrawingVerticalLine: (value) {
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
                          List<String> hours = [
                            '12AM',
                            '6AM',
                            '12PM',
                            '6PM',
                            '12AM'
                          ];
                          int index = (value ~/ 6).toInt();
                          return index >= 0 && index < hours.length
                              ? Padding(
                                  padding: const EdgeInsets.only(top: 8.0),
                                  child: Text(hours[index]),
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
                          return Text('${value.toInt()}%');
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border.all(color: Colors.grey[300]!),
                  ),
                  minX: 0,
                  maxX: 24,
                  minY: 0,
                  maxY: 100,
                  lineBarsData: [
                    LineChartBarData(
                      spots: cryData,
                      isCurved: true,
                      color: AppColors.chartPurple,
                      barWidth: 3,
                      isStrokeCapRound: true,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            AppColors.chartPurple.withValues(alpha: 0.3),
                            AppColors.chartPurple.withValues(alpha: 0.1),
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
                Text('Time of Day', style: TextStyle(color: Colors.grey)),
                Text('Cry Intensity (%)', style: TextStyle(color: Colors.grey)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReasonChart() {
    final Map<String, double> reasonData = {
      'Hunger': 45,
      'Sleepy': 25,
      'Discomfort': 15,
      'Need Burping': 10,
      'Other': 5,
    };

    final List<BarChartGroupData> barGroups = [];
    int x = 0;

    reasonData.forEach((reason, percentage) {
      barGroups.add(
        BarChartGroupData(
          x: x,
          barRods: [
            BarChartRodData(
              toY: percentage,
              color: _getReasonColor(reason),
              width: 20,
              borderRadius: BorderRadius.circular(4),
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
              'Cry Reasons Distribution',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  barTouchData: BarTouchData(
                    touchTooltipData: BarTouchTooltipData(
                      tooltipBgColor: Colors.white,
                    ),
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          List<String> reasons = reasonData.keys.toList();
                          int index = value.toInt();
                          return index >= 0 && index < reasons.length
                              ? Padding(
                                  padding: const EdgeInsets.only(top: 8.0),
                                  child: Text(
                                    reasons[index],
                                    style: const TextStyle(fontSize: 10),
                                    textAlign: TextAlign.center,
                                  ),
                                )
                              : const SizedBox();
                        },
                        reservedSize: 40,
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          return Text('${value.toInt()}%');
                        },
                        reservedSize: 30,
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border.all(color: Colors.grey[300]!),
                  ),
                  barGroups: barGroups,
                  gridData: const FlGridData(show: true),
                  alignment: BarChartAlignment.spaceAround,
                  maxY: 50,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentCries(BuildContext context) {
    final List<Map<String, dynamic>> recentCries = [
      {
        'time': '2:30 PM',
        'reason': 'Hunger',
        'duration': '4:12',
        'intensity': 85
      },
      {
        'time': '11:45 AM',
        'reason': 'Sleepy',
        'duration': '3:45',
        'intensity': 60
      },
      {
        'time': '9:15 AM',
        'reason': 'Discomfort',
        'duration': '5:20',
        'intensity': 90
      },
      {
        'time': '6:30 AM',
        'reason': 'Hunger',
        'duration': '3:55',
        'intensity': 75
      },
      {
        'time': '1:15 AM',
        'reason': 'Need Burping',
        'duration': '2:30',
        'intensity': 45
      },
    ];

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Cries',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Column(
              children: recentCries.map((cry) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: _getReasonColor(cry['reason'] as String)
                              .withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Icon(
                          _getReasonIcon(cry['reason'] as String),
                          color: _getReasonColor(cry['reason'] as String),
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              cry['reason'] as String,
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              'Duration: ${cry['duration']} min',
                              style: const TextStyle(
                                  fontSize: 12, color: Colors.grey),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(cry['time'] as String),
                          Text(
                            '${cry['intensity']}% intensity',
                            style: TextStyle(
                              fontSize: 12,
                              color:
                                  _getIntensityColor(cry['intensity'] as int),
                            ),
                          ),
                        ],
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

  Color _getReasonColor(String reason) {
    switch (reason) {
      case 'Hunger':
        return Colors.orange;
      case 'Sleepy':
        return Colors.blue;
      case 'Discomfort':
        return Colors.red;
      case 'Need Burping':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Color _getIntensityColor(int intensity) {
    if (intensity >= 80) return Colors.red;
    if (intensity >= 60) return Colors.orange;
    return Colors.green;
  }

  IconData _getReasonIcon(String reason) {
    switch (reason) {
      case 'Hunger':
        return Icons.local_dining;
      case 'Sleepy':
        return Icons.bedtime;
      case 'Discomfort':
        return Icons.sick;
      case 'Need Burping':
        return Icons.airline_seat_flat;
      default:
        return Icons.help;
    }
  }
}
