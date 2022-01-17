# Generated by Django 3.2.7 on 2021-10-02 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Update_In_Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('updating', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Update In Progress',
                'verbose_name_plural': 'Update In Progress',
                'ordering': ['id'],
            },
        ),
    ]