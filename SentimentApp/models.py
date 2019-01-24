from django.db import models
from django.db import connection, connections
import json


def ValidateLogin(user,password):
    if(user == 'admin' and password == '1234'):
        return True
    else:
        return False

class Score(models.Model):
    ScoreTextBlob = models.CharField(db_column='ScoreTextBlob', max_length=100, blank=True,
                                     null=True)  # Field name made lowercase.
    ScoreVader = models.CharField(db_column='ScoreVader', max_length=100, blank=True,
                                  null=True)  # Field name made lowercase.
    ScoreAzure = models.CharField(db_column='ScoreAzure', max_length=100, blank=True,
                                  null=True)  # Field name made lowercase.
    ScoreStanfordCoreNLP = models.CharField(db_column='ScoreStanfordCoreNLP', max_length=100, blank=True,
                                            null=True)  # Field name made lowercase.

    ScoreGoogleNLP = models.CharField(db_column='ScoreGoogleNLP', max_length=100, blank=True,
                                            # Field name made lowercase.
                                            null=True)

    ScoreIBMNLP = models.CharField(db_column='ScoreIBMNLP', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Score'


class FacebookHistory(models.Model):
    status_id = models.IntegerField(blank=True, null=True)
    status_type = models.CharField(max_length=200, blank=True, null=True)
    reaction_summary_total = models.IntegerField(blank=True, null=True)
    reaction_summary_viewer_reaction = models.CharField(max_length=200, blank=True, null=True)
    status_name = models.TextField(blank=True, null=True)
    share_count = models.IntegerField(blank=True, null=True)
    status_message = models.TextField(blank=True, null=True)
    status_link = models.TextField(blank=True, null=True)
    status_created_time = models.CharField(max_length=50, blank=True, null=True)
    comment_summary_order = models.TextField(blank=True, null=True)
    comment_summary_total = models.IntegerField(blank=True, null=True)
    comment_summary_can_comment = models.CharField(max_length=10, blank=True, null=True)
    love_summary_total = models.IntegerField(blank=True, null=True)
    angry_summary_total = models.IntegerField(blank=True, null=True)
    haha_summary_total = models.IntegerField(blank=True, null=True)
    like_summary_total = models.IntegerField(blank=True, null=True)
    sad_summary_total = models.IntegerField(blank=True, null=True)
    wow_summary_total = models.IntegerField(blank=True, null=True)
    historyid = models.CharField(max_length=50,blank=True, null=True, db_column="HistoryKey")
    scoreid = models.ForeignKey('Score', models.DO_NOTHING, db_column='ScoreId', blank=True,
                                null=True)  # Field name made lowercase.
    entrydate = models.DateTimeField(db_column='EntryDate', blank=True, null=True, auto_now_add=True, auto_now=False)  # Field name made lowercase.
    translated_status_message = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'FacebookHistory'


class WebCrawl(models.Model):
    url = models.CharField(max_length=256, null=True)
    keyWord = models.CharField(max_length=256, null=True)
    depth = models.IntegerField( null=True)
    title = models.CharField(max_length=256, null=True)
    entryTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    translatedText = models.CharField(max_length=256, null=True)
    HistoryId = models.CharField(max_length=50, db_column="HistoryKey",null=True)
    scoreid = models.ForeignKey('Score', models.DO_NOTHING, db_column='ScoreId', blank=True,
                                null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CrawlResult'


class UserCrawlHistory(models.Model):
    Historykey = models.CharField(max_length=500, null=True)
    KeyWord = models.CharField(max_length=500, null=True)
    EntryTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    class Meta:
        managed = False
        db_table = 'UserCrawlHistory'


class TwitterHistory(models.Model):
    status_id = models.CharField(max_length=100)
    status_message = models.TextField(blank=True, null=True)
    retweet_count = models.IntegerField(blank=True, null=True)
    favourite_count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    geo = models.CharField(max_length=100, blank=True, null=True)
    coordinates = models.CharField(max_length=100, blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    scoreid = models.ForeignKey('Score', models.DO_NOTHING, db_column='ScoreId', blank=True, null=True)  # Field name made lowercase.
    entrydate = models.DateTimeField(db_column='EntryDate', blank=True, null=True)  # Field name made lowercase.
    historykey = models.CharField(db_column='HistoryKey', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TwitterHistory'




