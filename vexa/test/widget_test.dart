// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'dart:ui'; // Required for Size

import 'package:vexa/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const VexaApp());

    // Verify that the role selection title is present.
    expect(find.text('Select your role'), findsOneWidget);

    // Tap 'Vehicle Owner'
    await tester.tap(find.text('Vehicle Owner'));
    await tester.pumpAndSettle();

    // Verify Dashboard
    expect(find.text('VEXA Assist'), findsOneWidget);

    // Tap 'Book safe slot'
    await tester.tap(find.text('Book safe slot'));
    await tester.pumpAndSettle();

    // Verify Slot Selection Screen
    expect(find.text('Select service slot'), findsOneWidget);

    // Tap 'Confirm booking'
    await tester.tap(find.text('Confirm booking'));
    await tester.pumpAndSettle();

    // Verify Booking Success Screen
    expect(find.text('Booking Success'), findsOneWidget);
    expect(
      find.text('Your preventive brake service is booked!'),
      findsOneWidget,
    );
  });

  testWidgets('Service Center flow smoke test', (WidgetTester tester) async {
    // Set a larger screen size for the split-view dashboard
    tester.view.physicalSize = const Size(1280, 800);
    tester.view.devicePixelRatio = 1.0;

    // Build our app and trigger a frame.
    await tester.pumpWidget(const VexaApp());

    // Verify Role Selection
    expect(find.text('Select your role'), findsOneWidget);

    // Tap 'Service Center'
    await tester.tap(find.text('Service Center'));
    await tester.pumpAndSettle();

    // Verify Service Dashboard
    expect(find.text('VEXA Service'), findsOneWidget);
    expect(find.text("Today's jobs"), findsOneWidget);

    // Verify Job List is present
    expect(find.text('DL8CAF1234'), findsOneWidget);

    // Verify Job Details are present (Split View)
    // Note: 'Job Card Details' was the AppBar title of the separate screen, which is gone.
    // We check for the content header instead.
    expect(find.text('Job Card – Predictive Brake Service'), findsOneWidget);

    // Reset window size
    // Reset window size
    addTearDown(tester.view.resetPhysicalSize);
  });

  testWidgets('Manufacturing Company flow smoke test', (
    WidgetTester tester,
  ) async {
    // Set a larger screen size for the dashboard
    tester.view.physicalSize = const Size(1280, 800);
    tester.view.devicePixelRatio = 1.0;

    // Build our app and trigger a frame.
    await tester.pumpWidget(const VexaApp());

    // Verify Role Selection
    expect(find.text('Select your role'), findsOneWidget);

    // Tap 'Manufacturing Company'
    await tester.tap(find.text('Manufacturing Company'));
    await tester.pumpAndSettle();

    // Verify Manufacturing Dashboard
    expect(find.text('VEXA OEM Insights'), findsOneWidget);
    expect(find.text('Vehicles monitored'), findsOneWidget);
    expect(find.text('Top 5 failure components'), findsOneWidget);
    expect(find.text('Root cause analysis (from CAPA / RCA)'), findsOneWidget);

    // Reset window size
    addTearDown(tester.view.resetPhysicalSize);
  });
}
