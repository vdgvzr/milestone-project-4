# Generated by Django 3.1.1 on 2020-10-13 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_features_featured_artist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='features',
            name='thumbnail_url',
            field=models.CharField(max_length=512),
        ),
    ]
