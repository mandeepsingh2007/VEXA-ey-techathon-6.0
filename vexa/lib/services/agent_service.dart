import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class AgentService {
  // Use 10.0.2.2 for Android Emulator, localhost for iOS/Web
  static const String baseUrl = kIsWeb
      ? 'http://localhost:8000'
      : 'http://10.0.2.2:8000';

  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );

      print('Login Response: ${response.body}');

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to login: ${response.body}');
      }
    } catch (e) {
      print('Login error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> fetchVehicleData(
    String vehicleId, {
    bool simulate = true,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/vehicle/$vehicleId/full_data?simulate=$simulate'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load vehicle data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to agent backend: $e');
    }
  }

  Future<void> confirmBooking(
    String vehicleId,
    Map<String, dynamic> bookingData,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/vehicle/$vehicleId/book'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(bookingData),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to confirm booking: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error confirming booking: $e');
    }
  }

  Future<void> completeService(String vehicleId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/vehicle/$vehicleId/complete_service'),
      );
      if (response.statusCode != 200) {
        throw Exception('Failed to complete service');
      }
    } catch (e) {
      throw Exception('Error completing service: $e');
    }
  }

  Future<void> submitFeedback(
    String vehicleId,
    int rating,
    String comments,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/vehicle/$vehicleId/feedback'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"rating": rating, "comments": comments}),
      );
      if (response.statusCode != 200) {
        throw Exception('Failed to submit feedback');
      }
    } catch (e) {
      throw Exception('Error submitting feedback: $e');
    }
  }

  Future<Map<String, dynamic>> fetchManufacturingInsights() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/manufacturing/insights'),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load manufacturing insights');
      }
    } catch (e) {
      throw Exception('Error fetching insights: $e');
    }
  }

  Future<String> chatWithManufacturingAgent(String query) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/manufacturing/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"query": query}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['response'] ?? "No response";
      } else {
        throw Exception('Failed to chat with agent');
      }
    } catch (e) {
      throw Exception('Error chatting with agent: $e');
    }
  }

  Future<void> simulateSecurityAttack() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/ueba/simulate_attack'),
      );
      if (response.statusCode != 200) {
        throw Exception('Failed to simulate attack');
      }
    } catch (e) {
      throw Exception('Error simulating attack: $e');
    }
  }

  Future<void> resetSecurityStatus() async {
    try {
      await http.post(Uri.parse('$baseUrl/ueba/reset'));
    } catch (e) {
      print('Reset error: $e');
    }
  }

  Future<Map<String, dynamic>> getSecurityStatus() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/ueba/status'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get security status');
      }
    } catch (e) {
      // Fail gracefully
      return {"risk_level": "LOW", "anomalies": []};
    }
  }
}
