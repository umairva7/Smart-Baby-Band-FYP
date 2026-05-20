import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'core/theme/app_colors.dart';
import 'services/firestore_service.dart';
import 'globals.dart';

class HeartbeatPage extends StatelessWidget {
  const HeartbeatPage({super.key});

  // Heartbeat history accent color: Pink
  static const Color _accent = AppColors.chartPink;

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
            return const Center(child: CircularProgressIndicator());
          }
          if (globalDeviceId.isEmpty) {
            return Center(
              child: Text(
                'Device not linked. Please configure a baby profile.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            );
          }
          return build(context);
        },
      );
    }

    return StreamBuilder<List<Map<String, dynamic>>>(
      stream: FirestoreService.getSensorData(globalDeviceId),
      builder: (context, snapshot) {
        final data = snapshot.data ?? [];

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Heart Rate with Live Animation
              _buildHeartRateLive(theme, colorScheme, isDark),
              const SizedBox(height: 20),

              // Heart Rate Trend (real Firebase data)
              _buildHeartRateTrendChart(theme, colorScheme, isDark, data),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeartRateLive(ThemeData theme, ColorScheme colorScheme, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppColors.heartGradient(isDark),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.15)),
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
            'Live Heart Rate',
            style: theme.textTheme.titleMedium,
          ),
          const SizedBox(height: 15),

          // Concentric circles only — no floating icon overlay
          Container(
            width: 150,
            height: 150,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _accent.withValues(alpha: 0.08),
            ),
            child: Center(
              child: Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _accent.withValues(alpha: 0.14),
                ),
                child: Center(
                  child: Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _accent.withValues(alpha: 0.22),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.favorite, color: _accent, size: 20),
                          const SizedBox(height: 2),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment:
                                CrossAxisAlignment.baseline,
                            textBaseline: TextBaseline.alphabetic,
                            children: [
                              Text(
                                '128',
                                style: theme.textTheme.displaySmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: _accent,
                                ),
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'BPM',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: _accent,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Normal',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: AppColors.chartGreen,
                              fontWeight: FontWeight.w600,
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
                    color: _accent,
                    barWidth: 2,
                    dotData: const FlDotData(show: false),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 10),
          Text(
            'Last 10 minutes trend',
            style: theme.textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeartRateTrendChart(ThemeData theme, ColorScheme colorScheme, bool isDark, List<Map<String, dynamic>> data) {
    if (data.isEmpty) return const SizedBox.shrink();

    final recent = data.length > 10 ? data.sublist(data.length - 10) : data;

    // Map entries to FlSpot — x = index, y = heart_rate (or bpm)
    final spots = <FlSpot>[];
    for (int i = 0; i < recent.length; i++) {
      final hr = (recent[i]['heart_rate'] ?? recent[i]['bpm'] ?? 0).toDouble();
      spots.add(FlSpot(i.toDouble(), hr));
    }

    if (spots.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppColors.heartGradient(isDark),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.15)),
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
          Text('Heart Rate Trend', style: theme.textTheme.titleMedium),
          const SizedBox(height: 12),
          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 10,
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
                      interval: 10,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          '${value.toInt()}',
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
                minY: 100,
                maxY: 160,
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
}
