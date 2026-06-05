from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0007_merge_0006_create_event_read_model_0006_order_notification_processed_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
