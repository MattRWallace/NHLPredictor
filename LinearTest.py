import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def linear_regression(x, y, new_data=None):
    # create LR model
    model = LinearRegression()

    # Fit
    model.fit(x, y)

    # r-squared
    y_pred = model.predict(x)
    r_squared = r2_score(y, y_pred)
    print("R-squared: ", r_squared)

    # P-Values
    x_intercept = sm.add_constant(x)
    model_sm = sm.OLS(y, x_intercept).fit()
    print("P-Values: ", model_sm.pvalues)

    # Coefficients
    print("Coef: ", model.coef_)
    print("Intercept: ", model.intercept_)

    # Predictions
    if new_data is not None:
        predictions = model.predict(new_data)
        print("Predictions based on new data: ", predictions)

# Data pass
x = np.array([[22, 78, 5], [5, 62, 33], [96, 23, 23], [53, 21, 43], [50, 87, 94], [6, 41, 92], [46, 72, 20], [73, 35, 64], [94, 98, 63], [4, 13, 73], [36, 78, 3], [95, 60, 58], [7, 74, 83], [47, 33, 40]])
y = np.array([10, 38, 72, 42, 38, 46, 40, 2, 59, 40, 14, 5, 19, 64])
new_data = np.array([[150, 111, 112], [113, 114, 115]])

linear_regression(x, y, new_data=new_data)