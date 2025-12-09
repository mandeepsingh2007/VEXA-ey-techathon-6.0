import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/services/agent_service.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:vexa/widgets/ai_chat_widget.dart';

class ManufacturingDashboardScreen extends StatefulWidget {
  const ManufacturingDashboardScreen({super.key});

  @override
  State<ManufacturingDashboardScreen> createState() =>
      _ManufacturingDashboardScreenState();
}

class _ManufacturingDashboardScreenState
    extends State<ManufacturingDashboardScreen> {
  final AgentService _agentService = AgentService();
  bool _isLoading = true;
  Map<String, dynamic>? _insightsData;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      final data = await _agentService.fetchManufacturingInsights();
      setState(() {
        _insightsData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      // Handle error cleanly or show mock data if fetch fails
    }
  }

  void _showChatModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        child: SizedBox(
          height: MediaQuery.of(context).size.height * 0.6,
          child: const AIChatWidget(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: AppTheme.backgroundColor,
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final defectTrends =
        _insightsData?['defect_trends'] as Map<String, dynamic>? ?? {};
    final failureTrends =
        _insightsData?['failure_trends'] as Map<String, dynamic>? ?? {};
    final recommendations = _insightsData?['recommendations'] as List?;

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showChatModal,
        backgroundColor: Colors.purple,
        icon: const Icon(Icons.auto_awesome, color: Colors.white),
        label: const Text("Ask AI Lead", style: TextStyle(color: Colors.white)),
      ),
      appBar: AppBar(
        title: const Text('VEXA OEM Insights'),
        actions: [
          _buildFilterButton('All Brands'),
          _buildFilterButton('Last 30 days', icon: Icons.calendar_today),
          const SizedBox(width: 16),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Responsive KPI Cards (Wrap)
            LayoutBuilder(
              builder: (context, constraints) {
                final isMobile = constraints.maxWidth < 800;

                return Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    SizedBox(
                      width: isMobile
                          ? (constraints.maxWidth - 16) / 2
                          : (constraints.maxWidth - 48) / 4,
                      child: _buildStatCard(
                        title: 'Vehicles monitored',
                        value: '12,450',
                        trend: '+8%',
                        isPositive: true,
                        icon: Icons.directions_car,
                        iconColor: Colors.blue,
                      ),
                    ),
                    SizedBox(
                      width: isMobile
                          ? (constraints.maxWidth - 16) / 2
                          : (constraints.maxWidth - 48) / 4,
                      child: _buildStatCard(
                        title: 'Predictive brake alerts (30d)',
                        value: '1,230',
                        trend: '-12%',
                        isPositive: false,
                        icon: Icons.warning_amber_rounded,
                        iconColor: Colors.orange,
                      ),
                    ),
                    SizedBox(
                      width: isMobile
                          ? (constraints.maxWidth - 16) / 2
                          : (constraints.maxWidth - 48) / 4,
                      child: _buildStatCard(
                        title: 'Breakdowns prevented',
                        value: '184',
                        trend: '+15%',
                        isPositive: true,
                        icon: Icons.shield_outlined,
                        iconColor: Colors.green,
                      ),
                    ),
                    SizedBox(
                      width: isMobile
                          ? (constraints.maxWidth - 16) / 2
                          : (constraints.maxWidth - 48) / 4,
                      child: _buildStatCard(
                        title: 'Warranty cost saved',
                        value: '₹3.2 Cr',
                        trend: '+22%',
                        isPositive: true,
                        icon: Icons.trending_up,
                        iconColor: Colors.purple,
                      ),
                    ),
                  ],
                );
              },
            ),
            const SizedBox(height: 24),

            // Responsive Charts Section
            LayoutBuilder(
              builder: (context, constraints) {
                // If width < 800, stack vertically.
                if (constraints.maxWidth < 800) {
                  return Column(
                    children: [
                      _buildCard(
                        title: 'Component Defect Trends',
                        child: SizedBox(
                          height: 300,
                          child: _buildBarChart(defectTrends),
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildCard(
                        title: 'Predictive vs Actual Failures',
                        child: SizedBox(
                          height: 300,
                          child: _buildLineChart(failureTrends),
                        ),
                      ),
                    ],
                  );
                } else {
                  // Desktop/Tablet: Side by side
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: _buildCard(
                          title: 'Component Defect Trends',
                          child: SizedBox(
                            height: 300,
                            child: _buildBarChart(defectTrends),
                          ),
                        ),
                      ),
                      const SizedBox(width: 24),
                      Expanded(
                        child: _buildCard(
                          title: 'Predictive vs Actual Failures',
                          child: SizedBox(
                            height: 300,
                            child: _buildLineChart(failureTrends),
                          ),
                        ),
                      ),
                    ],
                  );
                }
              },
            ),

            const SizedBox(height: 24),

            // Responsive Bottom Section
            LayoutBuilder(
              builder: (context, constraints) {
                if (constraints.maxWidth < 800) {
                  return Column(
                    children: [
                      _buildCard(
                        title: 'Root cause analysis (from CAPA / RCA)',
                        child: _buildRootCauseAnalysis(
                          _insightsData?['root_cause_analysis']
                                  as List<dynamic>? ??
                              [],
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildCard(
                        title: '',
                        noHeader: true,
                        child: _buildInsightsSection(recommendations),
                      ),
                    ],
                  );
                } else {
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        flex: 1,
                        child: _buildCard(
                          title: 'Root cause analysis (from CAPA / RCA)',
                          child: _buildRootCauseAnalysis(
                            _insightsData?['root_cause_analysis']
                                    as List<dynamic>? ??
                                [],
                          ),
                        ),
                      ),
                      const SizedBox(width: 24),
                      Expanded(
                        flex: 1,
                        child: _buildCard(
                          title: '', // Custom header inside
                          noHeader: true,
                          child: _buildInsightsSection(recommendations),
                        ),
                      ),
                    ],
                  );
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterButton(String label, {IconData? icon}) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      child: OutlinedButton.icon(
        onPressed: () {},
        icon: icon != null
            ? Icon(icon, size: 14, color: Colors.grey)
            : const SizedBox.shrink(),
        label: Text(label, style: const TextStyle(color: Colors.grey)),
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: Colors.grey[300]!),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        ),
      ),
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required String trend,
    required bool isPositive,
    required IconData icon,
    required Color iconColor,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[200]!),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: iconColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: iconColor, size: 20),
                ),
                Row(
                  children: [
                    Icon(
                      isPositive ? Icons.trending_up : Icons.trending_down,
                      color: isPositive ? Colors.green : Colors.red,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      trend,
                      style: TextStyle(
                        color: isPositive ? Colors.green : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: const TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCard({
    required String title,
    required Widget child,
    bool noHeader = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!noHeader) ...[
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 24),
          ],
          child,
        ],
      ),
    );
  }

  Widget _buildBarChart(Map<String, dynamic> data) {
    if (data.isEmpty) {
      return const Center(child: Text("No data available"));
    }

    int i = 0;
    final keys = data.keys.toList();

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 70,
        barTouchData: BarTouchData(enabled: false),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (double value, TitleMeta meta) {
                if (value.toInt() >= 0 && value.toInt() < keys.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      keys[value.toInt()],
                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
              reservedSize: 40,
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: true, reservedSize: 30),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        gridData: FlGridData(show: true, drawVerticalLine: false),
        borderData: FlBorderData(show: false),
        barGroups: data.entries.map((e) {
          final index = i++;
          return BarChartGroupData(
            x: index,
            barRods: [
              BarChartRodData(
                toY: (e.value as num).toDouble(),
                color: index % 2 == 0 ? Colors.green : Colors.blue,
                width: 20,
                borderRadius: BorderRadius.circular(4),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  Widget _buildLineChart(Map<String, dynamic> trends) {
    List<FlSpot> actualSpots = [];
    List<FlSpot> predictedSpots = [];

    if (trends.isNotEmpty) {
      final actual = trends['actual'] as List;
      final predicted = trends['predicted'] as List;

      actualSpots = actual
          .map(
            (point) => FlSpot(
              (point['x'] as num).toDouble(),
              (point['y'] as num).toDouble(),
            ),
          )
          .toList();

      predictedSpots = predicted
          .map(
            (point) => FlSpot(
              (point['x'] as num).toDouble(),
              (point['y'] as num).toDouble(),
            ),
          )
          .toList();
    } else {
      // Fallback or empty
      actualSpots = [const FlSpot(0, 0)];
      predictedSpots = [const FlSpot(0, 0)];
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true, drawVerticalLine: false),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: true, reservedSize: 30),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: true, reservedSize: 30),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          // Actual Failures (Blue)
          LineChartBarData(
            spots: actualSpots,
            isCurved: true,
            color: Colors.blue,
            barWidth: 3,
            dotData: FlDotData(show: true),
          ),
          // Predicted Failures (Green - Lower is better)
          LineChartBarData(
            spots: predictedSpots,
            isCurved: true,
            color: Colors.green,
            barWidth: 3,
            dotData: FlDotData(show: true),
          ),
        ],
      ),
    );
  }

  Widget _buildRootCauseAnalysis(List<dynamic> data) {
    if (data.isEmpty) {
      // Fallback for demo if backend hasn't updated yet
      data = [
        {'cause': 'Supplier quality', 'percent': 0.35},
        {'cause': 'Driver behaviour', 'percent': 0.40},
        {'cause': 'Design issue', 'percent': 0.15},
        {'cause': 'Others', 'percent': 0.10},
      ];
    }

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: const [
            Text('Cause', style: TextStyle(fontWeight: FontWeight.bold)),
            Text('% of cases', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        const Divider(height: 24),
        ...data.map((item) {
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 12.0),
            child: Row(
              children: [
                Expanded(flex: 2, child: Text(item['cause'] as String)),
                Expanded(
                  flex: 3,
                  child: Row(
                    children: [
                      Expanded(
                        child: LinearProgressIndicator(
                          value: item['percent'] is int
                              ? (item['percent'] as int).toDouble()
                              : (item['percent'] as double),
                          backgroundColor: Colors.grey[200],
                          color: Colors.green,
                          minHeight: 8,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        '${((item['percent'] is int ? (item['percent'] as int).toDouble() : (item['percent'] as double)) * 100).toInt()}%',
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }).toList(),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue.withOpacity(0.3)),
          ),
          child: const Text(
            'Analysis based on 1230 predictive alerts and 890 completed service records from last 30 days.',
            style: TextStyle(color: Colors.blue, fontSize: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildInsightsSection(List? recommendations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: const [
            Icon(Icons.description_outlined, color: AppTheme.textSecondary),
            SizedBox(width: 8),
            Text(
              'Insights and report',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (recommendations != null && recommendations.isNotEmpty)
          ...recommendations
              .map((r) => _buildInsightItem(r.toString()))
              .toList()
        else ...[
          _buildInsightItem('Summarised insights by model and supplier'),
          _buildInsightItem(
            'Recommendations to change brake pad material for Model X',
          ),
          _buildInsightItem('Trend of early failures in specific region'),
        ],
        const SizedBox(height: 24),
        // Chatbot prompt instead of PDF button
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.purple[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.purple.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              const Icon(Icons.auto_awesome, color: Colors.purple),
              const SizedBox(width: 12),
              Expanded(
                child: const Text(
                  "Have specific questions? Ask the AI Lead in the bottom right corner.",
                  style: TextStyle(color: Colors.purple),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Text(
            'Report generated automatically from predictive + service-completed data',
            style: TextStyle(color: AppTheme.textSecondary, fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.green.withOpacity(0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text(
                '• ROI Summary',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'For every ₹1 invested in VEXA predictive maintenance, OEM saves ₹4.2 in warranty and breakdown costs.',
                style: TextStyle(color: Colors.green),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInsightItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_outline, color: Colors.green, size: 20),
          const SizedBox(width: 8),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}
