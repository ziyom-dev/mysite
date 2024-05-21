from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Product, Category, Brand
import requests
from django.core.files.base import ContentFile
from wagtail.images.models import Image as WagtailImage
from mysite.settings.base import WAGTAILADMIN_BASE_URL
import os

from io import BytesIO
from PIL import Image
from wagtail.images import get_image_model



class ImageWidget(ForeignKeyWidget):
    def __init__(self, image_model=None, *args, **kwargs):
        self.model = image_model if image_model else get_image_model()
        super().__init__(self.model, *args, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            filename = value.split('/')[-1]
            file_extension = os.path.splitext(filename)[1].lower()
            
            if value.startswith('http://') or value.startswith('https://'):
                response = requests.get(value)
                if response.status_code == 200:
                    content = response.content
                    if file_extension in ['.webp', '.avif']:
                        image = Image.open(BytesIO(content))
                        converted_file = BytesIO()
                        image = image.convert('RGB')
                        filename = filename.replace(file_extension, '.jpeg')
                        image.save(converted_file, format='JPEG')
                        image_file = ContentFile(converted_file.getvalue(), name=filename)
                    else:
                        image_file = ContentFile(content, name=filename)
                    
                    image = self.model(title=filename)
                    image.file.save(filename, image_file, save=True)
                    image.save()
                    return image
                else:
                    # Возвращаем None, если не удалось скачать изображение
                    return None
            else:
                raise ValueError(f"Изображение не найдено в системе для пути: {value}")
        return None

    def render(self, value, obj=None):
        return WAGTAILADMIN_BASE_URL + value.file.url if value else ""


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
        parent_category_name = row.get("parent_category")
        if parent_category_name:
            parent_category, _ = Category.objects.get_or_create(name=parent_category_name)

            if parent_category.pk:
                parent_category = Category.objects.filter(pk=parent_category.pk).first()

            category_name = row.get("category")
            if category_name:
                Category.objects.get_or_create(name=category_name, defaults={"parent": parent_category})

        brand_name = row.get("brand")
        if brand_name:
            Brand.objects.get_or_create(name=brand_name, defaults={"name": brand_name})

    class Meta:
        model = Product
        # import_id_fields = ('site_id',)
        exclude = ('category_root_level',)
