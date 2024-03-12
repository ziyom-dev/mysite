from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    default_limit = 1000
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data,
        })


    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None
        url = self.request.build_absolute_uri()
        offset = self.offset + self.limit
        return replace_domain(url, offset=offset, limit=self.limit)

    def get_previous_link(self):
        if self.offset <= 0:
            return None
        url = self.request.build_absolute_uri()
        offset = self.offset - self.limit
        return replace_domain(url, offset=max(offset, 0), limit=self.limit)

def replace_domain(url, **params):
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

    # Разбор URL для получения только пути и параметров
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Обновление параметров пагинации
    query_params.update(params)
    query_string = urlencode(query_params, doseq=True)

    # Получение пути без '/api'
    path = parsed_url.path
    if path.startswith('/api'):
        path = path[4:]  # Удаление '/api' из пути

    # Формирование нового URL без домена и базового пути
    new_url = urlunparse((
        '', '',  # Пропуск схемы и домена
        path,
        parsed_url.params,
        query_string,
        parsed_url.fragment
    ))
    return new_url
    
class ProductsPagination(LimitOffsetPagination):
    default_limit = 9
    
    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)

        if self.count is not None and self.limit is not None and self.offset is not None:
            self.request = request
            self.queryset = queryset  # Задаем queryset вручную
            return list(queryset[self.offset:self.offset + self.limit])

    def get_count(self, queryset):
        # Возвращает общее количество объектов в queryset
        return queryset.count()

    def get_paginated_response(self, data):
        # Вычисляем атрибуты и значения
        attr_filters = self.calculate_attr_filters(self.queryset)

        # Добавляем "attr_filters" к обычному response
        response_data = {
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data,
            'attr_filters': attr_filters,
        }

        return Response(response_data)

    def calculate_attr_filters(self, queryset):
        attr_filters = {}

        for item in queryset:
            product_attrs = item.product_attrs.all()  # Используйте related manager для product_attrs

            for product_attr in product_attrs:
                attribute = product_attr.attribute
                attribute_value = product_attr.attribute_value

                # Создаем уникальный ключ на основе идентификатора атрибута
                key = attribute.id

                # Проверяем, был ли уже добавлен такой ключ в attr_filters
                if key not in attr_filters:
                    attr_filters[key] = {
                        'attribute': {
                            'id': attribute.id,
                            'name': attribute.name,
                        },
                        'attribute_values': [{
                            'id': attribute_value.id,
                            'value': attribute_value.value,
                            'product_count': 1,
                        }],
                    }
                else:
                    # Если ключ уже существует
                    existing_values = attr_filters[key]['attribute_values']
                    value_index = next((i for i, v in enumerate(existing_values) if v['id'] == attribute_value.id), None)
                    
                    if value_index is not None:
                        # Если значение уже существует, увеличиваем количество продуктов
                        attr_filters[key]['attribute_values'][value_index]['product_count'] += 1
                    else:
                        # Если значение еще не было добавлено, добавляем его в список
                        attr_filters[key]['attribute_values'].append({
                            'id': attribute_value.id,
                            'value': attribute_value.value,
                            'product_count': 1,
                        })

        # Преобразуем словарь в список
        return list(attr_filters.values())
    
class CategoriesPagination(CustomPagination):
    default_limit = 100
    
class BrandsPagination(LimitOffsetPagination):
    default_limit = 100
    
