import 'package:flutter/material.dart';
import 'package:vexa/screens/vehicle_owner/live_sensor_screen.dart';
import 'package:vexa/screens/vehicle_owner/predictive_alert_screen.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/services/agent_service.dart';
import 'dart:async';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;
  final AgentService _agentService = AgentService();
  Timer? _securityTimer;
  bool _isRiskHigh = false;
  String? _riskType;

  final List<Widget> _pages = [
    const LiveSensorScreen(),
    const PredictiveAlertScreen(),
    const Center(child: Text("Profile / Settings")), // Placeholder
  ];

  @override
  void initState() {
    super.initState();
    _startSecurityMonitor();
  }

  @override
  void dispose() {
    _securityTimer?.cancel();
    super.dispose();
  }

  void _startSecurityMonitor() {
    _securityTimer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      if (!mounted) return;
      try {
        final status = await _agentService.getSecurityStatus();
        if (!mounted) return;

        final isCritical = status['risk_level'] == 'CRITICAL';

        if (isCritical && !_isRiskHigh) {
          // Transition to High Risk
          final anomalies = status['anomalies'] as List;
          if (mounted) {
            setState(() {
              _isRiskHigh = true;
              _riskType = anomalies.isNotEmpty
                  ? anomalies[0]['type']
                  : 'UNKNOWN';
            });
            _showSecurityAlert(_riskType ?? "Intrusion Detected");
          }
        } else if (!isCritical && _isRiskHigh) {
          if (mounted) {
            setState(() {
              _isRiskHigh = false;
              _riskType = null;
            });
          }
        }
      } catch (e) {
        // silent fail
      }
    });
  }

  void _showSecurityAlert(String type) {
    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Row(
          children: const [
            Icon(Icons.warning, color: Colors.red),
            SizedBox(width: 8),
            Text('Security Alert'),
          ],
        ),
        content: Text(
          'UEBA Agent detected abnormal behavior:\n\nScheduling Agent suddenly tries to access vehicle telematics data\n\nAccess blocked to protect vehicle data.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // Show patching message
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'Patching vulnerability & Resetting protocols...',
                  ),
                  duration: Duration(seconds: 3),
                ),
              );
              // Auto-reset after 3 seconds
              Future.delayed(const Duration(seconds: 3), () async {
                await _agentService.resetSecurityStatus();
              });
            },
            child: const Text('ACKNOWLEDGE'),
          ),
        ],
      ),
    );
  }

  Future<void> _triggerSimulation() async {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Simulating cyber-attack...')));
    await _agentService.simulateSecurityAttack();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VEXA Assist'),
        centerTitle: true,
        backgroundColor: AppTheme.surfaceColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(
            _isRiskHigh ? Icons.gpp_bad : Icons.shield,
            color: _isRiskHigh ? Colors.red : Colors.green[700],
          ),
          tooltip: 'UEBA Security Status',
          onPressed: () {
            if (!_isRiskHigh) {
              // Hidden demo trigger on tap when safe
              _triggerSimulation();
            } else {
              _showSecurityAlert(_riskType ?? "Intrusion");
            }
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none),
            onPressed: () {},
          ),
          const Padding(
            padding: EdgeInsets.only(right: 16.0),
            child: CircleAvatar(
              radius: 16,
              backgroundColor: Color(0xFFE0E0E0),
              child: Icon(Icons.person, color: Colors.grey),
            ),
          ),
        ],
      ),
      body: IndexedStack(index: _currentIndex, children: _pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        backgroundColor: Colors.white,
        elevation: 3,
        shadowColor: Colors.black26,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.speed), label: 'Live Data'),
          NavigationDestination(
            icon: Icon(Icons.health_and_safety),
            label: 'Alerts',
          ),
          NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}
