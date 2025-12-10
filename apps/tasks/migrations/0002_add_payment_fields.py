# Generated manually for payment tracking

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workrecord',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='Whether this work has been paid to the employee', verbose_name='Is Paid'),
        ),
        migrations.AddField(
            model_name='workrecord',
            name='paid_at',
            field=models.DateTimeField(blank=True, help_text='Date and time when payment was processed', null=True, verbose_name='Paid At'),
        ),
        migrations.AddField(
            model_name='workrecord',
            name='paid_by',
            field=models.ForeignKey(blank=True, help_text='Employee (Master/Owner) who marked this as paid', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paid_work_records', to='employees.employee', verbose_name='Paid By'),
        ),
        migrations.AddIndex(
            model_name='workrecord',
            index=models.Index(fields=['is_paid'], name='work_record_is_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='workrecord',
            index=models.Index(fields=['tenant', 'is_paid'], name='work_record_tenant__is_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='workrecord',
            index=models.Index(fields=['employee', 'is_paid'], name='work_record_employe_is_paid_idx'),
        ),
    ]
