import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';

import 'package:vexa/services/agent_service.dart';

class JobDetailScreen extends StatelessWidget {
  const JobDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(title: const Text('Job Card Details')),
      body: const JobDetailContent(),
    );
  }
}

class JobDetailContent extends StatelessWidget {
  final Map<String, dynamic>? vehicleData;

  const JobDetailContent({super.key, this.vehicleData});

  @override
  Widget build(BuildContext context) {
    final vehicleId = vehicleData?['vehicle_id'] ?? 'DL8CAF1234';
    final diagnosis =
        vehicleData?['diagnosis_report'] ?? 'Predictive analysis pending...';
    final partName =
        vehicleData?['booking_info']?['reservation']?['article_no'] ??
        'Front brake pad set';
    final partStatus =
        vehicleData?['booking_info']?['reservation']?['available'] == true
        ? 'Reserved in store'
        : 'Check availability';

    final isJobCompleted = vehicleData?['service_status'] == 'COMPLETED';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              color: Color(0xFFE8F5E9), // Light green header
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Text(
                  'Job Card – $vehicleId',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
              border: Border.all(color: Colors.grey[200]!),
            ),
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Vehicle & Customer
                _buildSection(
                  context,
                  title: 'Vehicle & customer',
                  icon: Icons.directions_car_outlined,
                  child: Column(
                    children: [
                      _buildDetailRow('Vehicle', 'Car – $vehicleId'),
                      _buildDetailRow('VIN', '1HGBH41JXMN109186'),
                      _buildDetailRow('Odometer', '45,230 km'),
                      _buildDetailRow('Last service', '2024-09-15'),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Prediction Details
                _buildSection(
                  context,
                  title: 'Prediction details',
                  icon: Icons.show_chart,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildDetailRow(
                        'Anomaly score',
                        '0.92 (High)',
                        valueColor: AppTheme.errorColor,
                      ),
                      const Divider(height: 24),
                      _buildFormattedDiagnosis(diagnosis),
                      const SizedBox(height: 16),
                      _buildDetailRow('Source', 'Telematics + ML model'),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Parts and Labour
                _buildSection(
                  context,
                  title: 'Parts and labour',
                  icon: Icons.inventory_2_outlined,
                  child: Column(
                    children: [
                      _buildTableHeader(),
                      const Divider(height: 24),
                      _buildTableRow(partName, '1', partStatus, true),
                      const SizedBox(height: 8),
                      _buildTableRow(
                        'Labour - brake service',
                        '1',
                        'Standard',
                        false,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Bay and Technician
                _buildSection(
                  context,
                  title: 'Bay and technician',
                  icon: Icons.person_outline,
                  child: Column(
                    children: [
                      _buildDetailRow('Bay', 'Bay 2'),
                      _buildDetailRow('Technician', 'Raj (assigned)'),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Actions
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      'Mark vehicle received',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () async {
                      try {
                        // Show loading or immediate feedback
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Ending job...')),
                        );

                        // Assuming AgentService is available or we instantiate it
                        // Since JobDetailContent is stateless and no service passed, specific impl needed:
                        // Ideally passed down or use get_it/provider. For now, instantiate details:
                        // We need to import AgentService first.

                        // Note: This block assumes AgentService import is added at top
                        await AgentService().completeService(vehicleId);

                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                              'Job Ended. Feedback request sent to owner.',
                            ),
                          ),
                        );

                        Navigator.pop(context); // Go back to dashboard
                      } catch (e) {
                        ScaffoldMessenger.of(
                          context,
                        ).showSnackBar(SnackBar(content: Text('Error: $e')));
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isJobCompleted
                          ? Colors.grey
                          : AppTheme.errorColor, // Red for end job
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      'End Job',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Center(
                  child: TextButton.icon(
                    onPressed: () {},
                    icon: const Icon(
                      Icons.history,
                      size: 16,
                      color: AppTheme.primaryColor,
                    ),
                    label: const Text(
                      'View customer history',
                      style: TextStyle(color: AppTheme.primaryColor),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Widget child,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: AppTheme.textSecondary),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        child,
      ],
    );
  }

  Widget _buildDetailRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.w500,
              color: valueColor ?? AppTheme.textPrimary,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTableHeader() {
    return Row(
      children: const [
        Expanded(
          flex: 3,
          child: Text(
            'Item',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
        Expanded(
          flex: 1,
          child: Text(
            'Qty',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
        Expanded(
          flex: 2,
          child: Text(
            'Status',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildTableRow(String item, String qty, String status, bool isGreen) {
    return Row(
      children: [
        Expanded(
          flex: 3,
          child: Text(item, style: const TextStyle(fontSize: 13)),
        ),
        Expanded(
          flex: 1,
          child: Text(qty, style: const TextStyle(fontSize: 13)),
        ),
        Expanded(
          flex: 2,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: isGreen ? Colors.green[50] : Colors.grey[100],
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              status,
              style: TextStyle(
                fontSize: 11,
                color: isGreen ? Colors.green[700] : Colors.grey[700],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFormattedDiagnosis(String text) {
    if (text.isEmpty) return const SizedBox.shrink();

    final lines = text.split('\n');
    List<Widget> children = [];

    for (var line in lines) {
      line = line.trim();
      if (line.isEmpty) continue;

      if (line.startsWith('**') || line.startsWith('##')) {
        // Header style
        final cleanLine = line.replaceAll('**', '').replaceAll('##', '').trim();
        children.add(
          Padding(
            padding: const EdgeInsets.only(top: 8.0, bottom: 4.0),
            child: Text(
              cleanLine,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: AppTheme.textPrimary,
              ),
            ),
          ),
        );
      } else if (line.startsWith('-') || line.startsWith('*')) {
        // Bullet point
        children.add(
          Padding(
            padding: const EdgeInsets.only(left: 8.0, bottom: 4.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                Expanded(
                  child: Text(
                    line.substring(1).trim(),
                    style: const TextStyle(
                      fontSize: 13,
                      height: 1.4,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      } else {
        // Normal text
        children.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 4.0),
            child: Text(
              line,
              style: const TextStyle(
                fontSize: 13,
                height: 1.4,
                color: AppTheme.textPrimary,
              ),
            ),
          ),
        );
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
  }
}
