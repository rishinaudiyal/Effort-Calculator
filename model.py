import numpy as np
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
data=pd.read_csv("sat_Update2.csv")
x=data.iloc[:,1].values
y=data.iloc[:,-1].values
vectorizer = CountVectorizer()
x_vec=vectorizer.fit_transform(x).toarray()
le = LabelEncoder()
y =  le.fit_transform(y)
x_train,x_test,y_train,y_test=train_test_split(x_vec,y,test_size=0.1,random_state=0)
rfc=RandomForestClassifier(n_estimators=100,criterion='entropy')
rfc.fit(x_train,y_train)
pickle.dump((vectorizer,rfc),open('model.pkl','wb'))