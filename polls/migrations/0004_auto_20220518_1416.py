# Generated by Django 3.2.13 on 2022-05-18 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_rename_pub_data_post_pub_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='name',
            field=models.CharField(default='name', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='image_file',
            field=models.ImageField(upload_to='photos'),
        ),
    ]
