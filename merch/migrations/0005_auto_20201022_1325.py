# Generated by Django 3.1.1 on 2020-10-22 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0004_auto_20201022_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merch',
            name='image',
            field=models.ImageField(default='', upload_to=''),
            preserve_default=False,
        ),
    ]
