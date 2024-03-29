# Generated by Django 5.0.1 on 2024-03-21 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0002_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='apartment',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='entrance',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='floor',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='landmark',
            field=models.CharField(blank=True, max_length=225),
        ),
        migrations.AddField(
            model_name='address',
            name='link',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(blank=True, max_length=225),
        ),
    ]
