from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0007_candidateprofile_generated_resume_pdf_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='is_fresher',
            field=models.BooleanField(default=False),
        ),
    ]
