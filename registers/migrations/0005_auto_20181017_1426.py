# Generated by Django 2.0.9 on 2018-10-17 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0007_auto_20180829_1733'),
        ('registers', '0004_auto_20181011_0804'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeApproval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('approval_source', models.SmallIntegerField(choices=[(0, 'Email'), (1, 'Online'), (2, 'Verbal'), (3, 'Other')], default=0)),
                ('date_approved', models.DateTimeField()),
                ('notes', models.CharField(blank=True, max_length=2048, null=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organisation.DepartmentUser')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('log', models.TextField()),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='ChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('change_type', models.SmallIntegerField(choices=[(0, 'Normal'), (1, 'Standard'), (2, 'Emergency')], db_index=True, default=0)),
                ('status', models.SmallIntegerField(choices=[(0, 'Draft'), (1, 'Scheduled'), (2, 'Ready'), (3, 'Complete'), (4, 'Rolled back')], db_index=True, default=0)),
                ('description', models.TextField(help_text='Brief description of what the change is and why it is being undertaken')),
                ('incident_url', models.URLField(blank=True, help_text='If the change is to address an incident, URL to the incident details', max_length=2048, null=True, verbose_name='Incident URL')),
                ('test_date', models.DateField(blank=True, help_text='Date that the change was tested', null=True)),
                ('planned_start', models.DateTimeField(blank=True, help_text='Time that the change is planned to begin', null=True)),
                ('planned_end', models.DateTimeField(blank=True, help_text='Time that the change is planned to end', null=True)),
                ('completed', models.DateTimeField(blank=True, help_text='Time that the change was completed', null=True)),
                ('implementation', models.TextField(blank=True, help_text='Implementation/deployment instructions', null=True)),
                ('implementation_docs', models.FileField(blank=True, help_text='Implementation/deployment instructions (attachment)', null=True, upload_to='uploads/%Y/%m/%d')),
                ('outage', models.DurationField(blank=True, help_text='Duration of outage required to complete the change (hh:mm:ss).', null=True)),
                ('communication', models.TextField(blank=True, help_text='Description of all communications to be undertaken', null=True)),
                ('broadcast', models.FileField(blank=True, help_text='The broadcast text to be emailed to users regarding this change', null=True, upload_to='uploads/%Y/%m/%d')),
                ('unexpected_issues', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, help_text='Details of any unexpected issues, observations, etc.', null=True)),
                ('approver', models.ForeignKey(help_text='Change request approver', on_delete=django.db.models.deletion.PROTECT, related_name='approver', to='organisation.DepartmentUser')),
                ('implementer', models.ForeignKey(blank=True, help_text='Change request implementer', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementer', to='organisation.DepartmentUser')),
                ('it_systems', models.ManyToManyField(blank=True, help_text='IT System(s) affected by the change', to='registers.ITSystem', verbose_name='IT Systems')),
                ('requester', models.ForeignKey(help_text='Change requester', on_delete=django.db.models.deletion.PROTECT, related_name='requester', to='organisation.DepartmentUser')),
            ],
        ),
        migrations.CreateModel(
            name='StandardChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True, null=True)),
                ('expiry', models.DateField(blank=True, null=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organisation.DepartmentUser')),
                ('it_systems', models.ManyToManyField(blank=True, help_text='IT System(s) affected by the standard change', to='registers.ITSystem', verbose_name='IT Systems')),
            ],
        ),
        migrations.AddField(
            model_name='changerequest',
            name='standard_change',
            field=models.ForeignKey(blank=True, help_text='Standard change reference', null=True, on_delete=django.db.models.deletion.PROTECT, to='registers.StandardChange'),
        ),
        migrations.AddField(
            model_name='changelog',
            name='change_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registers.ChangeRequest'),
        ),
        migrations.AddField(
            model_name='changeapproval',
            name='change_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registers.ChangeRequest'),
        ),
    ]