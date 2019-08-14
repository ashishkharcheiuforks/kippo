# Generated by Django 2.2.3 on 2019-08-02 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20190803_0121'),
    ]

    operations = [
        migrations.AddField(
            model_name='kippoproject',
            name='github_project_api_url',
            field=models.URLField(blank=True, null=True, verbose_name='Github Project api URL (needed for webhook event linking to project)'),
        ),
    ]
