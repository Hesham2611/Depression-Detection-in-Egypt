# Generated by Django 4.0.7 on 2023-05-19 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_auto_20210215_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='is_depressed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
