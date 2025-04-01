from django.shortcuts import render, redirect
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
import datetime
import xlwt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.ensemble import VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score, precision_score, recall_score, matthews_corrcoef
from Remote_User.models import ClientRegister_Model, financial_risk_type, detection_ratio, detection_accuracy
import warnings

warnings.filterwarnings("ignore")
plt.style.use('ggplot')

def serviceproviderlogin(request):
    if request.method == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password == "admin":
            return redirect('View_Remote_Users')
    return render(request, 'SProvider/serviceproviderlogin.html')

def Find_Crypto_Currency_Financial_Risk_Type_Ratio(request):
    detection_ratio.objects.all().delete()
    kwords = [('No Risk Found', 'Prediction'), ('Risk Found', 'Prediction')]
    for kword, field in kwords:
        obj = financial_risk_type.objects.filter(Q(**{field: kword}))
        count = obj.count()
        count_all = financial_risk_type.objects.count()
        ratio = (count / count_all) * 100 if count_all else 0
        if ratio:
            detection_ratio.objects.create(names=kword, ratio=ratio)
    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/Find_Crypto_Currency_Financial_Risk_Type_Ratio.html', {'objs': obj})

def View_Remote_Users(request):
    obj = ClientRegister_Model.objects.all()
    return render(request, 'SProvider/View_Remote_Users.html', {'objects': obj})


def ViewTrendings(request):
    topic = financial_risk_type.objects.values('topics').annotate(dcount=Count('topics')).order_by('-dcount')
    return  render(request,'SProvider/ViewTrendings.html',{'objects':topic})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Prediction_Crypto_Currency_Financial_Risk_Type(request):
    obj =financial_risk_type.objects.all()
    return render(request, 'SProvider/View_Prediction_Crypto_Currency_Financial_Risk_Type.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Trained_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="TrainedData.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = financial_risk_type.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1

        ws.write(row_num, 0, my_row.volume_usd_24h, font_style)
        ws.write(row_num, 1, my_row.available_supply, font_style)
        ws.write(row_num, 2, my_row.idn, font_style)
        ws.write(row_num, 3, my_row.last_updated, font_style)
        ws.write(row_num, 4, my_row.market_cap_usd, font_style)
        ws.write(row_num, 5, my_row.max_supply, font_style)
        ws.write(row_num, 6, my_row.name, font_style)
        ws.write(row_num, 7, my_row.percent_change_1h, font_style)
        ws.write(row_num, 8, my_row.percent_change_24h, font_style)
        ws.write(row_num, 9, my_row.percent_change_7d, font_style)
        ws.write(row_num, 10, my_row.price_btc, font_style)
        ws.write(row_num, 11, my_row.price_usd, font_style)
        ws.write(row_num, 12, my_row.rank, font_style)
        ws.write(row_num, 13, my_row.symbol, font_style)
        ws.write(row_num, 14, my_row.total_supply, font_style)
        ws.write(row_num, 15, my_row.Prediction, font_style)

    wb.save(response)
    return response

def Train_Test_DataSets(request):
    detection_accuracy.objects.all().delete()

    df = pd.read_csv('Crypto_Currency_Datasets.csv')
    df
    df.columns

    df['Results'] = df.Label.apply(lambda x: 1 if x == 1 else 0)
    df.head()


    cv = CountVectorizer()
    X = df['name']
    y = df['Results']

    print("Currency Name")
    print(X)
    print("Label")
    print(y)

    X = cv.fit_transform(X)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Naive Bayes")

    from sklearn.naive_bayes import MultinomialNB
    NB = MultinomialNB()
    NB.fit(X_train, y_train)
    predict_nb = NB.predict(X_test)
    naivebayes = accuracy_score(y_test, predict_nb) * 100
    print(naivebayes)
    print(confusion_matrix(y_test, predict_nb))
    print(classification_report(y_test, predict_nb))
    models.append(('naive_bayes', NB))
    detection_accuracy.objects.create(names="Naive Bayes", ratio=naivebayes)

    # SVM Model
    print("SVM")
    from sklearn import svm
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    models.append(('svm', lin_clf))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)


    print("Logistic Regression")

    from sklearn.linear_model import LogisticRegression
    reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('logistic', reg))

    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)

    print("Decision Tree Classifier")
    dtc = DecisionTreeClassifier()
    dtc.fit(X_train, y_train)
    dtcpredict = dtc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, dtcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, dtcpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, dtcpredict))
    detection_accuracy.objects.create(names="Decision Tree Classifier",ratio=accuracy_score(y_test, dtcpredict) * 100)


    predicts = 'predicts.csv'
    df.to_csv(predicts, index=False)
    df.to_markdown

    obj = detection_accuracy.objects.all()


    return render(request,'SProvider/Train_Test_DataSets.html', {'objs': obj})