import datetime
from django.db import models
from django.db import connection, connections
import json
import urllib
#%matplotlib inline
import pandas as pd
from sklearn import datasets
from sklearn import metrics
from sklearn import model_selection
import tensorflow as tf
from sklearn import preprocessing
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from django.contrib.staticfiles.templatetags.staticfiles import static
import sqlalchemy
import pyodbc
import csv

# Get an array of dictionary as the procedure SP_ChurnAnalysis returns multiple tables
# def GetChrunResultset(dateupto, username, depotcode):
#     cur = connections['LogisticsEPSMirror'].cursor()
#     cur.callproc('[dbo].[SP_ChurnAnalysis]', [dateupto,username,depotcode])
#     resultset = []
#     results = dictfetchall(cur)
#     resultset.append(results)
#     while cur.nextset():
#         results = dictfetchall(cur)
#         resultset.append(results)
#
#     cur.close()
#     return resultset

# def GetGraphDataForChurn(tables):
#     resultSet = []
#     for table in tables:
#         jsonData = []
#         for row in table:
#             date = str(row['InvoicePeriod'])[:4] + "-" +  str(row['InvoicePeriod'])[4:6] + "-" + "01"
#             obj = {'time': date, 'value': float("{0:.2f}".format(row['ChurnRate']))}
#             jsonData.append(obj)
#         resultSet.append(json.dumps(jsonData))
#
#     return resultSet


class User():
    def ValidateLoginDB(self, user, password):
        cur = connections['ChurnAppDB'].cursor()
        cur.execute("SELECT count(*) FROM [dbo].[UserPanel] where UserId = '" + user + "' and Password = '" + password + "' and IsActive = 1")
        total = int(cur.fetchone()[0])
        cur.close()
        if (total > 0):
            return True
        else:
            return False

class ChurnPowerBIReport:
    def GetPBIEmbeddedToken(self, groupId, reportId):
        pbitoken = {}
        with urllib.request.urlopen("http://192.168.100.61:90/pbiembeddedapi/Home/EmbedReport/" + groupId + "/" + reportId) as url:
            data = json.loads(url.read().decode())
            print(data)
            pbitoken['EmbedToken'] = data['EmbedToken']['Token']
            pbitoken['EmbedUrl'] = data['EmbedUrl']
            pbitoken['Id'] = data['Id']
        return pbitoken


class ExploratoryAnalytics:
    def GetFeatureData(self):
        cur = connections['ChurnAppDB'].cursor()
        query = "select top 1000 T.TagId as CustomerLabel, R.PrechurnProductsPurchased as PreChurnFootfalls, TotalQuantity, " \
                    "TotalValue, StDevQuantity as STDQuantity, StDevValue as STDValue, AvgTimeDelta as AVGTimeDelta, "\
                    "Recency, UniqueTransactionId as UNQFootfalls, UniqueItemId  as UNQItems, UniqueProductCategory  as UNQCategories, "\
                    "TotalQuantityperUniqueTransactionId, TotalQuantityperUniqueItemId, TotalQuantityperUniqueLocation,TotalQuantityperUniqueProductCategory "\
                 "from [dbo].[FeaturesRetail] R "\
                 "Inner join dbo.TagsRetail T "\
                 "On R.UserId = T.UserId where T.TagId is not null or T.TagId != ''"
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
        return results, colnames

    def GenerateCorrelationDiagram(self, dataset, columnNames, directory, userid):
        corelationPD = pd.DataFrame(dataset)
        corelationPD.columns = columnNames
        corelationPD = corelationPD[['CustomerLabel','PreChurnFootfalls','TotalQuantity','TotalValue','STDQuantity','STDValue','AVGTimeDelta','Recency','UNQFootfalls','UNQItems','UNQCategories']]
        print(corelationPD.head(10))
        corr = corelationPD.corr()
        print(corr)
        plt.figure(figsize=(12, 12))
        sns.heatmap(corr, vmax=.8, linewidths=0.01, square=True, annot=True, cmap='YlGnBu', linecolor="white")
        plt.title('Correlation Analysis')
        plt.xticks(rotation=90)
        plt.yticks(rotation=0)

        timestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        pngFilename = "ChurnApp" + static(directory + "Correlation_" + timestr + ".png")
        plt.savefig(pngFilename)

        # instance = PreAnalysisChurn()
        # instance.user = userid
        # instance.figureName = timestr
        # instance.figurePath = pngFilename
        # instance.figuretype = "Correlation"
        # instance.save()
        return static(directory + "Correlation_" + timestr + ".png")


    def GenerateBoxPlotDiagram(self, dataset, columnNames, directory, userid):
        data = pd.DataFrame(dataset)
        data.columns = columnNames
        plt.figure(figsize=(12, 12))
        plt.subplot(131)
        #fig, axs = plt.subplots(nrows=1, ncols=3)

        sns.boxplot(x="CustomerLabel", y="PreChurnFootfalls",data=data )
        sns.stripplot(x="CustomerLabel", y="PreChurnFootfalls", data=data, jitter=True, edgecolor="gray")

        plt.subplot(132)
        sns.boxplot(x="CustomerLabel", y="UNQFootfalls", data=data)
        sns.stripplot(x="CustomerLabel", y="UNQFootfalls", data=data, jitter=True, edgecolor="gray")

        plt.subplot(133)
        sns.boxplot(x="CustomerLabel", y="TotalQuantityperUniqueTransactionId", data=data)
        sns.stripplot(x="CustomerLabel", y="TotalQuantityperUniqueTransactionId", data=data, jitter=True, edgecolor="gray")

        plt.title("Customer Type", fontsize=10)

        timestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        pngFilename = "ChurnApp" + static(directory + "Boxplot_" + timestr + ".png")
        plt.savefig(pngFilename)

        # instance = PreAnalysisChurn()
        # instance.user = userid
        # instance.figureName = timestr
        # instance.figurePath = pngFilename
        # instance.figuretype = "Boxplot"
        # instance.save()
        return static(directory + "Boxplot_" + timestr + ".png")

    def GeneratePairPlot1(self, dataset, columnNames, directory, userid):
        data = pd.DataFrame(dataset)
        data.columns = columnNames

        plt.figure(figsize=(12, 12))

        g = sns.pairplot(data[['CustomerLabel', 'TotalQuantityperUniqueTransactionId','TotalQuantityperUniqueItemId', 'TotalQuantityperUniqueLocation', 'TotalQuantityperUniqueProductCategory']], hue="CustomerLabel", palette="Set2", diag_kind="kde", size=2.5)

        plt.title('Pair Plot Analysis')
        plt.xticks(rotation=90)
        plt.yticks(rotation=0)

        timestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        pngFilename = "ChurnApp" + static(directory + "PairPlot_" + timestr + ".png")
        plt.savefig(pngFilename)

        # instance = PreAnalysisChurn()
        # instance.user = userid
        # instance.figureName = timestr
        # instance.figurePath = pngFilename
        # instance.figuretype = "PairPlot"
        # instance.save()
        return static(directory + "PairPlot_" + timestr + ".png")

class PredictionModel:
    x_train = None
    x_test = None
    y_train = None
    y_test = None
    x_test_columnNames = None
    UserIddf = None
    OutletAddressDF = None

    def GetTrainDataset(self, samplingRatio):
        cur = connections['ChurnAppDB'].cursor()
        query = "select  Address, " \
                "    TotalQuantity, TotalValue, StDevQuantity, StDevValue," \
                "   AvgTimeDelta, Recency," \
                "    UniqueTransactionId, UniqueItemId, UniqueLocation, UniqueProductCategory," \
                "    TotalQuantityperUniqueTransactionId, TotalQuantityperUniqueItemId, TotalQuantityperUniqueLocation, TotalQuantityperUniqueProductCategory, " \
                "    TotalValueperUniqueTransactionId, TotalValueperUniqueItemId, TotalValueperUniqueLocation, TotalValueperUniqueProductCategory," \
                "    TagId " \
                "from FeaturesRetail F " \
                "tablesample (" + str(samplingRatio) + " percent) repeatable (98052) " \
                "join TagsRetail T on F.UserId=T.UserId "
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
        return results, colnames

    def GetTestDataset(self,samplingRatio):
        cur = connections['ChurnAppDB'].cursor()
        query = "select F.UserId, F.Address, TotalQuantity, TotalValue, StDevQuantity, StDevValue, "\
                "    AvgTimeDelta, Recency,  "\
                "    UniqueTransactionId, UniqueItemId, UniqueLocation, UniqueProductCategory, "\
                "    TotalQuantityperUniqueTransactionId, TotalQuantityperUniqueItemId, TotalQuantityperUniqueLocation, TotalQuantityperUniqueProductCategory,  "\
                "    TotalValueperUniqueTransactionId, TotalValueperUniqueItemId, TotalValueperUniqueLocation, TotalValueperUniqueProductCategory, T.TagId from  "\
                "(   "\
                "    select a.* from FeaturesRetail a  "\
                "    left outer join "\
                "    (   "\
                "        select * from FeaturesRetail    "\
                "        tablesample ( " + str(samplingRatio) + " percent) repeatable (98052)     "\
                "    )b  "\
                "    on a.UserId=b.UserId    "\
                "    where b.UserId is null  "\
                ") F join TagsRetail T on F.UserId=T.UserId "
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
        return results, colnames

    def PrepareTrainTestDateset(self, traindataset, columnNames, testdataset, columnNames2):
        print("Training started")
        traindataset = self.ProcessDatasetToNumpyArray(traindataset, columnNames)
        self.x_train = traindataset[:,0:-1]
        self.y_train = traindataset[:,-1]

        testdataset = pd.DataFrame(testdataset)  #loading data as dataframe to drop userid column which will be omitted intraining model
        testdataset.columns = columnNames2
        UserIddf = testdataset['UserId']
        testdataset = testdataset.drop('UserId', 1)
        self.OutletAddressDF = testdataset['Address']
        testdataset = self.ProcessDatasetToNumpyArray(testdataset, columnNames2[1:])   #Removing "UserId" from columnlist which is at 0 th position in columnNames2
        self.x_test = testdataset[:,0:-1]
        self.y_test = testdataset[:, -1]
        self.x_test_columnNames = columnNames2[1:-1] #Removing "UserId" from columnlist which is at 0 th position and "Tag" which is at the last column index in columnNames2
        self.UserIddf = UserIddf

    def FitTensorflowModel(self):
        tf.reset_default_graph()
        X_FEATURE = 'x'  # Name of the input feature.
        # Build 3 layer DNN with 10, 20, 10 units respectively.
        feature_columns = [tf.feature_column.numeric_column(X_FEATURE, shape=np.array(self.x_train).shape[1:])]
        classifier = tf.estimator.DNNClassifier(feature_columns=feature_columns, hidden_units=[10, 20, 10], n_classes=2)

        # Train.
        train_input_fn = tf.estimator.inputs.numpy_input_fn(x={X_FEATURE: self.x_train}, y=self.y_train, num_epochs=200, shuffle=True)
        classifier.train(input_fn=train_input_fn, steps=200)

        # Predict.
        test_input_fn = tf.estimator.inputs.numpy_input_fn(x={X_FEATURE: self.x_test}, y=self.y_test, num_epochs=1, shuffle=False)
        predictions = classifier.predict(input_fn=test_input_fn)
        y_predicted = np.array(list(p['class_ids'] for p in predictions))
        y_predicted = y_predicted.reshape(np.array(self.y_test).shape)

        score = metrics.accuracy_score(self.y_test, y_predicted)
        print(self.y_test[0:20])
        print(y_predicted[0:20])
        dnn_accuracy = round(float(format(score)) * 100)
        print('Accuracy (sklearn): ' + str(dnn_accuracy))

        mergedResultedDF = self.FinalMerging(self.x_test, y_predicted)
        #self.SaveDfToDB(mergedResultedDF)

        return  mergedResultedDF, dnn_accuracy

    def ProcessDatasetToNumpyArray(self, dataset, columnNames):
        dataset = pd.DataFrame(dataset)  # loading data as dataframe
        dataset.columns = columnNames
        le = preprocessing.LabelEncoder()  # Address are like 'D01', 'D02'... so convert them to categorical value
        le.fit(dataset['Address'])
        dataset['Address'] = le.transform(dataset['Address'])
        dataset = np.array(dataset.values)  # converting dataframe into numpy 2d array
        dataset = dataset.astype(np.float32)  # converting all values to float and taking 2 decimal points
        #print(dataset[0:10])
        dataset = np.around(dataset, decimals=2)
        return dataset

    def FinalMerging(self, x_testdataset, y_predicted):
        PredictedDF = pd.DataFrame(data=y_predicted, index=list(range(x_testdataset.shape[0])), columns=['PredictedResult'])
        testdataDF = pd.DataFrame(data=x_testdataset, index = list(range(x_testdataset.shape[0])), columns = self.x_test_columnNames)
        mergedResultedDF = pd.concat([testdataDF, PredictedDF], axis=1)
        mergedResultedDF = pd.concat([self.UserIddf, mergedResultedDF], axis=1)
        mergedResultedDF['Address'] = self.OutletAddressDF
        print(mergedResultedDF.head(10))
        return mergedResultedDF

    # def SaveDfToDB(self, mergedResultedDF):
    #     print("Saving result into database.")
    #     connstr_alchemy = "mssql+pymssql://" + DATABASES['ChurnAppDB']['USER'] + ":" + DATABASES['default']['PASSWORD'] + "@" + DATABASES['default']['HOST'] + "/" + DATABASES['default']['NAME']
    #     #engine = sqlalchemy.create_engine("mssql+pymssql://sa:dataport@192.168.100.140/RetailChurn")
    #     engine = sqlalchemy.create_engine(connstr_alchemy)
    #     # write the DataFrame to a table in the sql database
    #     #mergedResultedDF.to_sql("PredictionResult", engine, if_exists='replace', index = False)
    #     csvFileName = "ChurnApp" + static("Statistics/PredictionResult.csv")
    #     mergedResultedDF.to_csv(csvFileName, sep='|', index = False)
    #
    #     with open(csvFileName, 'r') as f:
    #         reader = csv.reader(f, delimiter='|')
    #         columns = next(reader)
    #         query = 'insert into dbo.PredictionResult({0}) values ({1})'
    #         query = query.format(','.join(columns), ','.join('?' * len(columns)))
    #         print(query)
    #         cursor = connections['default'].cursor()
    #         for data in reader:
    #             print(data)
    #             cursor.execute(query, data)
    #         cursor.commit()


        # df is the dataframe containing an index and the columns "Event" and "Day"
        # create Index column to use as primary key
        # mergedResultedDF.reset_index(inplace=True)
        # mergedResultedDF.rename(columns={'index': 'Index'}, inplace=True)
        #
        # # create the table but first drop if it already exists
        # command = '''IF OBJECT_ID('[dbo].[PredictionResult]', 'U') IS NOT NULL DROP TABLE [dbo].[PredictionResult];
        #             CREATE TABLE [dbo].[PredictionResult]
        #             (
        #                 [Index] int not null primary key,
        #                 [UserId] [varchar](max) NULL,
        #                 [Address] [varchar](max) NULL,
        #                 [TotalQuantity] [real] NULL,
        #                 [TotalValue] [real] NULL,
        #                 [StDevQuantity] [real] NULL,
        #                 [StDevValue] [real] NULL,
        #                 [AvgTimeDelta] [real] NULL,
        #                 [Recency] [real] NULL,
        #                 [UniqueTransactionId] [real] NULL,
        #                 [UniqueItemId] [real] NULL,
        #                 [UniqueLocation] [real] NULL,
        #                 [UniqueProductCategory] [real] NULL,
        #                 [TotalQuantityperUniqueTransactionId] [real] NULL,
        #                 [TotalQuantityperUniqueItemId] [real] NULL,
        #                 [TotalQuantityperUniqueLocation] [real] NULL,
        #                 [TotalQuantityperUniqueProductCategory] [real] NULL,
        #                 [TotalValueperUniqueTransactionId] [real] NULL,
        #                 [TotalValueperUniqueItemId] [real] NULL,
        #                 [TotalValueperUniqueLocation] [real] NULL,
        #                 [TotalValueperUniqueProductCategory] [real] NULL,
        #                 [PredictedResult] [bigint] NULL
        #             );'''
        # connection = engine.raw_connection()
        # cursor = connection.cursor()
        # cursor.execute(command)
        # connection.commit()
        #
        # # stream the data using 'to_csv' and StringIO(); then use sql's 'copy_from' function
        # output = StringIO()
        # # ignore the index
        # mergedResultedDF.to_csv(output, sep='\t', header=False, index=False)
        # # jump to start of stream
        # output.seek(0)
        # contents = output.getvalue()
        # #cur = connection.cursor()
        # # null values become ''
        # cursor.copy_from(output, 'PredictionResult', null="")
        # connection.commit()
        # cursor.close()



# class PreAnalysisChurn(models.Model):
#     #PreAnalysisId = models.AutoField(db_column='pId', primary_key=True)
#     user = models.CharField(db_column='user', max_length=100)  # Field name made lowercase.
#     figureName = models.CharField(db_column='figureName', max_length=100)
#     figurePath = models.ImageField(db_column='figurePath',upload_to='/ChunApp/static/GeneratedImage/', blank=True)
#     figuretype = models.CharField(db_column='figuretype', max_length=30)
#     entryTime = models.DateTimeField(auto_now_add= True ,blank=True)
#
#     class Meta:
#         managed = False
#         db_table = 'PreAnalysisChurn'
#
#     def __str__(self):
#         return self.figureName


class PredictionResult(models.Model):
    class Meta:
        managed = False
        db_table = 'PredictionResult'

