import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/widgets/top_progress_bar.dart';
import 'package:vexa/screens/vehicle_owner/slot_selection_screen.dart';
import 'package:vexa/screens/vehicle_owner/booking_success_screen.dart';
import 'package:vexa/services/agent_service.dart';

class PredictiveAlertScreen extends StatefulWidget {
  const PredictiveAlertScreen({super.key});

  @override
  State<PredictiveAlertScreen> createState() => _PredictiveAlertScreenState();
}

class _PredictiveAlertScreenState extends State<PredictiveAlertScreen> {
  final AgentService _agentService = AgentService();
  bool _isLoading = true;
  Map<String, dynamic>? _vehicleData;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      // Hardcoded vehicle ID for demo
      final data = await _agentService.fetchVehicleData('VH-1001');
      if (mounted) {
        setState(() {
          _vehicleData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
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
        body: Center(child: Text('Error: $_error')),
      );
    }

    final customerMessage =
        _vehicleData?['customer_message']?['english'] ??
        'No alert message available.';
    final urgency = _vehicleData?['urgency'] ?? 'LOW';
    final vehicleId = _vehicleData?['vehicle_id'] ?? 'Unknown';

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: Column(
        children: [
          TopProgressBar(
            currentStep: 0,
            onStepTap: (step) {
              if (step == 1) {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => SlotSelectionScreen(
                      bookingInfo: _vehicleData?['booking_info'],
                    ),
                  ),
                );
              } else if (step == 2) {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const BookingSuccessScreen(),
                  ),
                );
              }
            },
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  // Check service status
                  if (_vehicleData?['service_status'] == 'COMPLETED')
                    _buildFeedbackCard(context)
                  else ...[
                    _buildAlertCard(
                      context,
                      vehicleId,
                      customerMessage,
                      urgency,
                    ),
                    const SizedBox(height: 16),
                    if (_vehicleData?['driver_tips'] != null) ...[
                      const SizedBox(height: 16),
                      _buildDriverTipsCard(
                        context,
                        _vehicleData!['driver_tips'],
                      ),
                    ],
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // State for feedback
  int _rating = 0;
  final TextEditingController _commentController = TextEditingController();
  bool _feedbackSubmitted = false;

  Widget _buildFeedbackCard(BuildContext context) {
    if (_feedbackSubmitted) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            children: [
              const Icon(Icons.check_circle, size: 64, color: Colors.green),
              const SizedBox(height: 16),
              Text(
                'Thank you for your feedback!',
                style: Theme.of(context).textTheme.titleLarge,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Service Completed',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppTheme.primaryColor,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Your vehicle service is done. Please rate your experience.',
            ),
            const Divider(height: 24),
            Center(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: List.generate(5, (index) {
                  return IconButton(
                    icon: Icon(
                      index < _rating ? Icons.star : Icons.star_border,
                      size: 40,
                      color: Colors.amber,
                    ),
                    onPressed: () {
                      setState(() {
                        _rating = index + 1;
                      });
                    },
                  );
                }),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _commentController,
              decoration: const InputDecoration(
                hintText: 'Add a comment (optional)',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _rating == 0
                    ? null
                    : () async {
                        try {
                          await _agentService.submitFeedback(
                            'VH-1001',
                            _rating,
                            _commentController.text,
                          );
                          setState(() {
                            _feedbackSubmitted = true;
                          });
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Feedback Submitted!'),
                            ),
                          );
                        } catch (e) {
                          ScaffoldMessenger.of(
                            context,
                          ).showSnackBar(SnackBar(content: Text('Error: $e')));
                        }
                      },
                child: const Text('Submit Feedback'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertCard(
    BuildContext context,
    String vehicleId,
    String message,
    String urgency,
  ) {
    final isRisk = urgency == 'HIGH' || urgency == 'CRITICAL';
    final color = isRisk ? AppTheme.errorColor : AppTheme.primaryColor;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: color),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Health Alert for $vehicleId',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimary,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isRisk ? Colors.red[50] : Colors.green[50],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  urgency,
                  style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          // Simple formatted message if it contains newlines, or just text
          ...message.split('\n').map((line) {
            line = line.trim();
            if (line.isEmpty) return const SizedBox.shrink();
            return Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (line.startsWith('⚠') || line.startsWith('-'))
                    Text(
                      '• ',
                      style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  Expanded(
                    child: Text(
                      line.replaceAll('⚠', '').trim(),
                      style: const TextStyle(
                        fontSize: 14,
                        color: AppTheme.textPrimary,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  'Est. cost',
                  '₹3,200',
                  icon: Icons.attach_money,
                ),
              ),
              Expanded(
                child: _buildStatItem(
                  'Time to service',
                  '45–60 mins',
                  icon: Icons.timer_outlined,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => SlotSelectionScreen(
                      bookingInfo: _vehicleData?['booking_info'],
                    ),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: color,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Book safe slot'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDriverTipsCard(BuildContext context, String tips) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.withOpacity(0.2)),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.drive_eta, color: Colors.blue),
              SizedBox(width: 8),
              Text(
                'Driver Coaching Tips',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          const Divider(height: 24, color: Colors.blue),
          // Parse tips similar to diagnosis
          ...tips.split('\n').map((line) {
            line = line.trim();
            if (line.isEmpty) return const SizedBox.shrink();
            return Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (line.startsWith('-') || line.startsWith('*'))
                    const Text(
                      '• ',
                      style: TextStyle(
                        color: Colors.blue,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  Expanded(
                    child: Text(
                      line.replaceAll(RegExp(r'^[-*]'), '').trim(),
                      style: const TextStyle(
                        fontSize: 14,
                        color: AppTheme.textPrimary,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, {IconData? icon}) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.backgroundColor,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey[300]!),
          ),
          child: Icon(
            icon ?? Icons.info_outline,
            size: 20,
            color: AppTheme.textSecondary,
          ),
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 12,
              ),
            ),
            Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
          ],
        ),
      ],
    );
  }
}
