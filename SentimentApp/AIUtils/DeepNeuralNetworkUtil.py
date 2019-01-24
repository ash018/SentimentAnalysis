from django.db import connection
from keras.models import Sequential
from keras.layers import Dense, Dropout
import numpy
import pandas as pd
from sklearn import preprocessing


class Song(object):

    def __init__(self, lyrics):
        self.lyrics = lyrics

    def sing_me_a_song(self):
        for line in self.lyrics:
            print(line)

class DeepNeuralNetwork(object):

    def __init__(self, SampleDatasetName):

        def LoadDiabetesData(self):
            with connection.cursor() as cursor:
                cursor.execute("SELECT  [PregnantTimes],[Plasma],[Diastolic],[Triceps],[Insulin],[Mass],[Pedigree],[Age],[HasDiabetes] FROM [dbo].[DatasetDiabetes]")
                row = cursor.fetchall()
            return row

        def LoadPharmaPerformance(self):
            with connection.cursor() as cursor:
                cursor.execute("SELECT  [districtcode], [thanacode], [creditdays], [TotalInvoice], [TotalSales]/1000 [TotalSales], [creditlimit]/1000 as [creditlimit], [Performance] "
                               "FROM [dbo].[PharmaCreditLimit]"
                               "where [creditlimit] between 100 and 1000000 "
                               "and TotalSales between 100 and 2000000")
                row = cursor.fetchall()
            return row

        def LoadPharmaPerformance2(self):
            with connection.cursor() as cursor:
                cursor.execute("SELECT [creditdays], [TotalInvoice], [TotalSales]/1000 [TotalSales], [creditlimit]/1000 as [creditlimit], [Performance] FROM [dbo].[PharmaCreditLimit]"
                                  "where [creditlimit] between 100 and 1000000 "
                                    "and TotalSales between 100 and 2000000")
                row = cursor.fetchall()
            return row

        self.datasetname = SampleDatasetName
        if self.datasetname == 'Diabetes':
            self.dataset = numpy.array(LoadDiabetesData(self), dtype=float)
        elif self.datasetname == 'PredictPharmaPerformance':
            self.dataset = numpy.array(LoadPharmaPerformance(self), dtype=float)
        elif self.datasetname == 'PredictPharmaPerformance2':
            self.dataset = numpy.array(LoadPharmaPerformance2(self), dtype=float)
        #print(self.dataset)

    def GenerateTrainTestDataset(self, trainDataSize, testDataSize, totalInputs):
        self.inTotal = trainDataSize + testDataSize
        self.X = self.dataset[0:trainDataSize, 0:totalInputs]
        self.Y = self.dataset[0:trainDataSize, totalInputs]
        self.TestX = self.dataset[trainDataSize:self.inTotal, 0:totalInputs]
        self.TestY = self.dataset[trainDataSize:self.inTotal, totalInputs]

    def PrepareModel_BinaryClassification(self, totalInputs):
        self.seed = 100
        numpy.random.seed(self.seed)
        #creating a [16,8,1] type neural network
        self.model = Sequential()
        self.model.add(Dense(16, input_dim=totalInputs, init='uniform', activation='relu'))
        self.model.add(Dropout(0.1))
        self.model.add(Dense(8, init='uniform', activation='relu'))
        self.model.add(Dropout(0.1))
        self.model.add(Dense(1, init='uniform', activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    def PrepareModel_RegressionClassification(self, totalInputs):
        self.seed = 55
        numpy.random.seed(self.seed)
        self.model = Sequential()
        self.model.add(Dense(32, input_dim=totalInputs, init='normal', activation='relu'))
        # self.model.add(Dropout(0.1))
        # self.model.add(Dense(16, init='normal', activation='linear'))
        # # self.model.add(Dropout(0.1))
        # self.model.add(Dense(18, init='normal', activation='relu'))
        # # self.model.add(Dropout(0.1))
        # self.model.add(Dense(8, init='normal', activation='elu'))
        # # self.model.add(Dropout(0.1))
        # self.model.add(Dense(18, init='normal', activation='relu'))

        self.model.add(Dense(1, init='normal'))
        self.model.compile(loss='mean_absolute_error', optimizer='rmsprop')

    def FitModel(self, epoch, batchSize):
        self.model.fit(self.X, self.Y, nb_epoch=epoch, batch_size=batchSize)

    def EvaluateModel(self):
        # evaluate the model
        self.scores = self.model.evaluate(self.X, self.Y)
        print("%s: %.2f%%" % (self.model.metrics_names[1], self.scores[1] * 100))
        return self.scores[1] * 100

    def PredictModel(self):
        self.predictions = self.model.predict(self.TestX)

    def GetFinalResult(self, testDataSize, totalInputs, output_filename):
        i=0
        colList = []
        while i < totalInputs:
            colList.append('Col' + str(i+1))
            i+=1

        self.PredictedDF = pd.DataFrame(data=self.predictions, index=list(range(testDataSize)), columns=['DNN_Predict'])

        self.TestDF_X = pd.DataFrame(data=self.TestX, index=list(range(testDataSize)), columns=colList)

        self.TestDF_Y = pd.DataFrame(data=self.TestY, index=list(range(testDataSize)), columns=['Actual'])

        result = pd.concat([self.TestDF_X, self.TestDF_Y, self.PredictedDF], axis=1)

        result['Error'] = abs((result['Actual'] - result['DNN_Predict'])) / result['Actual'] * 100

        pd.DataFrame(result).to_csv(output_filename, sep=',', index=False)

        return pd.DataFrame(result)

























