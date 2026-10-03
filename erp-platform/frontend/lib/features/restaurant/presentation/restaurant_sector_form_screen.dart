import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/router/app_routes.dart';
import '../../../app/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/layouts/app_scaffold.dart';
import '../data/restaurant_sector_remote_data_source.dart';

class RestaurantSectorFormScreen extends ConsumerStatefulWidget {
  const RestaurantSectorFormScreen({this.sector, super.key});

  final RestaurantSector? sector;

  @override
  ConsumerState<RestaurantSectorFormScreen> createState() =>
      _RestaurantSectorFormScreenState();
}

class _RestaurantSectorFormScreenState
    extends ConsumerState<RestaurantSectorFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _codeController = TextEditingController();
  RestaurantSectorType _type = RestaurantSectorType.diningRoom;
  bool _saving = false;

  bool get _isEditing => widget.sector != null;

  @override
  void initState() {
    super.initState();
    final sector = widget.sector;
    if (sector == null) {
      return;
    }
    _nameController.text = sector.name;
    _codeController.text = sector.code;
    _type = sector.type;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: _isEditing ? 'Editar setor' : 'Novo setor',
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  _isEditing ? 'Editar setor' : 'Novo setor',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  _isEditing
                      ? 'Atualize o ambiente sem perder seu contexto operacional.'
                      : 'Defina um ambiente para organizar o atendimento da filial.',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: AppSpacing.lg),
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Nome'),
                  validator: _required,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(
                  controller: _codeController,
                  textCapitalization: TextCapitalization.characters,
                  decoration: const InputDecoration(labelText: 'Código'),
                  validator: _required,
                ),
                const SizedBox(height: AppSpacing.md),
                DropdownButtonFormField<RestaurantSectorType>(
                  initialValue: _type,
                  decoration: const InputDecoration(labelText: 'Tipo'),
                  items: RestaurantSectorType.values
                      .map(
                        (type) => DropdownMenuItem(
                          value: type,
                          child: Text(_typeLabel(type)),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _type = value);
                    }
                  },
                ),
                const SizedBox(height: AppSpacing.lg),
                Align(
                  alignment: Alignment.centerRight,
                  child: AppButton(
                    label: _isEditing ? 'Salvar alterações' : 'Salvar setor',
                    icon: Icons.save_outlined,
                    isLoading: _saving,
                    onPressed: _save,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String? _required(String? value) {
    return value == null || value.trim().isEmpty ? 'Campo obrigatório' : null;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _saving = true);
    try {
      final input = RestaurantSectorInput(
        code: _codeController.text.trim().toUpperCase(),
        name: _nameController.text.trim(),
        type: _type == RestaurantSectorType.diningRoom
            ? 'dining_room'
            : _type.name,
        isActive: widget.sector?.isActive ?? true,
      );
      final dataSource = ref.read(restaurantSectorRemoteDataSourceProvider);
      if (_isEditing) {
        await dataSource.update(widget.sector!.id, input);
      } else {
        await dataSource.create(input);
      }
      ref.invalidate(restaurantSectorsProvider);
      if (mounted) {
        context.go(AppRoutes.restaurantSectors);
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              _isEditing
                  ? 'Não foi possível atualizar o setor.'
                  : 'Não foi possível salvar o setor.',
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }
}

String _typeLabel(RestaurantSectorType type) => switch (type) {
  RestaurantSectorType.diningRoom => 'Salão',
  RestaurantSectorType.outdoor => 'Área externa',
  RestaurantSectorType.bar => 'Bar',
  RestaurantSectorType.vip => 'Área VIP',
  RestaurantSectorType.counter => 'Balcão',
  RestaurantSectorType.other => 'Outro',
};
