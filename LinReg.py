%matplotlib inline
import pandas as pd
from sklearn import linear_model, preprocessing, svm
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LassoLars, ElasticNet
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.grid_search import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.externals import joblib
import random
import numpy as np
from scipy.stats import norm
import pylab as pl
import math


grandtable = pd.read_csv('_grandtable.csv')

# grandtable.plot(x='Year', y='LymeCases', kind='scatter')
X = grandtable.drop(grandtable.columns[[0,2,3]], axis=1)
Xid = grandtable[[3]]
y = grandtable[[2]]
Xcol = X.columns
X = pd.DataFrame(preprocessing.scale(X), columns = Xcol)
#y = np.sqrt(y)
X['county'] = Xid
X['lymecases'] = y
X = X.set_index('county')
grandscale = X

'''For SQL upload'''
X.to_sql('grandscale', engine, if_exists='replace')

'''Resume here'''
trainset = grandscale[grandscale.lymecases.isnull() == False]
futurepredict = grandscale[grandscale.lymecases.isnull() == True]

X = trainset.drop('lymecases', axis=1)    # Strip lymecases away from trainset
y = trainset[[24]]    # Isolate lymecases away from trainset
y = np.sqrt(y)
futureX = futurepredict.drop('lymecases', axis=1)      # Stip lymecases away from futurepredict

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=0)
''''''
ols = linear_model.LinearRegression()
model = ols.fit(X_train, y_train)
model.coef_                             # Coefficients/weights?
model.score(X_test, y_test)             # R^2 score
# Year only: R^2 = 0.23, Lyme = -13621.48 + 6.885 * Yr
model.intercept_

list(model.predict(X_test)[0:5])
list(y_test)[0:5]
((y_test - model.predict(X_test)) ** 2).sum()  # RSS
np.mean((model.predict(X_test) - y_test) ** 2)  # MSE

''''''

slr = LinearRegression()

slr.fit(X_train, y_train)
y_train_pred = slr.predict(X_train)
y_test_pred = slr.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 1124.252, test: 2212.719       # Bio01
# MSE train: 1014.180, test: 2946.979       # Bio01, Bio02
# Severe overfitting with Bio1–8
# MSE train: 15121.107, test: 20063.472     # Full bio
# MSE train: 14737.911, test: 19288.242     # With pop
# MSE train: 18669.408, test: 17243.482     # w/ NH/VT
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: 0.446, test: 0.332     #Bio01
# R^2 train: 0.500, test: 0.110     #Bio01, Bio02
# Severe overfitting with Bio1–8
# R^2 train: 0.684, test: 0.128     # Full bio
# R^2 train: 0.692, test: 0.162     # With pop
# R^2 train: 0.448, test: 0.352     # w/ NH/VT


slr.fit(X_train, y_train).coef_
# array([[ 36.02384887,  -5.22981331]])
# array([[ 35.75486307, -10.35803815,  18.64272682]])
slr.fit(X_train, y_train).score(X_test, y_test) #R^2 on test set

result = slr.predict(futureX)
#result = result[0][0]
#result = int(result)
#print result

'''Ridge regression'''

rrc = Ridge()

rrc.fit(X_train,y_train)
y_train_pred = rrc.predict(X_train)
y_test_pred = rrc.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 1144.035, test: 2474.597       # Bio01
# MSE train: 1042.990, test: 2817.660       # Bio01, Bio02
# MSE train: 17178.728, test: 19720.481     # full bio
# MSE train: 16861.713, test: 18842.148     # with pop
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: 0.436, test: 0.253
# R^2 train: 0.486, test: 0.149
# Worse than simple linear regression!
# R^2 train: 0.641, test: 0.143     #full bio
# R^2 train: 0.648, test: 0.181     # with pop

'''Lasso'''
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)
y_train_pred = lasso.predict(X_train)
y_test_pred = lasso.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 1124.312, test: 2226.141
# MSE train: 1014.291, test: 2924.448
# MSE train: 15562.842, test: 19199.434
# MSE train: 15229.264, test: 18447.983     # with pop
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: 0.446, test: 0.328
# R^2 train: 0.500, test: 0.117
# R^2 train: 0.675, test: 0.166     # full bio
# R^2 train: 0.682, test: 0.198     # with pop
# Still worse than simple linear regression!

'''Lasso LARS'''
lassol = LassoLars(alpha=0.1)
lassol.fit(X_train, y_train)
y_train_pred = lassol.predict(X_train)
y_test_pred = lassol.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 17549.219, test: 19599.301     # full bio
# MSE train: 17244.574, test: 18728.144     # with pop
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: 0.633, test: 0.148         # full bio
# R^2 train: 0.640, test: 0.186         # with pop
# Still worse than simple linear regression!

'''ElasticNet'''
elast = ElasticNet(alpha=0.1)
elast.fit(X_train, y_train)
y_train_pred = elast.predict(X_train)
y_test_pred = elast.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 18342.896, test: 19481.151     # full bio
# MSE train: 17970.743, test: 17833.676     # with pop
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: 0.617, test: 0.154         # full bio
# R^2 train: 0.624, test: 0.225         # with pop
# Still worse than simple linear regression!

'''SVM'''
sup = svm.NuSVR()
sup.fit(X_train, y_train)
y_train_pred = sup.predict(X_train)
y_test_pred = sup.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 53938.086, test: 22670.365
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: -0.127, test: 0.015

'''Random Forest Regressor'''

# Try a randomized search for 'n_estimators' (number of trees in forest)
n_estimators = np.random.normal(1000, 500, 30).astype(int)
hyperparameters = {'n_estimators':list(n_estimators)}

randomCV = RandomizedSearchCV(RandomForestRegressor(), param_distributions=hyperparameters, n_iter=10)
randomCV.fit(X_train, np.ravel(y_train))
best_n_estim = randomCV.best_params_['n_estimators']
print best_n_estim

trees = RandomForestRegressor(n_estimators = 1000, n_jobs = 2, oob_score=True)
trees.fit(X_train, np.ravel(y_train))
y_train_pred = trees.predict(X_train)
y_test_pred = trees.predict(X_test)

print('MSE train: %.3f, test: %.3f' % (
        mean_squared_error(y_train, y_train_pred),
        mean_squared_error(y_test, y_test_pred)))
# MSE train: 2197.075, test: 14939.625      # full bio
# MSE train: 1745.783, test: 8238.066       # with pop
# MSE train: 3361.140, test: 13738.915      # + CT, RI
# MSE train: 0.014, test: 0.100             # log-transformed
# MSE train: 1.220, test: 8.254             # sqrt-transformed
print('R^2 train: %.3f, test: %.3f' % (
        r2_score(y_train, y_train_pred),
        r2_score(y_test, y_test_pred)))
# R^2 train: 0.954, test: 0.351         # full bio
# R^2 train: 0.964, test: 0.642         # with pop
# R^2 train: 0.907, test: 0.618         # + CT, RI
# R^2 train: 0.944, test: 0.537         # full
# R^2 train: 0.979, test: 0.841         # log-transformed
# R^2 train: 0.971, test: 0.784         # sqrt-transformed, but large values better predicted?

trees.feature_importances_
trees.predict(futureX)
predict15 = pd.DataFrame((trees.predict(futureX))*(trees.predict(futureX)))
predict15['county'] = futureX.index
predict15 = predict15.set_index('county')
predict15.rename(columns={0:'lymecasespred'}, inplace=True)
'''Save to csv, upload to SQL database'''
predict15.to_csv('predict15.csv')
predict15.to_sql('predict15', engine, if_exists='replace')
'''Resume'''

with open('rf.pickle', 'wb') as f:
    pickle.dump(trees, f)
with open('rf.pickle', 'rb') as f:
    forest = pickle.load(f)
    trees = pickle.load(f)

f = 'rf.jblb'
joblib.dump(trees, f, compress=3)
crzy = joblib.load(f)

'''Plot predictions vs. actual'''
r2 = r2_score(y_test, y_test_pred)

pl.clf()
#pl.scatter(np.log(y_test), np.log(y_test_pred))
pl.scatter(y_test, y_test_pred)
pl.plot(label="r^2=" + str(r2), c="r")
pl.legend(loc="lower right")
pl.title("RandomForest Regression with scikit-learn")
pl.savefig('RFtest_sqrt.png')
