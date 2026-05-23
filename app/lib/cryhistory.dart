import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'core/theme/app_colors.dart';
import 'services/firestore_service.dart';
import 'globals.dart';

class CryPage extends StatelessWidget {
  const CryPage({super.key});

  // Cry history accent color: Amber
  static const Color _accent = AppColors.chartAmber;

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
          return _buildStreamedContent(context, theme, colorScheme, isDark);
        },
      );
    }

    return _buildStreamedContent(context, theme, colorScheme, isDark);
  }

  Widget _buildStreamedContent(
      BuildContext context, ThemeData theme, ColorScheme colorScheme, bool isDark) {
    return StreamBuilder<List<Map<String, dynamic>>>(
      stream: FirestoreService.getCryEvents(globalDeviceId),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text('Error loading charts: ${snapshot.error}'),
            ),
          );
        }

        final events = snapshot.data ?? [];

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary Cards (Dynamically computed from events!)
              _buildSummaryCards(theme, isDark, events),
              const SizedBox(height: 20),

              // Dynamic Area Line Chart (Cry Pattern Last 24 Hours)
              _buildLineChart(theme, colorScheme, isDark, events),
              const SizedBox(height: 20),

              // Dynamic Bar Chart (Cry Reasons Distribution)
              _buildReasonChart(theme, colorScheme, isDark, events),
              const SizedBox(height: 20),

              // Recent Cries List
              _buildRecentCries(context, theme, colorScheme, isDark, events),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSummaryCards(ThemeData theme, bool isDark, List<Map<String, dynamic>> events) {
    // 1. Calculate Today's Cries
    final now = DateTime.now();
    final todayEvents = events.where((e) {
      final ts = e['timestamp'];
      if (ts == null) return false;
      final dt = ts is Timestamp ? ts.toDate() : DateTime.fromMillisecondsSinceEpoch(ts as int);
      return dt.year == now.year && dt.month == now.month && dt.day == now.day;
    }).toList();
    final String todayCount = todayEvents.length.toString();

    // 2. Calculate Average Confidence
    double totalConf = 0.0;
    for (var e in events) {
      final val = e['confidence'];
      if (val is num) {
        totalConf += val.toDouble();
      }
    }
    final String avgConf = events.isNotEmpty
        ? '${(totalConf / events.length * 100).toStringAsFixed(0)}%'
        : '0%';

    // 3. Calculate Most Frequent Reason
    final Map<String, int> counts = {};
    for (var e in events) {
      final reason = (e['cry_type'] ?? 'unknown').toString().toLowerCase();
      if (reason != 'unknown') {
        counts[reason] = (counts[reason] ?? 0) + 1;
      }
    }
    String mostReason = 'None';
    if (counts.isNotEmpty) {
      final topLabel = counts.entries.reduce((a, b) => a.value > b.value ? a : b).key;
      mostReason = _getFormattedReason(topLabel);
    }

    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            theme, isDark,
            'Today\'s Cries',
            todayCount,
            Icons.mic_rounded,
            _accent,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildSummaryCard(
            theme, isDark,
            'Avg Confidence',
            avgConf,
            Icons.query_stats_rounded,
            AppColors.chartBlue,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildSummaryCard(
            theme, isDark,
            'Most Reason',
            mostReason,
            Icons.local_dining_rounded,
            AppColors.chartOrange,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(
      ThemeData theme, bool isDark,
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      height: 110,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [color.withValues(alpha: 0.12), color.withValues(alpha: 0.06)]
              : [color.withValues(alpha: 0.08), color.withValues(alpha: 0.03)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 6),
          Text(
            value,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildLineChart(
      ThemeData theme, ColorScheme colorScheme, bool isDark, List<Map<String, dynamic>> events) {
    // Generate beautiful real spots from dynamic history events
    final List<FlSpot> spots = [];

    if (events.isEmpty) {
      // Return beautiful baseline spots if no data is present
      for (int h = 0; h <= 24; h += 4) {
        spots.add(FlSpot(h.toDouble(), 0));
      }
    } else {
      // Map live cry events to hourly spots based on time of occurrence and confidence
      for (var e in events) {
        final ts = e['timestamp'];
        if (ts != null) {
          final DateTime dt = ts is Timestamp ? ts.toDate() : DateTime.fromMillisecondsSinceEpoch(ts as int);
          final double timeOfDay = dt.hour + (dt.minute / 60.0);
          final double confidence = ((e['confidence'] ?? 0.8) as num).toDouble() * 100;
          spots.add(FlSpot(timeOfDay, confidence));
        }
      }
      
      // Safety sort to ensure fl_chart draws chronologically along X axis
      spots.sort((a, b) => a.x.compareTo(b.x));

      // Anchor corners for clean aesthetics
      if (spots.first.x > 0) {
        spots.insert(0, FlSpot(0, spots.first.y * 0.4));
      }
      if (spots.last.x < 24) {
        spots.add(FlSpot(24, spots.last.y * 0.4));
      }
    }

    final gridColor = isDark ? colorScheme.outlineVariant : Colors.grey[300]!;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.10)),
        boxShadow: [
          BoxShadow(
            color: colorScheme.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Cry Pattern & Intensity (Last 24 Hours)',
                  style: theme.textTheme.titleMedium,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: true,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(color: gridColor, strokeWidth: 0.7);
                  },
                  getDrawingVerticalLine: (value) {
                    return FlLine(color: gridColor, strokeWidth: 0.7);
                  },
                ),
                titlesData: FlTitlesData(
                  show: true,
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 30,
                      getTitlesWidget: (value, meta) {
                        List<String> hours = ['12AM', '6AM', '12PM', '6PM', '12AM'];
                        int index = (value / 6).round();
                        if (index >= 0 && index < hours.length && (value % 6).abs() < 0.1) {
                          return Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Text(hours[index], style: theme.textTheme.bodySmall),
                          );
                        }
                        return const SizedBox();
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) {
                        if (value % 20 == 0) {
                          return Text('${value.toInt()}%', style: theme.textTheme.bodySmall);
                        }
                        return const SizedBox();
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border.all(color: gridColor),
                ),
                minX: 0,
                maxX: 24,
                minY: 0,
                maxY: 100,
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    curveSmoothness: 0.35,
                    color: _accent,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        colors: [
                          _accent.withValues(alpha: 0.35),
                          _accent.withValues(alpha: 0.05),
                        ],
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                      ),
                    ),
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, barData, index) {
                        return FlDotCirclePainter(
                          radius: 4,
                          color: _accent,
                          strokeWidth: 1.5,
                          strokeColor: Colors.white,
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Time of Day', style: theme.textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              )),
              Text('Confidence (%)', style: theme.textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              )),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildReasonChart(
      ThemeData theme, ColorScheme colorScheme, bool isDark, List<Map<String, dynamic>> events) {
    // 1. Calculate dynamic distribution percentages
    final Map<String, int> counts = {
      'hungry': 0,
      'tired': 0,
      'discomfort': 0,
      'diaper': 0,
      'pain': 0
    };
    
    int classifiedCount = 0;
    for (var e in events) {
      final reason = (e['cry_type'] ?? 'unknown').toString().toLowerCase();
      if (counts.containsKey(reason)) {
        counts[reason] = counts[reason]! + 1;
        classifiedCount++;
      }
    }

    final Map<String, double> reasonData = {
      'Hunger': 0,
      'Sleepy': 0,
      'Discomfort': 0,
      'Diaper': 0,
      'Pain': 0,
    };

    if (classifiedCount > 0) {
      reasonData['Hunger'] = (counts['hungry']! / classifiedCount) * 100;
      reasonData['Sleepy'] = (counts['tired']! / classifiedCount) * 100;
      reasonData['Discomfort'] = (counts['discomfort']! / classifiedCount) * 100;
      reasonData['Diaper'] = (counts['diaper']! / classifiedCount) * 100;
      reasonData['Pain'] = (counts['pain']! / classifiedCount) * 100;
    } else {
      // Default placeholder layout if database is empty
      reasonData['Hunger'] = 0.0;
      reasonData['Sleepy'] = 0.0;
      reasonData['Discomfort'] = 0.0;
      reasonData['Diaper'] = 0.0;
      reasonData['Pain'] = 0.0;
    }

    final List<BarChartGroupData> barGroups = [];
    int x = 0;
    double maxVal = 10.0; // Default dynamic ceiling

    reasonData.forEach((reason, percentage) {
      if (percentage > maxVal) maxVal = percentage;
      barGroups.add(
        BarChartGroupData(
          x: x,
          barRods: [
            BarChartRodData(
              toY: percentage,
              color: _getReasonColor(reason),
              width: 16,
              borderRadius: BorderRadius.circular(6),
              backDrawRodData: BackgroundBarChartRodData(
                show: true,
                toY: 100,
                color: isDark ? Colors.grey[850] : Colors.grey[100],
              ),
            ),
          ],
        ),
      );
      x++;
    });

    final gridColor = isDark ? colorScheme.outlineVariant : Colors.grey[300]!;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.10)),
        boxShadow: [
          BoxShadow(
            color: colorScheme.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Cry Reasons Distribution (%)',
            style: theme.textTheme.titleMedium,
          ),
          const SizedBox(height: 15),
          SizedBox(
            height: 200,
            child: BarChart(
              BarChartData(
                barTouchData: BarTouchData(
                  touchTooltipData: BarTouchTooltipData(
                    tooltipBgColor: colorScheme.surface,
                    getTooltipItem: (group, groupIndex, rod, rodIndex) {
                      final reason = reasonData.keys.elementAt(groupIndex);
                      return BarTooltipItem(
                        '$reason\n${rod.toY.toStringAsFixed(1)}%',
                        theme.textTheme.bodyMedium!.copyWith(
                          color: _getReasonColor(reason),
                          fontWeight: FontWeight.bold,
                        ),
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
                        List<String> reasons = reasonData.keys.toList();
                        int index = value.toInt();
                        return index >= 0 && index < reasons.length
                            ? Padding(
                                padding: const EdgeInsets.only(top: 8.0),
                                child: Text(
                                  reasons[index],
                                  style: theme.textTheme.bodySmall?.copyWith(fontSize: 9),
                                  textAlign: TextAlign.center,
                                ),
                              )
                            : const SizedBox();
                      },
                      reservedSize: 30,
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        if (value % 20 == 0) {
                          return Text('${value.toInt()}%', style: theme.textTheme.bodySmall);
                        }
                        return const SizedBox();
                      },
                      reservedSize: 30,
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border.all(color: gridColor),
                ),
                barGroups: barGroups,
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (value) => FlLine(color: gridColor, strokeWidth: 0.5),
                ),
                alignment: BarChartAlignment.spaceAround,
                maxY: 100,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentCries(
      BuildContext context, ThemeData theme, ColorScheme colorScheme, bool isDark, List<Map<String, dynamic>> events) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _accent.withValues(alpha: 0.10)),
        boxShadow: [
          BoxShadow(
            color: colorScheme.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent Cries History',
            style: theme.textTheme.titleMedium,
          ),
          const SizedBox(height: 15),
          if (events.isEmpty)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'No cry recordings logged yet.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            )
          else
            Column(
              children: events.take(15).map((cry) {
                final reason = cry['cry_type'] ?? 'Unknown';
                
                String timeStr = '--:--';
                final ts = cry['timestamp'];
                if (ts != null) {
                  DateTime dt;
                  if (ts is int) {
                    dt = DateTime.fromMillisecondsSinceEpoch(ts);
                  } else {
                    dt = ts.toDate();
                  }
                  timeStr = '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
                }

                final confidenceVal = cry['confidence'];
                int confidence = 0;
                if (confidenceVal is double) {
                  confidence = (confidenceVal * 100).toInt();
                } else if (confidenceVal is int) {
                  confidence = confidenceVal;
                }

                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: _getReasonColor(reason).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          _getReasonIcon(reason),
                          color: _getReasonColor(reason),
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _getFormattedReason(reason),
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(timeStr, style: theme.textTheme.bodyMedium),
                          Text(
                            '$confidence% confidence',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: _getIntensityColor(confidence),
                              fontSize: 11,
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
    );
  }

  Color _getReasonColor(String reason) {
    switch (reason.toLowerCase()) {
      case 'hungry':
      case 'hunger':
        return AppColors.chartOrange;
      case 'tired':
      case 'sleepy':
        return AppColors.chartIndigo;
      case 'discomfort':
        return AppColors.chartRed;
      case 'diaper':
      case 'wet diaper':
        return AppColors.chartGreen;
      case 'pain':
        return AppColors.chartRed;
      default:
        return AppColors.chartAmber;
    }
  }

  Color _getIntensityColor(int intensity) {
    if (intensity >= 80) return AppColors.chartRed;
    if (intensity >= 60) return AppColors.chartOrange;
    return AppColors.chartGreen;
  }

  IconData _getReasonIcon(String reason) {
    switch (reason.toLowerCase()) {
      case 'hungry':
      case 'hunger':
        return Icons.local_dining;
      case 'tired':
      case 'sleepy':
        return Icons.bedtime;
      case 'discomfort':
        return Icons.sick;
      case 'diaper':
      case 'wet diaper':
        return Icons.baby_changing_station;
      case 'pain':
        return Icons.warning_amber_rounded;
      default:
        return Icons.help;
    }
  }

  String _getFormattedReason(String reason) {
    switch (reason.toLowerCase()) {
      case 'hungry':
        return 'Hunger';
      case 'tired':
        return 'Sleepy';
      case 'discomfort':
        return 'Discomfort';
      case 'diaper':
        return 'Wet Diaper';
      case 'pain':
        return 'Pain';
      default:
        return reason.toUpperCase();
    }
  }
}
