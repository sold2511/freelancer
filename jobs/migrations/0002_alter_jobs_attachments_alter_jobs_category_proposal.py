# Generated by Django 5.2.3 on 2025-07-02 16:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='attachments',
            field=models.FileField(upload_to='job_attachments/'),
        ),
        migrations.AlterField(
            model_name='jobs',
            name='category',
            field=models.CharField(choices=[('web_dev', 'Web Development'), ('graphic_design', 'Graphic Design'), ('seo', 'SEO'), ('content_writing', 'Content Writing'), ('video_editing', 'Video Editing'), ('data_entry', 'Data Entry'), ('translation', 'Translation'), ('mobile_dev', 'Mobile App Development'), ('marketing', 'Digital Marketing'), ('support', 'Customer Support')], default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('estimated_budget', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timeline', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('freelancer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.jobs')),
            ],
        ),
    ]
