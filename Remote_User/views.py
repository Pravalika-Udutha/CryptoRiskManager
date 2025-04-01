from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
import datetime
import openpyxl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.ensemble import VotingClassifier
from sklearn.tree import DecisionTreeClassifier
import warnings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
from Remote_User.models import ClientRegister_Model, financial_risk_type, detection_ratio, detection_accuracy

warnings.filterwarnings("ignore")
plt.style.use('ggplot')

def login(request):
    if request.method == "POST" and 'submit1' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = ClientRegister_Model.objects.get(username=username, password=password)
            request.session["userid"] = user.id
            return redirect('ViewYourProfile')
        except ClientRegister_Model.DoesNotExist:
            pass
    return render(request, 'RUser/login.html')

def RegisterUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phoneno = request.POST.get('phoneno')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        ClientRegister_Model.objects.create(username=username, email=email, password=password, phoneno=phoneno,
                                            country=country, state=state, city=city, address=address, gender=gender)
        obj = "Registered Successfully"
        return render(request, 'RUser/RegisterUser.html', {'object': obj})
    else:
        return render(request,'RUser/RegisterUser.html')

def ViewYourProfile(request):
    userid = request.session.get('userid')
    if userid:
        user = get_object_or_404(ClientRegister_Model, id=userid)
        return render(request, 'RUser/ViewYourProfile.html', {'object': user})
    # Handle the case when user is not logged in

def predict_crypto_currency_financial_risk_type(request):
    if request.method == "POST":
        volume_usd_24h= request.POST.get('volume_usd_24h')
        available_supply= request.POST.get('available_supply')
        idn= request.POST.get('idn')
        last_updated= request.POST.get('last_updated')
        market_cap_usd= request.POST.get('market_cap_usd')
        max_supply= request.POST.get('max_supply')
        name= request.POST.get('name')
        percent_change_1h= request.POST.get('percent_change_1h')
        percent_change_24h= request.POST.get('percent_change_24h')
        percent_change_7d= request.POST.get('percent_change_7d')
        price_btc= request.POST.get('price_btc')
        price_usd= request.POST.get('price_usd')
        rank= request.POST.get('rank')
        symbol= request.POST.get('symbol')
        total_supply= request.POST.get('total_supply')

        df = pd.read_csv('Crypto_Currency_Datasets.csv')
        df
        df.columns

        df['label'] = df.Label.apply(lambda x: 1 if x == 1 else 0)
        df.head()

        cv = CountVectorizer()
        X = df['name']
        y = df['label']

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

        classifier = VotingClassifier(models)
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)


        crypto_currency_name = [name]
        vector1 = cv.transform(crypto_currency_name).toarray()
        predict_text = classifier.predict(vector1)

        pred = str(predict_text).replace("[", "")
        pred1 = pred.replace("]", "")

        prediction = int(pred1)

        if prediction == 0:
            val = 'No Risk Found'
        elif prediction == 1:
            val = 'Risk Found'

        print(val)
        print(pred1)

        financial_risk_type.objects.create(
        volume_usd_24h=volume_usd_24h,
        available_supply=available_supply,
        idn=idn,
        last_updated=last_updated,
        market_cap_usd=market_cap_usd,
        max_supply=max_supply,
        name=name,
        percent_change_1h=percent_change_1h,
        percent_change_24h=percent_change_24h,
        percent_change_7d=percent_change_7d,
        price_btc=price_btc,
        price_usd=price_usd,
        rank=rank,
        symbol=symbol,
        total_supply=total_supply,
        Prediction=val)

        return render(request, 'RUser/predict_crypto_currency_financial_risk_type.html',{'objs': val})
    return render(request, 'RUser/predict_crypto_currency_financial_risk_type.html')

