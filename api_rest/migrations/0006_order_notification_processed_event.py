from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0005_alter_event_max_participants_alter_user_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='data_processamento',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='status_notificacao',
            field=models.CharField(
                choices=[
                    ('requested', 'Requested'),
                    ('notification_sent', 'Notification sent'),
                ],
                default='requested',
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='ProcessedEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=64, unique=True)),
                ('processed_at', models.DateTimeField(auto_now_add=True)),
                (
                    'order',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='processed_event',
                        to='api_rest.order',
                    ),
                ),
            ],
            options={
                'ordering': ['-processed_at'],
            },
        ),
    ]
