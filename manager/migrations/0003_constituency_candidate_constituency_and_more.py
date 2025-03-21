# Generated by Django 5.1 on 2025-03-19 12:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_candidate_votingsession_vote'),
    ]

    operations = [
        migrations.CreateModel(
            name='Constituency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('constituency', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='constituency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.constituency'),
        ),
        migrations.AddField(
            model_name='votingsession',
            name='constituency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.constituency'),
        ),
        migrations.AlterField(
            model_name='voter',
            name='constituency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.constituency'),
        ),
        migrations.CreateModel(
            name='VoteCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_votes', models.PositiveIntegerField(default=0)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.candidate')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.votingsession')),
            ],
            options={
                'unique_together': {('session', 'candidate')},
            },
        ),
        migrations.DeleteModel(
            name='Vote',
        ),
    ]
