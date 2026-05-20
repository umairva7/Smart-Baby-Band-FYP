import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'core/theme/app_colors.dart';
import 'services/firestore_service.dart';
import 'globals.dart';

class TemperaturePage extends StatelessWidget {
  const TemperaturePage({super.key});

  // Temperature history accent color: Red
  static const Color _accent = AppColors.chartRed;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    if (globalDeviceId.isEmpty) {
      return FutureBuilder(
        future: loadDeviceId(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(body: Center(child: CircularProgressIndicator()));
          }
          if (globalDeviceId.isEmpty) {
            return const Scaffold(
              body: Center(child: Text('Device not linked. Please configure a baby profile.')),
            );
          }
          // Device ID recovered — rebuild with data
          return build(context);
        },
      );
    }

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: StreamBuilder<List<Map<String, dynamic>>>(
            stream: FirestoreService.getEnvironmentLogs(globalDeviceId),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Text('Error loading data: ${snapshot.error}',
                  style: theme.textTheme.bodyMedium);
              }
              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return Text('No data yet', style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ));
              }

          final data = snapshot.data!;
          final latest = data.first;
          final double currentTemp = (latest['temperature'] ?? 36.5).toDouble();

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Temperature Gauge
              _buildTemperatureGauge(theme, colorScheme, isDark, currentTemp),
              const SizedBox(height: 20),

              // Temperature Trend (real Firebase data)
              _buildTemperatureTrendChart(theme, colorScheme, isDark, data),
            ],
          );
        },
      ),
    ),
  ),
);
  }

  Widget _buildTemperatureGauge(ThemeData theme, ColorScheme colorScheme, bool isDark, double currentTemp) {
    double minTemp = 35.0;
    double maxTemp = 38.0;
    double tempPercentage = (currentTemp - minTemp) / (maxTemp - minTemp);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppColors.tempGradient(isDark),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.12)),
        boxShadow: [
          BoxShadow(
            color: _accent.withValues(alpha: isDark ? 0.08 : 0.06),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            'Current Temperature',
            style: theme.textTheme.titleMedium,
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
                      color: colorScheme.outlineVariant,
                      width: 15,
                    ),
                  ),
                ),

                // Temperature Arc — clipped to circle to hide gradient seam
                ClipOval(
                  child: Container(
                    width: 180,
                    height: 180,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: SweepGradient(
                        colors: [
                          Color(0xFF42A5F5),
                          Color(0xFF66BB6A),
                          Color(0xFFFFC107),
                          Color(0xFFFF9800),
                          Color(0xFFEF5350),
                        ],
                        stops: [0.0, 0.25, 0.5, 0.75, 1.0],
                        startAngle: 3.14,
                        endAngle: 6.28,
                      ),
                    ),
                  ),
                ),

                // Inner Circle
                Container(
                  width: 150,
                  height: 150,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: colorScheme.surface,
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
                              style: theme.textTheme.displayMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: _getTempStatusColor(currentTemp),
                              ),
                            ),
                            const SizedBox(width: 5),
                            Text(
                              '°C',
                              style: theme.textTheme.titleLarge?.copyWith(
                                color: _getTempStatusColor(currentTemp),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 5),
                        Text(
                          _getTempStatus(currentTemp),
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: _getTempStatusColor(currentTemp),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Temperature Indicator — adjusted for bottom-arc orientation
                Transform.rotate(
                  angle: (tempPercentage * 3.14) + 3.14,
                  child: Container(
                    width: 2,
                    height: 90,
                    color: colorScheme.onSurface,
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
              Text('35°C', style: theme.textTheme.bodySmall?.copyWith(
                color: const Color(0xFF42A5F5), fontWeight: FontWeight.w600)),
              Text('36°C', style: theme.textTheme.bodySmall?.copyWith(
                color: const Color(0xFF66BB6A), fontWeight: FontWeight.w600)),
              Text('37°C', style: theme.textTheme.bodySmall?.copyWith(
                color: const Color(0xFFFF9800), fontWeight: FontWeight.w600)),
              Text('38°C', style: theme.textTheme.bodySmall?.copyWith(
                color: _accent, fontWeight: FontWeight.w600)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTemperatureTrendChart(ThemeData theme, ColorScheme colorScheme, bool isDark, List<Map<String, dynamic>> data) {
    final recent = data.length > 10 ? data.sublist(data.length - 10) : data;

    // Map entries to FlSpot — x = index, y = temperature
    final spots = <FlSpot>[];
    for (int i = 0; i < recent.length; i++) {
      final temp = (recent[i]['temperature'] ?? 0).toDouble();
      spots.add(FlSpot(i.toDouble(), temp));
    }

    if (spots.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppColors.tempGradient(isDark),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.12)),
        boxShadow: [
          BoxShadow(
            color: _accent.withValues(alpha: isDark ? 0.08 : 0.06),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Temperature Trend', style: theme.textTheme.titleMedium),
          const SizedBox(height: 12),
          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 0.5,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: colorScheme.outlineVariant.withValues(alpha: 0.4),
                      strokeWidth: 1,
                    );
                  },
                ),
                titlesData: FlTitlesData(
                  show: true,
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 0.5,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          '${value.toStringAsFixed(1)}°',
                          style: theme.textTheme.bodySmall,
                        );
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  bottomTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                minY: 35.0,
                maxY: 38.5,
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    color: _accent,
                    barWidth: 2.5,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, barData, index) {
                        return FlDotCirclePainter(
                          radius: 3,
                          color: _accent,
                          strokeWidth: 0,
                        );
                      },
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      color: _accent.withValues(alpha: 0.08),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Last ${recent.length} readings',
            style: theme.textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  Color _getTempStatusColor(double temp) {
    if (temp < 36.5) return const Color(0xFF42A5F5);
    if (temp >= 36.5 && temp <= 37.0) return AppColors.chartGreen;
    if (temp > 37.0 && temp <= 37.5) return AppColors.chartOrange;
    return _accent;
  }

  String _getTempStatus(double temp) {
    if (temp < 36.5) return 'Slightly Low';
    if (temp >= 36.5 && temp <= 37.0) return 'Normal';
    if (temp > 37.0 && temp <= 37.5) return 'Slightly High';
    return 'High Temperature';
  }
}
