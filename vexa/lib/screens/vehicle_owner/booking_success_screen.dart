import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/widgets/top_progress_bar.dart';
import 'package:vexa/screens/vehicle_owner/predictive_alert_screen.dart';
import 'package:vexa/screens/vehicle_owner/slot_selection_screen.dart';

class BookingSuccessScreen extends StatelessWidget {
  const BookingSuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text('Booking Success'),
        automaticallyImplyLeading: false, // Hide back button on success
        actions: [
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () {
              // Navigate back to dashboard root
              Navigator.of(context).popUntil((route) => route.isFirst);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          TopProgressBar(
            currentStep: 2,
            onStepTap: (step) {
              if (step == 0) {
                // Go back to root (Alert)
                Navigator.of(context).popUntil((route) => route.isFirst);
                // Push Alert if needed, but usually popping to root is enough if root is Alert.
                // However, root is RoleSelection. So we need to pop until Alert?
                // Actually, Alert is pushed on top of RoleSelection.
                // Let's just pop until we find PredictiveAlertScreen or push it.
                // Simplest for demo:
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const PredictiveAlertScreen(),
                  ),
                  (route) => route.isFirst,
                );
              } else if (step == 1) {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const SlotSelectionScreen(),
                  ),
                );
              }
            },
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  const SizedBox(height: 24),
                  // Success Icon
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9), // Light green
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.check_circle_outline,
                      color: AppTheme.primaryColor,
                      size: 64,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Your preventive brake service is booked!',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Booking Details Card
                  _buildDetailsCard(context),
                  const SizedBox(height: 24),

                  // Service Progress Card
                  _buildProgressCard(context),
                  const SizedBox(height: 32),

                  // Actions
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {},
                      child: const Text('View job card details'),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () {},
                    child: const Text(
                      'Reschedule / cancel',
                      style: TextStyle(color: AppTheme.textSecondary),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailsCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            _buildDetailRow(
              Icons.calendar_today,
              'Date & time',
              'Tomorrow, 09:00 – 10:00',
            ),
            const SizedBox(height: 16),
            _buildDetailRow(
              Icons.location_on_outlined,
              'Workshop',
              'Magic Motors GTB Nagar',
            ),
            const SizedBox(height: 16),
            _buildDetailRow(Icons.receipt_long, 'Booking ID', 'VEXA-123456'),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: AppTheme.textSecondary, size: 20),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 14,
                  color: AppTheme.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildProgressCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Service progress',
              style: Theme.of(
                context,
              ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                _buildProgressStep('Booked', true, true),
                _buildProgressLine(false),
                _buildProgressStep('Vehicle received', false, false),
                _buildProgressLine(false),
                _buildProgressStep('Service\ncomplete', false, false),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressStep(String label, bool isActive, bool isFirst) {
    return Expanded(
      child: Column(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: isActive ? AppTheme.primaryColor : Colors.grey[300],
              shape: BoxShape.circle,
            ),
            child: isActive
                ? const Icon(Icons.check, color: Colors.white, size: 16)
                : Container(
                    margin: const EdgeInsets.all(8),
                    decoration: const BoxDecoration(
                      color: Colors.grey,
                      shape: BoxShape.circle,
                    ),
                  ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 10,
              color: isActive ? AppTheme.textPrimary : AppTheme.textSecondary,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressLine(bool isActive) {
    return Expanded(
      child: Container(
        height: 2,
        color: isActive ? AppTheme.primaryColor : Colors.grey[300],
        margin: const EdgeInsets.only(bottom: 20), // Align with circle center
      ),
    );
  }
}
