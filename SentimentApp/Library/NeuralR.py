# import os
# os.environ['R_HOME'] = 'C:\Program Files\R\R-3.4.1'
# os.environ['R_USER'] = 'C:\Anaconda3\Lib\site-packages\rpy2'
# import rpy2.robjects as robjects
# from rpy2.robjects.packages import importr
# import pandas as pd
# from rpy2.robjects import pandas2ri
#
#
# def NeuralR():
#     ts = robjects.r('ts')
#     # forecast = importr('forecast')
#     pandas2ri.activate()
#     traindf = pd.read_csv(r'D:\Projects\Python\sentiment-analysis-repository\SentimentApp\Library\UKgas.csv', index_col=0)
#     traindf.index = traindf.index.to_datetime()
#
#     # rdata = ts(traindf.Price.values, frequency=4)
#
#     rstring = """
#         function(testdata){
#             library(forecast)
#             fitted_model<-auto.arima(testdata)
#             forecasted_data<-forecast(fitted_model,h=16,level=c(95))
#             outdf<-data.frame(forecasted_data$mean,forecasted_data$lower,forecasted_data$upper)
#             colnames(outdf)<-c('forecast','lower_95_pi','upper_95_pi')
#             outdf
#         }
#     """
#
#     rStringTest = """
#             function(){
#                 set.seed(500)
#                 library(MASS)
#                 data <- Boston
#
#                 apply(data,2,function(x) sum(is.na(x)))
#
#                 index <- sample(1:nrow(data),round(0.75*nrow(data)))
#                 train <- data[index,]
#                 test <- data[-index,]
#                 lm.fit <- glm(medv~., data=train)
#                 summary(lm.fit)
#                 pr.lm <- predict(lm.fit,test)
#                 MSE.lm <- sum((pr.lm - test$medv)^2)/nrow(test)
#
#                 maxs <- apply(data, 2, max)
#                 mins <- apply(data, 2, min)
#
#                 scaled <- as.data.frame(scale(data, center = mins, scale = maxs - mins))
#
#                 train_ <- scaled[index,]
#                 test_ <- scaled[-index,]
#
#                 library(neuralnet)
#                 n <- names(train_)
#                 f <- as.formula(paste("medv ~", paste(n[!n %in% "medv"], collapse = " + ")))
#                 nn <- neuralnet(f,data=train_,hidden=c(5,3),linear.output=T)
#
#                 plot(nn)
#             }
#         """
#
#     rfunc = robjects.r(rStringTest)
#
#     # rdata = ts(traindf.values, frequency=4)
#     # r_df = rfunc(rdata)
#     # forecast_df = pandas2ri.ri2py(r_df)
#     # forecast_df.index = pd.date_range(start=traindf.index.max(), periods=len(forecast_df) + 1, freq='QS')[1:]
#
#     r_df = rfunc()
#     print(r_df)