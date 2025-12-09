import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';
import 'package:vexa/screens/service_center/job_detail_screen.dart';
import 'package:vexa/services/agent_service.dart';

class ServiceDashboardScreen extends StatefulWidget {
  const ServiceDashboardScreen({super.key});

  @override
  State<ServiceDashboardScreen> createState() => _ServiceDashboardScreenState();
}

class _ServiceDashboardScreenState extends State<ServiceDashboardScreen> {
  final AgentService _agentService = AgentService();
  bool _isLoading = true;
  Map<String, dynamic>? _vehicleData;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      final data = await _agentService.fetchVehicleData(
        'VH-1001',
        simulate: false,
      );
      setState(() {
        _vehicleData = data;
        _isLoading = false;
      });
    } catch (e) {
      print('Error fetching vehicle data: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Extract dynamic data or use defaults
    final vehicleId = _vehicleData?['vehicle_id'] ?? 'DL8CAF1234';
    final urgency = _vehicleData?['urgency'] ?? 'HIGH';
    final rawStatus = _vehicleData?['booking_info']?['status'] ?? 'Pending';
    final status =
        rawStatus.toString().substring(0, 1).toUpperCase() +
        rawStatus.toString().substring(1);

    // Find high risk component for issue description
    String issue = 'Predictive Maintenance';
    if (_vehicleData != null) {
      final health =
          _vehicleData!['health_summary']?['component_health'] as List?;
      if (health != null) {
        for (var c in health) {
          if (c['risk_level'] == 'HIGH') {
            issue = '${c['component']} – predictive';
            break;
          }
        }
      }
    }

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text('VEXA Service'),
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
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: Colors.white,
            height: 48,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                _buildTab(context, "Today's jobs", true),
                _buildTab(context, "Predictive alerts", false),
                _buildTab(context, "History", false),
                _buildTab(context, "Reports", false),
              ],
            ),
          ),
        ),
      ),
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Left Side: Job List (Flexible width, e.g., 40% or fixed width)
          Expanded(
            flex: 2,
            child: Column(
              children: [
                // Filter and Search
                Container(
                  padding: const EdgeInsets.all(16),
                  color: Colors.white,
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey[300]!),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: const [
                            Text('All'),
                            SizedBox(width: 8),
                            Icon(Icons.keyboard_arrow_down, size: 16),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              hintText: 'Search by reg. no. or customer',
                              border: InputBorder.none,
                              icon: Icon(Icons.search, color: Colors.grey),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Job List
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      _buildJobItem(
                        context,
                        time: '09:00',
                        regNo: vehicleId,
                        customer: 'Rahul',
                        issue: issue,
                        type: urgency == 'CRITICAL'
                            ? 'Breakdown'
                            : 'Preventive',
                        status: status,
                        isPreventive: urgency != 'CRITICAL',
                        isSelected: true, // Highlight the first item
                      ),
                      _buildJobItem(
                        context,
                        time: '10:30',
                        regNo: 'DL3CXY5678',
                        customer: 'Priya',
                        issue: 'Oil change',
                        type: 'Preventive',
                        status: 'In progress',
                        isPreventive: true,
                      ),
                      _buildJobItem(
                        context,
                        time: '11:00',
                        regNo: 'HR26AB9876',
                        customer: 'Amit',
                        issue: 'Engine overheating',
                        type: 'Breakdown',
                        status: 'Waiting',
                        isPreventive: false,
                      ),
                      _buildJobItem(
                        context,
                        time: '14:00',
                        regNo: 'UP32DE4567',
                        customer: 'Sneha',
                        issue: 'Tire rotation',
                        type: 'Preventive',
                        status: 'Booked',
                        isPreventive: true,
                      ),
                      _buildJobItem(
                        context,
                        time: '15:30',
                        regNo: 'DL1CAB1234',
                        customer: 'Vijay',
                        issue: 'Battery replacement',
                        type: 'Breakdown',
                        status: 'Booked',
                        isPreventive: false,
                      ),
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        child: Text(
                          'Showing 5 jobs',
                          style: TextStyle(
                            color: AppTheme.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Right Side: Job Details (Flexible width, e.g., 60%)
          Expanded(
            flex: 3,
            child: Container(
              decoration: BoxDecoration(
                border: Border(left: BorderSide(color: Colors.grey[200]!)),
              ),
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _vehicleData == null
                  ? const Center(child: Text("Failed to load vehicle data"))
                  : JobDetailContent(vehicleData: _vehicleData),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTab(BuildContext context, String title, bool isActive) {
    return Container(
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: isActive ? AppTheme.primaryColor : Colors.transparent,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        title,
        style: TextStyle(
          color: isActive ? Colors.white : AppTheme.textSecondary,
          fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
          fontSize: 14,
        ),
      ),
    );
  }

  Widget _buildJobItem(
    BuildContext context, {
    required String time,
    required String regNo,
    required String customer,
    required String issue,
    required String type,
    required String status,
    required bool isPreventive,
    bool isSelected = false,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isSelected ? Colors.green[50] : Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isSelected
              ? AppTheme.primaryColor.withOpacity(0.3)
              : Colors.grey[200]!,
        ),
      ),
      child: InkWell(
        onTap: () {
          // In a real app, this would update the selected job state
        },
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Row 1: Time and Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    time,
                    style: const TextStyle(
                      fontWeight: FontWeight.w500,
                      fontSize: 13,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: isPreventive ? Colors.blue[50] : Colors.red[50],
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      type,
                      style: TextStyle(
                        color: isPreventive ? Colors.blue : Colors.red,
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              // Row 2: Reg No (Green)
              Text(
                regNo,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: AppTheme.primaryColor,
                ),
              ),
              const SizedBox(height: 4),
              // Row 3: Customer and Issue
              Text(
                '$customer • $issue',
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 8),
              // Row 4: Status
              Row(
                children: [
                  const Icon(Icons.info_outline, size: 14, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    status,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
