import 'package:flutter/material.dart';
import 'package:vexa/screens/splash_screen.dart';
import 'package:vexa/theme/app_theme.dart';

void main() {
  runApp(const VexaApp());
}

class VexaApp extends StatelessWidget {
  const VexaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VEXA',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const SplashScreen(),
    );
  }
}
