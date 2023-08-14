# Generated by Django 4.2.2 on 2023-08-14 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campus', '0002_boardpost_boardcomment_boardpostlike'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boardpost',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='boardpostlike',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='boardpostlike',
            name='post',
        ),
        migrations.RemoveField(
            model_name='boardpostlike',
            name='user',
        ),
        migrations.DeleteModel(
            name='BoardComment',
        ),
        migrations.DeleteModel(
            name='BoardPost',
        ),
        migrations.DeleteModel(
            name='BoardPostLike',
        ),
    ]