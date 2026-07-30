import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/state/view_state.dart';

final splashViewModelProvider = NotifierProvider<SplashViewModel, ViewState>(
  SplashViewModel.new,
);

class SplashViewModel extends Notifier<ViewState> {
  @override
  ViewState build() {
    return const ViewState.idle();
  }
}
