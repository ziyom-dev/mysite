# Generated by Django 5.0.4 on 2024-04-18 21:23

import autoslug.fields
import django.db.models.deletion
import modelcluster.fields
import mptt.fields
import phonenumber_field.modelfields
import wagtail.fields
import wagtail.search.index
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Customer', '0001_initial'),
        ('wagtailcore', '0091_remove_revision_submitted_for_moderation'),
        ('wagtailimages', '0025_alter_image_file_alter_rendition_file'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Attribute Group',
                'verbose_name_plural': 'Attribute Groups',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('symbol', models.CharField(max_length=5)),
                ('exchange_rate', models.DecimalField(decimal_places=4, max_digits=10)),
            ],
            options={
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencys',
            },
        ),
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, primary_key=True, region='UZ', serialize=False, unique=True)),
                ('otp', models.IntegerField(null=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('attempts', models.IntegerField(default=3)),
            ],
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('name', models.CharField(max_length=255)),
                ('group', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='ecommerce.attributegroup')),
            ],
            options={
                'verbose_name': 'Attribute',
                'verbose_name_plural': 'Attributes',
            },
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('value', models.CharField(max_length=255)),
                ('attribute', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='ecommerce.attribute')),
            ],
            options={
                'verbose_name': 'Attribute value',
                'verbose_name_plural': 'Attribute values',
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(blank=True, editable=True, populate_from='name', unique=True)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'verbose_name': 'Brand',
                'verbose_name_plural': 'Brands',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', wagtail.fields.RichTextField(blank=True)),
                ('slug', autoslug.fields.AutoSlugField(blank=True, editable=True, populate_from='name', unique=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, limit_choices_to={'level': 0}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='ecommerce.category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=255, null=True)),
                ('user_phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region='UZ')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('total_price', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'В ожидании'), ('processing', 'Обработка'), ('shipped', 'Отправлено'), ('delivered', 'Доставлено'), ('canceled', 'Отменено')], default='pending', max_length=20)),
                ('delivery_type', models.CharField(choices=[('delivery', 'Доставка'), ('self-delivery', 'Самовывоз')], default='delivery', max_length=20)),
                ('payment_type', models.CharField(choices=[('cash', 'Наличные'), ('card', 'Карта')], default='cash', max_length=20)),
                ('comment', models.TextField(blank=True)),
                ('delivery_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Customer.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('live', models.BooleanField(default=True, editable=False, verbose_name='live')),
                ('has_unpublished_changes', models.BooleanField(default=False, editable=False, verbose_name='has unpublished changes')),
                ('first_published_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='first published at')),
                ('last_published_at', models.DateTimeField(editable=False, null=True, verbose_name='last published at')),
                ('go_live_at', models.DateTimeField(blank=True, null=True, verbose_name='go live date/time')),
                ('expire_at', models.DateTimeField(blank=True, null=True, verbose_name='expiry date/time')),
                ('expired', models.BooleanField(default=False, editable=False, verbose_name='expired')),
                ('name', models.CharField(max_length=255)),
                ('sku', models.CharField(blank=True, max_length=255, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('availability', models.CharField(choices=[('OutOfStock', 'Нет в наличии'), ('InStock', 'Есть в наличии'), ('Soon', 'Скоро')], default='Soon', max_length=20)),
                ('description', wagtail.fields.RichTextField(blank=True)),
                ('short_description', models.TextField(blank=True, max_length=160)),
                ('slug', autoslug.fields.AutoSlugField(blank=True, editable=True, populate_from='name', unique=True)),
                ('views', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('purchases', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('site_id', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('category_root_level', models.IntegerField(default=0)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecommerce.brand')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='category', to='ecommerce.category')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('latest_revision', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.revision', verbose_name='latest revision')),
                ('live_revision', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.revision', verbose_name='live revision')),
                ('parent_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_category', to='ecommerce.category')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('product_price', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('order', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='ecommerce.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
            options={
                'verbose_name': 'Order Item',
                'verbose_name_plural': 'Order Items',
            },
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('attribute_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.attributegroup')),
                ('product', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attrs', to='ecommerce.product')),
            ],
            options={
                'unique_together': {('product', 'attribute_group')},
            },
        ),
        migrations.CreateModel(
            name='ProductAttributeAttrs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.attribute')),
                ('attribute_value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.attributevalue')),
                ('product_attribute', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='attrs', to='ecommerce.productattribute')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.image')),
                ('product', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery', to='ecommerce.product')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stars', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1)),
                ('review_text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_visible', models.BooleanField(default=True)),
                ('product', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='ecommerce.product')),
                ('user', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
            },
        ),
        migrations.CreateModel(
            name='UserFavoriteProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='ecommerce.product')),
                ('user', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_products', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'product')},
            },
        ),
    ]
