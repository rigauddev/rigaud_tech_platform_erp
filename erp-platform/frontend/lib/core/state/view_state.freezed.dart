// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'view_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ViewState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ViewState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ViewState()';
}


}

/// @nodoc
class $ViewStateCopyWith<$Res>  {
$ViewStateCopyWith(ViewState _, $Res Function(ViewState) __);
}


/// Adds pattern-matching-related methods to [ViewState].
extension ViewStatePatterns on ViewState {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( ViewStateIdle value)?  idle,TResult Function( ViewStateLoading value)?  loading,TResult Function( ViewStateError value)?  error,required TResult orElse(),}){
final _that = this;
switch (_that) {
case ViewStateIdle() when idle != null:
return idle(_that);case ViewStateLoading() when loading != null:
return loading(_that);case ViewStateError() when error != null:
return error(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( ViewStateIdle value)  idle,required TResult Function( ViewStateLoading value)  loading,required TResult Function( ViewStateError value)  error,}){
final _that = this;
switch (_that) {
case ViewStateIdle():
return idle(_that);case ViewStateLoading():
return loading(_that);case ViewStateError():
return error(_that);}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( ViewStateIdle value)?  idle,TResult? Function( ViewStateLoading value)?  loading,TResult? Function( ViewStateError value)?  error,}){
final _that = this;
switch (_that) {
case ViewStateIdle() when idle != null:
return idle(_that);case ViewStateLoading() when loading != null:
return loading(_that);case ViewStateError() when error != null:
return error(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function()?  idle,TResult Function()?  loading,TResult Function( String message)?  error,required TResult orElse(),}) {final _that = this;
switch (_that) {
case ViewStateIdle() when idle != null:
return idle();case ViewStateLoading() when loading != null:
return loading();case ViewStateError() when error != null:
return error(_that.message);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function()  idle,required TResult Function()  loading,required TResult Function( String message)  error,}) {final _that = this;
switch (_that) {
case ViewStateIdle():
return idle();case ViewStateLoading():
return loading();case ViewStateError():
return error(_that.message);}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function()?  idle,TResult? Function()?  loading,TResult? Function( String message)?  error,}) {final _that = this;
switch (_that) {
case ViewStateIdle() when idle != null:
return idle();case ViewStateLoading() when loading != null:
return loading();case ViewStateError() when error != null:
return error(_that.message);case _:
  return null;

}
}

}

/// @nodoc


class ViewStateIdle implements ViewState {
  const ViewStateIdle();







@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ViewStateIdle);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ViewState.idle()';
}


}




/// @nodoc


class ViewStateLoading implements ViewState {
  const ViewStateLoading();







@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ViewStateLoading);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ViewState.loading()';
}


}




/// @nodoc


class ViewStateError implements ViewState {
  const ViewStateError(this.message);


 final  String message;

/// Create a copy of ViewState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ViewStateErrorCopyWith<ViewStateError> get copyWith => _$ViewStateErrorCopyWithImpl<ViewStateError>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ViewStateError&&(identical(other.message, message) || other.message == message));
}


@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'ViewState.error(message: $message)';
}


}

/// @nodoc
abstract mixin class $ViewStateErrorCopyWith<$Res> implements $ViewStateCopyWith<$Res> {
  factory $ViewStateErrorCopyWith(ViewStateError value, $Res Function(ViewStateError) _then) = _$ViewStateErrorCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class _$ViewStateErrorCopyWithImpl<$Res>
    implements $ViewStateErrorCopyWith<$Res> {
  _$ViewStateErrorCopyWithImpl(this._self, this._then);

  final ViewStateError _self;
  final $Res Function(ViewStateError) _then;

/// Create a copy of ViewState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(ViewStateError(
null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
