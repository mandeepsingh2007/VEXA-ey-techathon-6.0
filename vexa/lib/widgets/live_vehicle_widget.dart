import 'package:flutter/material.dart';
import 'package:vexa/theme/app_theme.dart';

class LiveVehicleWidget extends StatelessWidget {
  final Map<String, dynamic> telematics;

  const LiveVehicleWidget({super.key, required this.telematics});

  @override
  Widget build(BuildContext context) {
    // Extract formatted values
    final double speed = (telematics['speed_kmph'] ?? 0.0).toDouble();
    final int rpm = (telematics['engine_rpm'] ?? 0).toInt();
    final double fuel = (telematics['fuel_level_pct'] ?? 0.0).toDouble();
    final double battery = (telematics['battery_voltage_v'] ?? 0.0).toDouble();

    // New Fields
    final double odometer = (telematics['odometer_km'] ?? 0.0).toDouble();
    final double coolantTemp = (telematics['engine_coolant_temp_c'] ?? 0.0)
        .toDouble();
    final double oilTemp = (telematics['engine_oil_temp_c'] ?? 0.0).toDouble();
    final String mode = telematics['driving_mode'] ?? 'NORMAL';

    // Tires
    final double fl = (telematics['tire_pressure_fl_psi'] ?? 32.0).toDouble();
    final double fr = (telematics['tire_pressure_fr_psi'] ?? 32.0).toDouble();
    final double rl = (telematics['tire_pressure_rl_psi'] ?? 32.0).toDouble();
    final double rr = (telematics['tire_pressure_rr_psi'] ?? 32.0).toDouble();

    // Dynamics
    final double steering = (telematics['steering_angle_deg'] ?? 0.0)
        .toDouble();
    final double brake = (telematics['brake_pedal_pressure'] ?? 0.0).toDouble();

    return Column(
      children: [
        // Main Dashboard Card
        Container(
          padding: const EdgeInsets.all(24.0),
          decoration: BoxDecoration(
            color: AppTheme.surfaceColor,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 15,
                offset: const Offset(0, 5),
              ),
            ],
            border: Border.all(color: Colors.grey.withOpacity(0.1)),
          ),
          child: Column(
            children: [
              _buildHeader(mode),
              const SizedBox(height: 32),

              // Speed & RPM
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        speed.toStringAsFixed(0),
                        style: const TextStyle(
                          color: AppTheme.textPrimary,
                          fontSize: 72,
                          fontWeight: FontWeight.w800,
                          height: 0.9,
                          letterSpacing: -2,
                        ),
                      ),
                      Text(
                        'km/h',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  _buildRPMGauge(rpm),
                ],
              ),
              const SizedBox(height: 32),

              // Key Stats Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildStatItem(
                    Icons.local_gas_station,
                    '${fuel.toStringAsFixed(0)}%',
                    'Fuel',
                    Colors.blue,
                  ),
                  _buildStatItem(
                    Icons.thermostat,
                    '${coolantTemp.toStringAsFixed(0)}°C',
                    'Coolant',
                    Colors.orange,
                  ),
                  _buildStatItem(
                    Icons.oil_barrel,
                    '${oilTemp.toStringAsFixed(0)}°C',
                    'Oil',
                    Colors.redAccent,
                  ),
                  _buildStatItem(
                    Icons.bolt,
                    '${battery.toStringAsFixed(1)}V',
                    'Battery',
                    Colors.purple,
                  ),
                ],
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Secondary Info Grid
        Row(
          children: [
            // Tire Pressure Card
            Expanded(
              flex: 3,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceColor,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.grey.withOpacity(0.1)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Tire Pressure',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildTirePair('FL', fl, 'RL', rl),
                        Icon(
                          Icons.directions_car,
                          size: 48,
                          color: Colors.grey[300],
                        ),
                        _buildTirePair('FR', fr, 'RR', rr),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 16),

            // Dynamics / Odometer Card
            Expanded(
              flex: 2,
              child: Container(
                height: 140, // Match height roughly
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceColor,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.grey.withOpacity(0.1)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Odometer',
                          style: TextStyle(
                            color: AppTheme.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                        Text(
                          '${odometer.toStringAsFixed(1)} km',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    const Divider(),
                    Row(
                      children: [
                        Icon(
                          Icons.u_turn_left,
                          size: 16,
                          color: AppTheme.textSecondary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${steering.toStringAsFixed(1)}°',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(width: 8),
                        Icon(
                          Icons.speed,
                          size: 16,
                          color: AppTheme.textSecondary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${brake.toStringAsFixed(0)}%',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHeader(String mode) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.sensors,
                color: AppTheme.primaryColor,
                size: 16,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'LIVE TELEMETRY',
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.black,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            mode,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRPMGauge(int rpm) {
    return Stack(
      alignment: Alignment.center,
      children: [
        SizedBox(
          height: 80,
          width: 80,
          child: CircularProgressIndicator(
            value: rpm / 8000.0,
            strokeWidth: 8,
            backgroundColor: Colors.grey[100],
            valueColor: const AlwaysStoppedAnimation<Color>(
              AppTheme.primaryColor,
            ),
          ),
        ),
        Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              (rpm / 1000).toStringAsFixed(1),
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontWeight: FontWeight.bold,
                fontSize: 20,
              ),
            ),
            const Text(
              'RPM\nx1000',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 9,
                height: 1,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatItem(
    IconData icon,
    String value,
    String label,
    Color color,
  ) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        Text(
          label,
          style: TextStyle(color: AppTheme.textSecondary, fontSize: 11),
        ),
      ],
    );
  }

  Widget _buildTirePair(String l1, double v1, String l2, double v2) {
    return Column(
      children: [
        _buildTireVal(l1, v1),
        const SizedBox(height: 16),
        _buildTireVal(l2, v2),
      ],
    );
  }

  Widget _buildTireVal(String label, double val) {
    final bool warning = val < 30 || val > 40;
    return Column(
      children: [
        Text(
          '${val.toStringAsFixed(1)}',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: warning ? Colors.red : AppTheme.textPrimary,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 10, color: AppTheme.textSecondary),
        ),
      ],
    );
  }
}
