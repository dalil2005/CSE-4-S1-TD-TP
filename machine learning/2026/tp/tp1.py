from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from sklearn.datasets import fetch_openml
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


BASE_DIR = Path(__file__).resolve().parent


print("numpy        :", np.__version__)
print("pandas       :", pd.__version__)
print("scikit-learn :", __import__('sklearn').__version__)


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def initialize_parameters(n):
    w = np.zeros((n, 1))
    b = 0.0
    return w, b


def compute_cost_and_gradients(X, y, w, b, lambda_=0.0):
    m = X.shape[0]
    y = y.reshape(-1, 1)
    z = X @ w + b
    A = sigmoid(z)
    cost = -(1 / m) * np.sum(y * np.log(A + 1e-8) + (1 - y) * np.log(1 - A + 1e-8))
    dw = (1 / m) * (X.T @ (A - y))
    db = (1 / m) * np.sum(A - y)
    return cost, dw, db


def gradient_descent(X, y, w, b, alpha=0.1, num_iters=1000, compute_fn=None, lambda_=0.0):
    if compute_fn is None:
        compute_fn = compute_cost_and_gradients
    costs = []
    for _ in range(num_iters):
        cost, dw, db = compute_fn(X, y, w, b, lambda_)
        w = w - alpha * dw
        b = b - alpha * db
        costs.append(cost)
    return w, b, costs


def predict(X, w, b):
    probs = sigmoid(X @ w + b)
    return (probs >= 0.5).astype(int)


def compute_cost_and_gradients_L2(X, y, w, b, lambda_):
    m = X.shape[0]
    y = y.reshape(-1, 1)
    z = X @ w + b
    A = sigmoid(z)
    cost = -(1 / m) * np.sum(y * np.log(A + 1e-8) + (1 - y) * np.log(1 - A + 1e-8))
    cost += (lambda_ / (2 * m)) * np.sum(w ** 2)
    dw = (1 / m) * (X.T @ (A - y)) + (lambda_ / m) * w
    db = (1 / m) * np.sum(A - y)
    return cost, dw, db


def compute_cost_and_gradients_L1(X, y, w, b, lambda_):
    m = X.shape[0]
    y = y.reshape(-1, 1)
    z = X @ w + b
    A = sigmoid(z)
    cost = -(1 / m) * np.sum(y * np.log(A + 1e-8) + (1 - y) * np.log(1 - A + 1e-8))
    cost += (lambda_ / m) * np.sum(np.abs(w))
    dw = (1 / m) * (X.T @ (A - y)) + (lambda_ / m) * np.sign(w)
    db = (1 / m) * np.sum(A - y)
    return cost, dw, db


def compute_cost_and_gradients_EN(X, y, w, b, lambda_, rho=0.5):
    m = X.shape[0]
    y = y.reshape(-1, 1)
    z = X @ w + b
    A = sigmoid(z)
    log_loss = -(1 / m) * np.sum(y * np.log(A + 1e-8) + (1 - y) * np.log(1 - A + 1e-8))
    l1_term = (lambda_ * rho / m) * np.sum(np.abs(w))
    l2_term = (lambda_ * (1 - rho) / (2 * m)) * np.sum(w ** 2)
    cost = log_loss + l1_term + l2_term
    dw = (1 / m) * (X.T @ (A - y)) + (lambda_ * rho / m) * np.sign(w) + (lambda_ * (1 - rho) / m) * w
    db = (1 / m) * np.sum(A - y)
    return cost, dw, db


def linear_regression_demo():
    salary_df = pd.read_csv(BASE_DIR / 'salary_data.csv')
    print('\nSalary dataset sample:\n', salary_df.head())
    print('\nDataset info:')
    salary_df.info()
    print('\nDescriptive statistics:\n', salary_df.describe())

    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=salary_df, x='YearsExperience', y='Salary')
    plt.title('Salary vs Years of Experience')
    plt.xlabel('Years of Experience')
    plt.ylabel('Salary')
    plt.tight_layout()
    plt.show()

    corr = salary_df.corr().iloc[0, 1]
    print(f'\nPearson correlation coefficient: {corr:.4f}')
    print('The relationship is strongly linear, which supports linear regression.')

    X = salary_df[['YearsExperience']].values
    y = salary_df['Salary'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    print('\nLinear Regression coefficients:')
    print('Intercept:', model.intercept_)
    print('Slope:', model.coef_[0])

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f'MSE on test set: {mse:.2f}')
    print(f'R^2 on test set: {r2:.4f}')

    train_x = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
    train_y = model.predict(train_x)
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=salary_df, x='YearsExperience', y='Salary', alpha=0.7)
    plt.plot(train_x, train_y, color='red', linewidth=2, label='Linear regression fit')
    plt.title('Linear Regression Fit')
    plt.xlabel('Years of Experience')
    plt.ylabel('Salary')
    plt.legend()
    plt.tight_layout()
    plt.show()

    alpha_values = [0.1, 1, 10]
    models = []
    for alpha in alpha_values:
        models.append(('Ridge', Ridge(alpha=alpha), alpha))
        models.append(('Lasso', Lasso(alpha=alpha, max_iter=10000), alpha))
        models.append(('ElasticNet', ElasticNet(alpha=alpha, l1_ratio=0.5, max_iter=10000), alpha))

    results = []
    for name, estimator, alpha in models:
        estimator.fit(X_train, y_train)
        pred = estimator.predict(X_test)
        mse = mean_squared_error(y_test, pred)
        r2 = r2_score(y_test, pred)
        coef = estimator.coef_[0] if hasattr(estimator, 'coef_') else np.nan
        results.append({
            'Model': name,
            'alpha': alpha,
            'MSE (test)': mse,
            'R² (test)': r2,
            'Estimated coefficient': coef,
        })

    results_df = pd.DataFrame(results)
    print('\nRegularized regression summary:\n')
    print(results_df.to_string(index=False))


def logistic_regression_demo():
    data = fetch_openml(name='heart-disease', version=1, as_frame=True)
    df = data.frame.copy()
    print('\nHeart disease dataset sample:\n', df.head())
    print('\nMissing values per column:\n', df.isnull().sum())

    if df.isnull().sum().sum() > 0:
        df = df.dropna().reset_index(drop=True)

    y = df['target'].astype(int)
    X = df.drop(columns=['target'])
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    X_train = X_train.reshape(X_train.shape[0], -1)
    X_test = X_test.reshape(X_test.shape[0], -1)
    y_train = y_train.to_numpy().reshape(-1, 1)
    y_test = y_test.to_numpy().reshape(-1, 1)

    w, b = initialize_parameters(X_train.shape[1])
    w, b, costs = gradient_descent(X_train, y_train, w, b, alpha=0.1, num_iters=1000, compute_fn=compute_cost_and_gradients)
    plt.figure(figsize=(8, 5))
    plt.plot(costs)
    plt.title('Cost over iterations (No regularization)')
    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.show()

    y_pred = predict(X_test, w, b).reshape(-1)
    y_test_flat = y_test.reshape(-1)
    acc = accuracy_score(y_test_flat, y_pred)
    cm = confusion_matrix(y_test_flat, y_pred)
    print(f'\nAccuracy (baseline logistic regression): {acc:.4f}')
    print('Confusion matrix:\n', cm)
    print('Interpretation: the matrix shows true positives, true negatives, false positives, and false negatives. In medicine, false negatives are often the most costly because a diseased patient may not receive treatment.')

    lambda_l2 = 1.0
    w_l2, b_l2 = initialize_parameters(X_train.shape[1])
    w_l2, b_l2, costs_l2 = gradient_descent(X_train, y_train, w_l2, b_l2, alpha=0.5, num_iters=2000, compute_fn=compute_cost_and_gradients_L2, lambda_=lambda_l2)
    plt.figure(figsize=(8, 5))
    plt.plot(costs_l2)
    plt.title('Cost over iterations (L2 regularization)')
    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.show()
    y_pred_l2 = predict(X_test, w_l2, b_l2).reshape(-1)
    print(f'Accuracy (L2): {accuracy_score(y_test_flat, y_pred_l2):.4f}')
    print('Confusion matrix (L2):\n', confusion_matrix(y_test_flat, y_pred_l2))

    lambda_l1 = 0.1
    w_l1, b_l1 = initialize_parameters(X_train.shape[1])
    w_l1, b_l1, costs_l1 = gradient_descent(X_train, y_train, w_l1, b_l1, alpha=0.5, num_iters=2000, compute_fn=compute_cost_and_gradients_L1, lambda_=lambda_l1)
    plt.figure(figsize=(8, 5))
    plt.plot(costs_l1)
    plt.title('Cost over iterations (L1 regularization)')
    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.show()
    y_pred_l1 = predict(X_test, w_l1, b_l1).reshape(-1)
    print(f'Accuracy (L1): {accuracy_score(y_test_flat, y_pred_l1):.4f}')
    print('Confusion matrix (L1):\n', confusion_matrix(y_test_flat, y_pred_l1))

    lambda_en = 0.1
    rho = 0.5
    w_en, b_en = initialize_parameters(X_train.shape[1])
    w_en, b_en, costs_en = gradient_descent(X_train, y_train, w_en, b_en, alpha=0.5, num_iters=2000, compute_fn=lambda X, y, w, b, reg: compute_cost_and_gradients_EN(X, y, w, b, reg, rho=rho), lambda_=lambda_en)
    plt.figure(figsize=(8, 5))
    plt.plot(costs_en)
    plt.title('Cost over iterations (Elastic Net regularization)')
    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.show()
    y_pred_en = predict(X_test, w_en, b_en).reshape(-1)
    print(f'Accuracy (Elastic Net): {accuracy_score(y_test_flat, y_pred_en):.4f}')
    print('Confusion matrix (Elastic Net):\n', confusion_matrix(y_test_flat, y_pred_en))


if __name__ == '__main__':
    linear_regression_demo()
    logistic_regression_demo()
