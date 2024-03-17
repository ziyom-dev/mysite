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
        filters = self.get_filters()

        # Добавляем "attr_filters" к обычному response
        response_data = {
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data,
            'filters': filters,
        }
        
    

        return Response(response_data)
    
    def get_filters(self):
        attributes = self.get_attributes_from_queryset()
        brands = self.get_brands_from_queryset()
        return {
            'brands': brands,  # Пример данных для "brands"
            'attributes': attributes  # Пример данных для "attributes"
        }
        
    def get_brands_from_queryset(self):
        # Используем set для хранения уникальных брендов
        brands_set = set()

        # Проходим по товарам текущей страницы для извлечения брендов
        for product in self.queryset.prefetch_related('brand'):
            brands_set.add((product.brand.id, product.brand.name))

        # Преобразуем set в список словарей
        brands_list = [{'brand_id': brand[0], 'brand_name': brand[1]} for brand in brands_set]

        return brands_list
        
        
    def get_attributes_from_queryset(self):
        attribute_groups_dict = {}
        attribute_usage_count = {}

        for product in self.queryset.prefetch_related(
            "product_attrs__attrs__attribute__group", "product_attrs__attrs__attribute_value"
        ):
            product_attributes_set = set()  # Для отслеживания уникальных атрибутов в текущем продукте

            for product_attr in product.product_attrs.all():
                group_id = product_attr.attribute_group.id
                group_name = product_attr.attribute_group.name

                if group_id not in attribute_groups_dict:
                    attribute_groups_dict[group_id] = {
                        "attribute_group_id": group_id,
                        "attribute_group_name": group_name,
                        "attrs": set()
                    }

                for attr in product_attr.attrs.all():
                    attr_tuple = (
                        attr.attribute.id,
                        attr.attribute.name,
                        attr.attribute_value.id,
                        attr.attribute_value.value
                    )

                    # Проверяем, встречался ли уже атрибут в текущем продукте
                    if attr_tuple not in product_attributes_set:
                        product_attributes_set.add(attr_tuple)
                        attribute_groups_dict[group_id]["attrs"].add(attr_tuple)

                        # Увеличиваем счетчик использования атрибута
                        if attr_tuple in attribute_usage_count:
                            attribute_usage_count[attr_tuple] += 1
                        else:
                            attribute_usage_count[attr_tuple] = 1

        # Преобразуем set в список, добавляем счетчик и сортируем
        for group_id, group_data in attribute_groups_dict.items():
            attrs_sorted_list = sorted(list(group_data["attrs"]), key=lambda x: x[0])  # Сортировка по ID атрибута
            attrs_list = [
                {
                    "attribute_id": attr[0],
                    "attribute_name": attr[1],
                    "attribute_value_id": attr[2],
                    "attribute_value_name": attr[3],
                    "product_count": attribute_usage_count[attr]  # Добавляем счетчик продуктов
                }
                for attr in attrs_sorted_list
            ]
            group_data["attrs"] = attrs_list

        return list(attribute_groups_dict.values())



    
class CategoriesPagination(CustomPagination):
    default_limit = 100
    
class BrandsPagination(LimitOffsetPagination):
    default_limit = 100
    
