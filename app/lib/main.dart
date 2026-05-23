import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'firebase_options.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/app_colors.dart';
import 'services/firestore_service.dart';
import 'theme_provider.dart';
import 'globals.dart';
import 'login.dart';
import 'dash.dart';
import 'history.dart';
import 'notification.dart';
import 'settings.dart';

/// Global navigator key to navigate and show overlays from anywhere in the app
final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

/// Global [ThemeProvider] instance shared across the app.
/// Screens can access it via [MyApp.themeProvider].
final ThemeProvider _themeProvider = ThemeProvider();

/// This handler runs when the app is fully terminated and a push notification arrives.
/// It MUST be a top-level function (not inside a class).
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  debugPrint('FCM: Background message received — ${message.messageId}');
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Register the background message handler
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  
  // Load persisted theme preference BEFORE rendering MaterialApp
  await _themeProvider.loadThemePreference();
  
  // Restore persisted device ID so screens don't show "Device not linked"
  await loadDeviceId();
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  /// Public accessor so any screen can toggle the theme
  /// via `MyApp.themeProvider.toggleTheme(...)`.
  static ThemeProvider get themeProvider => _themeProvider;

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _themeProvider,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Smart Baby Band',
          navigatorKey: navigatorKey,
          themeMode: _themeProvider.themeMode,
          theme: AppTheme.light,
          darkTheme: AppTheme.dark,
          home: FirebaseAuth.instance.currentUser != null 
              ? const DashboardPage() 
              : const LoginPage(),
          routes: {
            '/login': (context) => const LoginPage(),
            '/dashboard': (context) => const DashboardPage(),
            '/history': (context) => const HistoryPage(),
            '/notifications': (context) => const NotificationsPage(),
            '/settings': (context) => const SettingsPage(),
          },
          builder: (context, child) {
            return GlobalAlertListener(child: child!);
          },
        );
      },
    );
  }
}

/// GlobalAlertListener wraps the entire Navigator tree to listen for real-time unread 
/// critical alerts from Firestore and manages heads-up overlays inside the Navigator.
class GlobalAlertListener extends StatefulWidget {
  final Widget child;
  const GlobalAlertListener({super.key, required this.child});

  @override
  State<GlobalAlertListener> createState() => _GlobalAlertListenerState();
}

class _GlobalAlertListenerState extends State<GlobalAlertListener> {
  StreamSubscription? _authSubscription;
  StreamSubscription? _notificationSubscription;
  String? _currentUserId;

  // Cache to track which notification IDs we have already shown during this app runtime session
  final Set<String> _seenNotificationIds = {};
  
  // Reference to the currently active heads-up overlay entry
  OverlayEntry? _activeOverlayEntry;

  @override
  void initState() {
    super.initState();
    _initAuthListener();
  }

  void _initAuthListener() {
    _authSubscription = FirebaseAuth.instance.authStateChanges().listen((user) {
      if (user != null) {
        if (_currentUserId != user.uid) {
          _currentUserId = user.uid;
          _subscribeToNotifications(user.uid);
        }
      } else {
        _currentUserId = null;
        _unsubscribeNotifications();
        _removeActiveOverlay();
      }
    });
  }

  void _subscribeToNotifications(String userId) {
    _unsubscribeNotifications();
    
    // Ignore old alerts created before the app run session (within last 15 seconds)
    final DateTime appSessionStartTime = DateTime.now().subtract(const Duration(seconds: 15));

    _notificationSubscription = FirestoreService.getNotifications(userId).listen((notifications) {
      if (notifications.isEmpty) return;

      // Check the latest alert
      final latest = notifications.first;
      final String id = latest['id'] ?? '';
      final bool isRead = latest['is_read'] ?? false;
      
      DateTime createdAt = DateTime.now();
      final ts = latest['created_at'];
      if (ts is Timestamp) {
        createdAt = ts.toDate();
      }

      // If it is unread, not seen during this run, and was triggered during the active session
      if (!isRead && !_seenNotificationIds.contains(id) && createdAt.isAfter(appSessionStartTime)) {
        _seenNotificationIds.add(id);
        _triggerHeadsUpDisplay(latest);
      }
    });
  }

  void _unsubscribeNotifications() {
    _notificationSubscription?.cancel();
    _notificationSubscription = null;
  }

  void _triggerHeadsUpDisplay(Map<String, dynamic> alert) {
    _removeActiveOverlay();

    final overlayState = navigatorKey.currentState?.overlay;
    if (overlayState == null) {
      debugPrint("GlobalAlertListener: Overlay state not initialized yet. Skipping HUD banner.");
      return;
    }

    _activeOverlayEntry = OverlayEntry(
      builder: (context) {
        return GlobalHeadsUpBanner(
          alert: alert,
          onDismiss: () {
            _removeActiveOverlay();
          },
        );
      },
    );

    overlayState.insert(_activeOverlayEntry!);
  }

  void _removeActiveOverlay() {
    _activeOverlayEntry?.remove();
    _activeOverlayEntry = null;
  }

  @override
  void dispose() {
    _authSubscription?.cancel();
    _unsubscribeNotifications();
    _removeActiveOverlay();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Simply render the child Navigator, keeping this listener completely transparent and decoupled
    return widget.child;
  }
}

/// GlobalHeadsUpBanner is rendered inside the root Overlay of the Navigator,
/// guaranteeing proper context ancestors (Overlay, MediaQuery, MaterialLocalizations).
class GlobalHeadsUpBanner extends StatefulWidget {
  final Map<String, dynamic> alert;
  final VoidCallback onDismiss;

  const GlobalHeadsUpBanner({
    super.key,
    required this.alert,
    required this.onDismiss,
  });

  @override
  State<GlobalHeadsUpBanner> createState() => _GlobalHeadsUpBannerState();
}

class _GlobalHeadsUpBannerState extends State<GlobalHeadsUpBanner> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _offsetAnimation;
  Timer? _autoHideTimer;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _offsetAnimation = Tween<Offset>(
      begin: const Offset(0, -1.5), // Positioned fully offscreen above the notch
      end: const Offset(0, 0),       // Slide down into standard view
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutBack, // Bouncy entry animation
    ));

    // Trigger sliding animation
    _controller.forward();

    // Auto-hide the heads-up banner after 6 seconds
    _autoHideTimer = Timer(const Duration(seconds: 6), _dismissBanner);
  }

  void _dismissBanner() async {
    _autoHideTimer?.cancel();
    if (mounted) {
      await _controller.reverse();
    }
    widget.onDismiss();
  }

  @override
  void dispose() {
    _autoHideTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    final alert = widget.alert;
    final String id = alert['id'] ?? '';
    final String title = alert['title'] ?? 'Emergency Alert';
    final String message = alert['message'] ?? '';
    final String type = alert['type'] ?? 'info';

    final Color alertColor = type == 'critical' 
        ? AppColors.chartRed 
        : (type == 'warning' ? AppColors.chartOrange : AppColors.chartBlue);

    return SafeArea(
      child: Align(
        alignment: Alignment.topCenter,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: SlideTransition(
            position: _offsetAnimation,
            child: Material(
              color: Colors.transparent,
              child: Container(
                decoration: BoxDecoration(
                  color: isDark ? Colors.grey[900] : Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: alertColor.withValues(alpha: 0.4),
                    width: 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: alertColor.withValues(alpha: 0.25),
                      blurRadius: 20,
                      spreadRadius: 2,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(20),
                    onTap: () {
                      _dismissBanner();
                      navigatorKey.currentState?.pushNamed('/notifications');
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Left-side dynamic warning icon
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: alertColor.withValues(alpha: 0.15),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              type == 'critical' 
                                  ? Icons.warning_rounded 
                                  : (type == 'warning' ? Icons.thermostat_rounded : Icons.info_rounded),
                              color: alertColor,
                              size: 26,
                            ),
                          ),
                          const SizedBox(width: 12),

                          // Alert description text
                          Expanded(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  title,
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: alertColor,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  message,
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    color: theme.colorScheme.onSurfaceVariant,
                                    height: 1.3,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),

                          // Quick actions (Close and Mark as Read)
                          Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.close_rounded, size: 20),
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                                onPressed: _dismissBanner,
                              ),
                              const SizedBox(height: 10),
                              IconButton(
                                icon: Icon(Icons.check_circle_outline_rounded, color: alertColor, size: 20),
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                                tooltip: 'Mark as read',
                                onPressed: () async {
                                  _dismissBanner();
                                  await FirestoreService.markNotificationAsRead(id);
                                },
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
