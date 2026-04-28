import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class TemperaturePage extends StatelessWidget {
  const TemperaturePage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Temperature Gauge
            _buildTemperatureGauge(),
            const SizedBox(height: 20),

            // Temperature Trend Area Chart
            _buildTemperatureAreaChart(),
            const SizedBox(height: 20),

            // Temperature Heat Map (Weekly)
            _buildTemperatureHeatMap(),
            const SizedBox(height: 20),

            // Temperature Statistics
            _buildTemperatureStats(),
        ],
      ),
    );
  }

  Widget _buildTemperatureGauge() {
    double currentTemp = 36.8;
    double minTemp = 35.0;
    double maxTemp = 38.0;
    double tempPercentage = (currentTemp - minTemp) / (maxTemp - minTemp);

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'Current Temperature',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),

            // Gauge Circle
            SizedBox(
              height: 180,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Background Circle
                  Container(
                    width: 180,
                    height: 180,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Colors.grey[300]!,
                        width: 15,
                      ),
                    ),
                  ),

                  // Temperature Arc
                  Container(
                    width: 180,
                    height: 180,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: SweepGradient(
                        colors: [
                          Colors.blue,
                          Colors.green,
                          Colors.yellow,
                          Colors.orange,
                          Colors.red,
                        ],
                        stops: const [0.0, 0.25, 0.5, 0.75, 1.0],
                        startAngle: -0.5,
                        endAngle: 2.5,
                      ),
                    ),
                  ),

                  // Inner Circle
                  Container(
                    width: 150,
                    height: 150,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white,
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.baseline,
                            textBaseline: TextBaseline.alphabetic,
                            children: [
                              Text(
                                currentTemp.toStringAsFixed(1),
                                style: const TextStyle(
                                  fontSize: 42,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.orange,
                                ),
                              ),
                              const SizedBox(width: 5),
                              const Text(
                                '°C',
                                style: TextStyle(
                                  fontSize: 24,
                                  color: Colors.orange,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 5),
                          Text(
                            _getTempStatus(currentTemp),
                            style: TextStyle(
                              fontSize: 16,
                              color: _getTempStatusColor(currentTemp),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Temperature Indicator
                  Transform.rotate(
                    angle: (tempPercentage * 3.14) - 1.57,
                    child: Container(
                      width: 2,
                      height: 90,
                      color: Colors.black,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 15),

            // Temperature Range Labels
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('35°C', style: TextStyle(color: Colors.blue[700])),
                Text('36°C', style: TextStyle(color: Colors.green[700])),
                Text('37°C', style: TextStyle(color: Colors.orange[700])),
                Text('38°C', style: TextStyle(color: Colors.red[700])),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTemperatureAreaChart() {
    final List<FlSpot> tempData = [
      const FlSpot(0, 36.5),
      const FlSpot(2, 36.6),
      const FlSpot(4, 36.4),
      const FlSpot(6, 36.7),
      const FlSpot(8, 36.9),
      const FlSpot(10, 37.0),
      const FlSpot(12, 36.8),
      const FlSpot(14, 36.7),
      const FlSpot(16, 36.9),
      const FlSpot(18, 37.1),
      const FlSpot(20, 36.8),
      const FlSpot(22, 36.6),
      const FlSpot(24, 36.5),
    ];

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '24-Hour Temperature Trend',
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
                    drawHorizontalLine: true,
                    getDrawingHorizontalLine: (value) {
                      if (value == 37.0) {
                        return FlLine(
                          color: Colors.red.withValues(alpha: 0.5),
                          strokeWidth: 1,
                          dashArray: const [5, 5],
                        );
                      }
                      return FlLine(
                        color: Colors.grey[200]!,
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
                            '12AM',
                            '6AM',
                            '12PM',
                            '6PM',
                            '12AM'
                          ];
                          int index = (value ~/ 6).toInt();
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
                          return Text(
                            '${value.toStringAsFixed(1)}°',
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(show: false),
                  minX: 0,
                  maxX: 24,
                  minY: 36.0,
                  maxY: 37.5,
                  lineBarsData: [
                    LineChartBarData(
                      spots: tempData,
                      isCurved: true,
                      color: Colors.transparent,
                      barWidth: 0,
                      isStrokeCapRound: true,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.orange.withValues(alpha: 0.5),
                            Colors.orange.withValues(alpha: 0.1),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                      dotData: FlDotData(
                        show: true,
                        getDotPainter: (spot, percent, barData, index) {
                          return FlDotCirclePainter(
                            radius: 3,
                            color: Colors.orange,
                            strokeWidth: 2,
                            strokeColor: Colors.white,
                          );
                        },
                      ),
                    ),
                  ],
                  lineTouchData: LineTouchData(
                    touchTooltipData: LineTouchTooltipData(
                      tooltipBgColor: Colors.white,
                      getTooltipItems: (touchedSpots) {
                        return touchedSpots.map((spot) {
                          return LineTooltipItem(
                            '${spot.y.toStringAsFixed(1)}°C\n${spot.x.toInt()}:00',
                            const TextStyle(color: Colors.black),
                          );
                        }).toList();
                      },
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Area chart shows temperature variations'),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'Safe Range',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.orange[800],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTemperatureHeatMap() {
    final List<String> days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    final List<String> times = ['AM', 'PM'];

    // Simulated temperature data for heatmap
    final List<List<double>> heatMapData = [
      [36.5, 36.7, 36.6, 36.8, 36.9, 37.0, 36.8], // AM
      [36.7, 36.8, 36.9, 37.0, 37.1, 36.9, 36.7], // PM
    ];

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Weekly Temperature Pattern',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),

            // Heat Map Grid
            Column(
              children: [
                // Header row (days)
                Row(
                  children: [
                    const SizedBox(width: 40),
                    ...days.map((day) => Expanded(
                          child: Center(
                            child: Text(
                              day,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        )),
                  ],
                ),

                const SizedBox(height: 10),

                // Heat map rows
                ...List.generate(2, (timeIndex) {
                  return Row(
                    children: [
                      SizedBox(
                        width: 40,
                        child: Text(
                          times[timeIndex],
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      ...List.generate(7, (dayIndex) {
                        double temp = heatMapData[timeIndex][dayIndex];
                        return Expanded(
                          child: Container(
                            margin: const EdgeInsets.all(2),
                            height: 40,
                            decoration: BoxDecoration(
                              color: _getHeatMapColor(temp),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Center(
                              child: Text(
                                '${temp.toStringAsFixed(1)}',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: temp >= 37.0
                                      ? Colors.white
                                      : Colors.black,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        );
                      }),
                    ],
                  );
                }),
              ],
            ),

            const SizedBox(height: 10),

            // Heat Map Legend
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Heat Map Legend:'),
                Row(
                  children: [
                    Container(width: 15, height: 15, color: Colors.blue),
                    const SizedBox(width: 5),
                    const Text('Cool', style: TextStyle(fontSize: 12)),
                    const SizedBox(width: 10),
                    Container(width: 15, height: 15, color: Colors.green),
                    const SizedBox(width: 5),
                    const Text('Normal', style: TextStyle(fontSize: 12)),
                    const SizedBox(width: 10),
                    Container(width: 15, height: 15, color: Colors.orange),
                    const SizedBox(width: 5),
                    const Text('Warm', style: TextStyle(fontSize: 12)),
                    const SizedBox(width: 10),
                    Container(width: 15, height: 15, color: Colors.red),
                    const SizedBox(width: 5),
                    const Text('Hot', style: TextStyle(fontSize: 12)),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTemperatureStats() {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Temperature Statistics',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),

            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              childAspectRatio: 2.5,
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              children: [
                _buildStatBox(
                    'Today\'s High', '37.1°C', Icons.arrow_upward, Colors.red),
                _buildStatBox('Today\'s Low', '36.4°C', Icons.arrow_downward,
                    Colors.blue),
                _buildStatBox(
                    'Weekly Avg', '36.8°C', Icons.timeline, Colors.orange),
                _buildStatBox(
                    'Stability', '94%', Icons.stacked_line_chart, Colors.green),
              ],
            ),

            const SizedBox(height: 15),
            const Divider(),
            const SizedBox(height: 10),

            // Temperature Range Info
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Normal Range:', style: TextStyle(color: Colors.grey)),
                    Text('36.5°C - 37.0°C',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('Current Status:',
                        style: TextStyle(color: Colors.grey)),
                    Text('Normal',
                        style: TextStyle(
                            color: Colors.green, fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatBox(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
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
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getTempStatusColor(double temp) {
    if (temp < 36.5) return Colors.blue;
    if (temp >= 36.5 && temp <= 37.0) return Colors.green;
    if (temp > 37.0 && temp <= 37.5) return Colors.orange;
    return Colors.red;
  }

  String _getTempStatus(double temp) {
    if (temp < 36.5) return 'Slightly Low';
    if (temp >= 36.5 && temp <= 37.0) return 'Normal';
    if (temp > 37.0 && temp <= 37.5) return 'Slightly High';
    return 'High Temperature';
  }

  Color _getHeatMapColor(double temp) {
    if (temp < 36.5) return Colors.blue[200]!;
    if (temp >= 36.5 && temp < 36.8) return Colors.green[200]!;
    if (temp >= 36.8 && temp < 37.0) return Colors.yellow[200]!;
    if (temp >= 37.0 && temp < 37.2) return Colors.orange[200]!;
    return Colors.red[200]!;
  }
}
