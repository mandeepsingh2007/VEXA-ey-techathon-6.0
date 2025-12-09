import 'dart:async';
import 'package:flutter/material.dart';
import 'package:vexa/services/agent_service.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/widgets/live_vehicle_widget.dart';

class LiveSensorScreen extends StatefulWidget {
  const LiveSensorScreen({super.key});

  @override
  State<LiveSensorScreen> createState() => _LiveSensorScreenState();
}

class _LiveSensorScreenState extends State<LiveSensorScreen> {
  final AgentService _agentService = AgentService();
  bool _isLoading = true;
  Map<String, dynamic>? _vehicleData;
  Timer? _timer;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchData();
    // Poll every 5 seconds for live data
    _timer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (mounted) {
        _fetchData(silent: true);
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _fetchData({bool silent = false}) async {
    try {
      // Hardcoded vehicle ID for demo
      final data = await _agentService.fetchVehicleData('VH-1001');
      if (mounted) {
        setState(() {
          _vehicleData = data;
          if (!silent) _isLoading = false;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          // Only show error on first load, otherwise keeps retrying silently
          if (!silent) _error = e.toString();
          if (!silent) _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: AppTheme.backgroundColor,
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        backgroundColor: AppTheme.backgroundColor,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text('Error: $_error', textAlign: TextAlign.center),
          ),
        ),
      );
    }

    final telematics = _vehicleData?['latest_telematics'] ?? {};

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16),
            Text(
              'Real-Time Telemetry',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Monitoring vehicle sensors live via Digital Twin connection.',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 24),

            // The main widget
            LiveVehicleWidget(telematics: telematics),

            const SizedBox(height: 24),

            // Additional info or placeholders could go here
            _buildConnectionStatusCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectionStatusCard() {
    return Card(
      color: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.cloud_sync, color: Colors.green),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Digital Twin Active',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  Text(
                    'Syncing with vehicle ECU...',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          ],
        ),
      ),
    );
  }
}
