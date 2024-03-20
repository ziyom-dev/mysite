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
        min_price, max_price = self.get_price_range_from_queryset()
        return {
            'brands': brands,  # Пример данных для "brands"
            'attributes': attributes,  # Пример данных для "attributes"
            'price': {
                'min': min_price,
                'max': max_price,
            },
        }
    
    def get_price_range_from_queryset(self):
        # Предполагаем, что изначально минимальная и максимальная цены не установлены
        min_price = None
        max_price = None

        for product in self.queryset:
            # Преобразуем цену и цену со скидкой из строки в число, обрабатывая случай, когда скидка отсутствует
            product_price = float(product.price)
            product_sale_price = float(product.sale_price) if product.sale_price else product_price

            # Определяем актуальную цену как минимум из цены и цены со скидкой
            actual_price = min(product_price, product_sale_price)

            # Обновляем минимальную и максимальную цены
            if min_price is None or actual_price < min_price:
                min_price = actual_price
            if max_price is None or actual_price > max_price:
                max_price = actual_price

        # Если после обхода всех продуктов цены не были установлены (queryset был пустым), устанавливаем их в 0
        if min_price is None or max_price is None:
            min_price, max_price = 0, 0

        return min_price, max_price
        
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

        for product in self.queryset.prefetch_related(
            "product_attrs__attrs__attribute__group", "product_attrs__attrs__attribute_value"
        ):
            for product_attr in product.product_attrs.all():
                group_id = product_attr.attribute_group.id
                group_name = product_attr.attribute_group.name

                if group_id not in attribute_groups_dict:
                    attribute_groups_dict[group_id] = {
                        "attribute_group_id": group_id,
                        "attribute_group_name": group_name,
                        "attrs": {}
                    }

                for attr in product_attr.attrs.all():
                    attribute_id = attr.attribute.id
                    attribute_name = attr.attribute.name

                    if attribute_id not in attribute_groups_dict[group_id]["attrs"]:
                        attribute_groups_dict[group_id]["attrs"][attribute_id] = {
                            "attribute_id": attribute_id,
                            "attribute_name": attribute_name,
                            "values": []
                        }

                    value_dict = {
                        "attribute_value_id": attr.attribute_value.id,
                        "attribute_value_name": attr.attribute_value.value,
                        "product_count": 1  # Предположим, что каждый продукт уникален для упрощения
                    }

                    # Проверка на уникальность значения атрибута для предотвращения дубликатов
                    if value_dict not in attribute_groups_dict[group_id]["attrs"][attribute_id]["values"]:
                        attribute_groups_dict[group_id]["attrs"][attribute_id]["values"].append(value_dict)

        # Преобразование структуры данных для соответствия желаемому формату вывода
        final_result = []
        for group_id, group_data in attribute_groups_dict.items():
            attrs_list = []
            for attr_id, attr_data in group_data["attrs"].items():
                attrs_list.append(attr_data)
            
            group_data["attrs"] = attrs_list
            final_result.append(group_data)

        return final_result
    
class CategoriesPagination(CustomPagination):
    default_limit = 100
    
class BrandsPagination(LimitOffsetPagination):
    default_limit = 100
    
