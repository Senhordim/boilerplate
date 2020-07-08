from django.apps import apps
from django.db.models import Q


def obter_modelo(nome_modelo):
    if not nome_modelo:
        return None
    try:
        return next(
            (m for m in apps.get_models() if m._meta.model_name.lower() == nome_modelo.lower()),
            None)
    except LookupError:
        return None


def registro_existente(objeto, campo):
    campo_str = '{0}__iexact'.format(campo)
    filtro = Q(**{campo_str: getattr(objeto, campo)})
    if objeto.id:
        return objeto._meta.model.objects.exclude(id=objeto.id).filter(filtro).exists()
    else:
        return objeto._meta.model.objects.filter(filtro).exists()
