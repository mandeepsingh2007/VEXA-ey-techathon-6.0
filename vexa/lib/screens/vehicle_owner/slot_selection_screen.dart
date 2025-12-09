import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/widgets/top_progress_bar.dart';
import 'package:vexa/screens/vehicle_owner/booking_success_screen.dart';
import 'package:vexa/services/agent_service.dart';

class SlotSelectionScreen extends StatefulWidget {
  final Map<String, dynamic>? bookingInfo;

  const SlotSelectionScreen({super.key, this.bookingInfo});

  @override
  State<SlotSelectionScreen> createState() => _SlotSelectionScreenState();
}

class _SlotSelectionScreenState extends State<SlotSelectionScreen> {
  int _selectedDateIndex = 1; // Default to "Tomorrow"
  int _selectedTimeIndex = 0; // Default to first slot
  String? _recommendedTime;

  final List<String> _dates = ['Today', 'Tomorrow', '+2 days'];
  late List<String> _timeSlots;

  @override
  void initState() {
    super.initState();
    _initTimeSlots();
  }

  void _initTimeSlots() {
    final suggestedSlot = widget.bookingInfo?['slot'];

    if (suggestedSlot != null) {
      // Parse start time from ISO string if possible, or just use the string
      // For demo, we'll just append it as a recommended slot
      final start = suggestedSlot['start'];
      final end = suggestedSlot['end'];
      if (start != null && end != null) {
        // Simple formatting, assuming ISO strings
        try {
          final startTime = DateTime.parse(start);
          final endTime = DateTime.parse(end);
          _recommendedTime =
              '${startTime.hour}:${startTime.minute.toString().padLeft(2, '0')} – ${endTime.hour}:${endTime.minute.toString().padLeft(2, '0')}';
        } catch (e) {
          _recommendedTime = '$start – $end';
        }
      }
    }

    // Manual slots only, as AI slot is shown separately
    _timeSlots = ['09:00 – 10:00', '11:00 – 12:00', '16:00 – 17:00'];

    // If AI slot exists, select it by default (index -1)
    if (_recommendedTime != null) {
      _selectedTimeIndex = -1;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text('Select service slot'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          TopProgressBar(
            currentStep: 1,
            onStepTap: (step) {
              if (step == 0) {
                Navigator.pop(context); // Go back to Alert
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
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildCarDetailsCard(context),
                  const SizedBox(height: 24),
                  _buildSectionTitle(context, 'Select date'),
                  const SizedBox(height: 12),
                  _buildDateSelector(),
                  const SizedBox(height: 24),
                  _buildSectionTitle(context, 'Proposes appointment slots'),
                  const SizedBox(height: 12),
                  _buildTimeSelector(),
                  const SizedBox(height: 24),
                  _buildWorkshopCard(context),
                  const SizedBox(height: 24),
                  _buildBillEstimateCard(context),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
          _buildBottomBar(context),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
        fontWeight: FontWeight.w600,
        color: AppTheme.textPrimary,
      ),
    );
  }

  Widget _buildCarDetailsCard(BuildContext context) {
    final component =
        widget.bookingInfo?['reservation']?['component_type'] ??
        'Front brake pad';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SizedBox(
          width: double.infinity,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Car – VH-1001', // Matching the demo ID
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Text(
                '$component replacement',
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: AppTheme.textSecondary),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDateSelector() {
    return Row(
      children: List.generate(_dates.length, (index) {
        final isSelected = _selectedDateIndex == index;
        return Expanded(
          child: Padding(
            padding: EdgeInsets.only(
              right: index < _dates.length - 1 ? 12.0 : 0,
            ),
            child: InkWell(
              onTap: () => setState(() => _selectedDateIndex = index),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primaryColor : Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isSelected
                        ? AppTheme.primaryColor
                        : Colors.grey[300]!,
                  ),
                ),
                alignment: Alignment.center,
                child: Text(
                  _dates[index],
                  style: TextStyle(
                    color: isSelected ? Colors.white : AppTheme.textPrimary,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                  ),
                ),
              ),
            ),
          ),
        );
      }),
    );
  }

  Widget _buildTimeSelector() {
    return Column(
      children: [
        if (_recommendedTime != null) ...[
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.primaryColor),
            ),
            child: InkWell(
              onTap: () {
                setState(() {
                  _selectedTimeIndex = -1; // -1 indicates AI slot
                });
              },
              child: Row(
                children: [
                  Radio<int>(
                    value: -1,
                    groupValue: _selectedTimeIndex,
                    activeColor: AppTheme.primaryColor,
                    onChanged: (value) {
                      setState(() {
                        _selectedTimeIndex = value!;
                      });
                    },
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.auto_awesome,
                              size: 16,
                              color: AppTheme.primaryColor,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'AI Recommended Slot',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: AppTheme.primaryColor,
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _recommendedTime!,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 16,
                            color: AppTheme.textPrimary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 16),
        ],
        // Manual slots
        Card(
          child: Column(
            children: List.generate(_timeSlots.length, (index) {
              return RadioListTile<int>(
                value: index,
                groupValue: _selectedTimeIndex,
                onChanged: (value) =>
                    setState(() => _selectedTimeIndex = value!),
                title: Text(
                  _timeSlots[index],
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                    fontSize: 14,
                  ),
                ),
                activeColor: AppTheme.primaryColor,
                contentPadding: const EdgeInsets.symmetric(horizontal: 8),
                visualDensity: VisualDensity.compact,
              );
            }),
          ),
        ),
      ],
    );
  }

  Widget _buildWorkshopCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(
              Icons.location_on_outlined,
              color: AppTheme.primaryColor,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Magic Motors GTB Nagar (2.3 km)',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Bay 2 reserved, Technician: Raj',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBillEstimateCard(BuildContext context) {
    final partName =
        widget.bookingInfo?['reservation']?['article_no'] ?? 'OEM parts';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E9), // Light green background
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Estimated bill: ₹3,200',
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 4),
          Text(
            'Parts: $partName, Labour: standard',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  final AgentService _agentService = AgentService();
  bool _isLoading = false;

  Widget _buildBottomBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: _isLoading ? null : () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: _isLoading
                  ? null
                  : () async {
                      setState(() {
                        _isLoading = true;
                      });

                      try {
                        // Create booking payload
                        final bookingData = {
                          "slot": widget.bookingInfo?['slot'],
                          "reservation": widget.bookingInfo?['reservation'],
                          "component":
                              widget
                                  .bookingInfo?['reservation']?['component_type'] ??
                              "General Service",
                        };

                        // Call API
                        await _agentService.confirmBooking(
                          "VH-1001",
                          bookingData,
                        );

                        if (mounted) {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  const BookingSuccessScreen(),
                            ),
                          );
                        }
                      } catch (e) {
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Booking failed: $e'),
                              backgroundColor: Colors.red,
                            ),
                          );
                        }
                      } finally {
                        if (mounted) {
                          setState(() {
                            _isLoading = false;
                          });
                        }
                      }
                    },
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('Confirm booking'),
            ),
          ),
        ],
      ),
    );
  }
}
