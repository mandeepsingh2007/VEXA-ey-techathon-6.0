import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';

class TopProgressBar extends StatelessWidget {
  final int currentStep; // 0: Alert, 1: Slot, 2: Success
  final Function(int)? onStepTap;

  const TopProgressBar({super.key, required this.currentStep, this.onStepTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.white,
      child: Row(
        children: [
          _buildStep(context, 0, 'Predictive\nAlert'),
          const SizedBox(width: 8),
          _buildStep(context, 1, 'Slot Selection'),
          const SizedBox(width: 8),
          _buildStep(context, 2, 'Booking\nSuccess'),
        ],
      ),
    );
  }

  Widget _buildStep(BuildContext context, int stepIndex, String title) {
    final isActive = stepIndex == currentStep;

    return Expanded(
      child: GestureDetector(
        onTap: () => onStepTap?.call(stepIndex),
        child: Container(
          height: 50,
          decoration: BoxDecoration(
            color: isActive ? AppTheme.primaryColor : const Color(0xFFF5F5F5),
            borderRadius: BorderRadius.circular(8),
          ),
          alignment: Alignment.center,
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isActive ? Colors.white : const Color(0xFF424242),
              fontSize: 12,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ),
      ),
    );
  }
}
