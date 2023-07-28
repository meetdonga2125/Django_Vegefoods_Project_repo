from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),  # Replace 'myapp' and '0001_initial' with your app's name and initial migration file
    ]

    operations = [
        migrations.AddField(
            model_name='user',  # Replace 'User' with your actual user model name
            name='address',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
