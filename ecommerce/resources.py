# ecommerce/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, Widget
from .models import Product, Category, Brand
import requests
from django.core.files.base import ContentFile
from wagtail.images.models import Image as WagtailImage
import hashlib


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
        return value.file.name if value else ""


class CategoryWidget(Widget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            parent_name, category_name = value.split(">")
            parent, _ = Category.objects.get_or_create(name=parent_name, parent=None)
            category, _ = Category.objects.get_or_create(name=category_name, parent=parent)
            return category
        return None

    def render(self, value, obj=None):
        if value:
            return f"{value.parent.name}>{value.name}" if value.parent else value.name
        return ""

class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=CategoryWidget()
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
    
    def before_import_row(self, row, **kwargs):
        brand_name = row.get("brand")  # Используйте метод .get() словаря
        if brand_name:  # Проверяем, что brand_name не None и не пустая строка
            Brand.objects.get_or_create(name=brand_name, defaults={"name": brand_name})


    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('id',)
        exclude = ()
