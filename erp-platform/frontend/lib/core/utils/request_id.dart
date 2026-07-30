import 'package:flutter/foundation.dart';

String createRequestId() {
  return '${DateTime.now().microsecondsSinceEpoch}-${UniqueKey()}';
}
