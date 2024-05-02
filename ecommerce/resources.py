# ecommerce/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, Widget, BooleanWidget
from .models import Product, Category, Brand
import requests
from django.core.files.base import ContentFile
from wagtail.images.models import Image as WagtailImage
import hashlib

from mysite.settings.base import WAGTAILADMIN_BASE_URL


class ImageWidget(ForeignKeyWidget):
    def __init__(self, image_model=None, *args, **kwargs):
        self.model = image_model if image_model else WagtailImage
        super().__init__(self.model, *args, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            filename = value.split('/')[-1]
            if value.startswith('http://') or value.startswith('https://'):
                # Проверяем, существует ли изображение с таким же именем файла
                image = self.model.objects.filter(file__endswith=filename).first()
                if image:
                    # Если изображение с таким именем файла уже существует, возвращаем его
                    return image
                else:
                    # Скачиваем изображение только если оно не найдено в базе данных
                    response = requests.get(value)
                    if response.status_code == 200:
                        content = response.content
                        image_file = ContentFile(content)
                        # Создаем новый объект изображения, так как изображение с таким именем файла не найдено
                        image = self.model(title=filename)
                        image.file.save(filename, image_file, save=True)
                        image.save()
                        return image
                    else:
                        raise ValueError(f"Не удалось скачать изображение по URL: {value}")
            else:
                raise ValueError(f"Изображение не найдено в системе для пути: {value}")
        return None

    def render(self, value, obj=None):
        return WAGTAILADMIN_BASE_URL+value.file.url if value else ""




class ProductResource(resources.ModelResource):
    parent_category = fields.Field(
        column_name='parent_category',
        attribute='parent_category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    brand = fields.Field(
        column_name='brand',
        attribute='brand',
        widget=ForeignKeyWidget(Brand, 'name')
    )
    
    image = fields.Field(
        column_name='image',
        attribute='image',
        widget=ImageWidget()
    )
    
    views = fields.Field(
        column_name='',
        attribute='',
        readonly=True
    )
    purchases = fields.Field(
        column_name='',
        attribute='',
        readonly=True
    )
    
    def before_import_row(self, row, **kwargs):
        parent_category_name = row.get("parent_category")  # Получаем имя родительской категории из импортируемых данных
        if parent_category_name:  # Проверяем, что parent_category_name не None и не пустая строка
            parent_category, _ = Category.objects.get_or_create(name=parent_category_name)
            
            # Ищем родительскую категорию в MPTT модели
            if parent_category.pk:
                parent_category = Category.objects.filter(pk=parent_category.pk).first()
            
            # Устанавливаем parent_category как родителя для category
            category_name = row.get("category")  # Получаем имя категории из импортируемых данных
            if category_name:  # Проверяем, что category_name не None и не пустая строка
                category, _ = Category.objects.get_or_create(name=category_name, defaults={"name": category_name, "parent": parent_category})
            
        brand_name = row.get("brand")  # Получаем имя бренда из импортируемых данных
        if brand_name:  # Проверяем, что brand_name не None и не пустая строка
            Brand.objects.get_or_create(name=brand_name, defaults={"name": brand_name})



    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('id',)
        exclude = ('category_root_level')
