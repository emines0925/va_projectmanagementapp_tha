# Generated by Django 4.2.23 on 2025-07-15 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmembership',
            name='role',
            field=models.CharField(choices=[('Owner', 'Owner'), ('Editor', 'Editor'), ('Reader', 'Reader')], max_length=10),
        ),
    ]
