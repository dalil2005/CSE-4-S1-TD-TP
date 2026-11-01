#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACHINE LEARNING — COMPLETE STUDY & TP HANDBOOK
================================================
A bilingual (English + Arabic) learning companion based on the supplied tp1.py.

WHAT THIS FILE COVERS
---------------------
1. AI, Machine Learning and supervised learning
2. Datasets, features, labels, training/testing and preprocessing
3. Linear Regression (salary prediction)
4. Logistic Regression (binary classification)
5. Sigmoid, log loss, cost function and Gradient Descent
6. L1 (Lasso), L2 (Ridge) and Elastic Net regularization
7. Evaluation: MSE, R², accuracy and confusion matrix
8. Python libraries used in the practical work
9. Guided practical demos
10. Glossary, common TP questions and mini quiz

INSTALLATION
------------
Open a terminal / CMD and run:
    python -m pip install numpy pandas matplotlib seaborn scikit-learn

OPTIONAL DATA
-------------
For the salary demo, place salary_data.csv in the same folder as this file.
It should contain columns named:
    YearsExperience, Salary

The heart-disease demo tries the same OpenML dataset as the supplied practical.
It needs an internet connection the first time. If it cannot be downloaded,
the script uses scikit-learn's breast-cancer dataset as an explicitly labelled
educational fallback. This fallback is NOT the same dataset as the TP dataset.

RUN
---
    python machine_learning_handbook.py

Arabic note:
هذا الملف دليل تعليمي وتطبيقي. اقرأ الشرح ثم شغّل الأمثلة من القائمة.
"""

from __future__ import annotations

import math
import textwrap
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    plt = None
    sns = None

try:
    from sklearn import datasets
    from sklearn.datasets import fetch_openml
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
    from sklearn.metrics import (
        accuracy_score, confusion_matrix, mean_squared_error,
        r2_score, classification_report
    )
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import MinMaxScaler
except ImportError as exc:
    raise SystemExit(
        "Missing scikit-learn. Install dependencies with:\n"
        "python -m pip install numpy pandas matplotlib seaborn scikit-learn"
    ) from exc


BASE_DIR = Path(__file__).resolve().parent
EPSILON = 1e-8


# ---------------------------------------------------------------------------
# 0. DISPLAY HELPERS / أدوات العرض
# ---------------------------------------------------------------------------

def title(text: str) -> None:
    print("\n" + "=" * 78)
    print(text)
    print("=" * 78)


def pause() -> None:
    input("\nPress Enter to return to the menu... / اضغط Enter للعودة إلى القائمة...")


def explain(english: str, arabic: str) -> None:
    print("\nENGLISH:")
    print(textwrap.fill(english, width=76))
    print("\nالعربية:")
    print(arabic)


def show_formula(name: str, formula: str, meaning: str) -> None:
    print(f"\n{name}\n  {formula}\n  {meaning}")


# ---------------------------------------------------------------------------
# 1. CORE CONCEPTS / المفاهيم الأساسية
# ---------------------------------------------------------------------------

def lesson_ai_ml() -> None:
    title("1. ARTIFICIAL INTELLIGENCE & MACHINE LEARNING")
    explain(
        "Artificial Intelligence (AI) is the broad field of building systems "
        "that perform tasks associated with human intelligence. Machine "
        "Learning (ML) is a branch of AI in which algorithms learn patterns "
        "from data and use those patterns to make predictions or decisions.",
        "الذكاء الاصطناعي هو المجال الواسع الذي يهتم ببناء أنظمة تنفذ مهام "
        "مرتبطة عادةً بالذكاء البشري. التعلم الآلي فرع من الذكاء الاصطناعي، "
        "تتعلم فيه الخوارزميات الأنماط من البيانات ثم تستعملها للتنبؤ أو اتخاذ القرار."
    )
    print("\nExamples / أمثلة:")
    print("  AI: voice assistants, image recognition, language tools.")
    print("  ML: salary prediction, spam detection, disease classification.")
    print("\nRelationship / العلاقة:")
    print("  Artificial Intelligence")
    print("       └── Machine Learning")
    print("              └── Deep Learning (a specialized ML approach)")
    print("\nImportant: this TP mainly studies supervised learning, not deep learning.")


def lesson_ml_types() -> None:
    title("2. TYPES OF MACHINE LEARNING / أنواع التعلم الآلي")
    explain(
        "Supervised learning uses labelled examples: each training example "
        "has an input and a known target. Unsupervised learning receives data "
        "without target labels and searches for structure, such as clusters. "
        "Reinforcement learning trains an agent through actions, feedback and rewards.",
        "التعلم الخاضع للإشراف يستعمل أمثلة لها مدخلات وإجابات معروفة. "
        "التعلم غير الخاضع للإشراف يستعمل بيانات بلا إجابات جاهزة ويبحث عن "
        "مجموعات وأنماط. التعلم بالتعزيز يدرّب وكيلاً عن طريق الأفعال والتغذية "
        "الراجعة والمكافآت."
    )
    print("\nThis practical / هذا العمل التطبيقي:")
    print("  Linear Regression  -> supervised learning, regression.")
    print("  Logistic Regression -> supervised learning, classification.")


def lesson_vocabulary() -> None:
    title("3. DATASET VOCABULARY / مصطلحات البيانات")
    rows = [
        ("Dataset", "A collection of examples", "مجموعة البيانات"),
        ("Sample / observation", "One row or example", "عينة أو ملاحظة"),
        ("Feature (X)", "Input variable used by a model", "خاصية أو متغير مدخل"),
        ("Label / target (y)", "Value the model must predict", "التسمية أو القيمة الهدف"),
        ("Model", "Learned mathematical relationship", "النموذج"),
        ("Training", "Learning model parameters from data", "التدريب"),
        ("Testing", "Evaluating on held-out data", "الاختبار"),
        ("Prediction", "Model output for new inputs", "التنبؤ"),
        ("Parameter", "Learned value, e.g. weight or bias", "معامل يتعلمه النموذج"),
        ("Hyperparameter", "Setting chosen before/during training", "معامل ضبط يحدده المستخدم"),
    ]
    print(f"{'TERM':<24} {'ENGLISH':<43} ARABIC")
    print("-" * 100)
    for term, meaning, arabic in rows:
        print(f"{term:<24} {meaning:<43} {arabic}")


def lesson_train_test() -> None:
    title("4. TRAINING / TESTING SPLIT & DATA PREPROCESSING")
    explain(
        "Training data teaches the model. Test data is kept separate and "
        "estimates performance on unseen examples. The supplied practical "
        "uses test_size=0.3, meaning 70% training and 30% testing.",
        "بيانات التدريب تُستخدم لتعليم النموذج. أما بيانات الاختبار فتُترك "
        "جانبا لتقييمه على أمثلة لم يتدرب عليها. يستعمل العمل التطبيقي "
        "test_size=0.3 أي 70% للتدريب و30% للاختبار."
    )
    print("\nExample:")
    print("  X_train, X_test, y_train, y_test = train_test_split(")
    print("      X, y, test_size=0.3, random_state=42")
    print("  )")
    print("\nPreprocessing / معالجة البيانات:")
    print("  - Check missing values (NaN). / افحص القيم المفقودة.")
    print("  - Convert data to numeric form when needed. / حوّل البيانات إلى أرقام عند الحاجة.")
    print("  - Scale features when useful. / وحّد مقاييس الخصائص عند الحاجة.")
    print("  - Fit preprocessing on training data only, then transform test data.")
    print("    نلائم المعالجة على بيانات التدريب فقط ثم نطبقها على الاختبار.")
    print("\nMinMaxScaler formula:")
    print("  X_scaled = (X - X_min) / (X_max - X_min)")
    print("  It maps training feature values approximately into [0, 1].")


# ---------------------------------------------------------------------------
# 2. MATHEMATICS / الرياضيات
# ---------------------------------------------------------------------------

def sigmoid(z):
    """Numerically safer sigmoid; maps real values to probabilities (0, 1)."""
    z = np.asarray(z, dtype=float)
    # Avoid overflow for very large magnitudes.
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def lesson_sigmoid() -> None:
    title("5. SIGMOID FUNCTION / دالة سيغمويد")
    explain(
        "Sigmoid converts any real number into a value between 0 and 1. "
        "In binary Logistic Regression, this value is interpreted as the "
        "model's estimated probability for class 1.",
        "دالة سيغمويد تحول أي عدد حقيقي إلى قيمة بين 0 و1. في الانحدار "
        "اللوجستي الثنائي، تُفسر هذه القيمة على أنها الاحتمال المقدّر للفئة 1."
    )
    show_formula("Formula / الصيغة", "sigmoid(z) = 1 / (1 + exp(-z))",
                 "z = Xw + b")
    print("\nExamples:")
    for z in [-4, -1, 0, 1, 4]:
        print(f"  sigmoid({z:>2}) = {sigmoid(z):.4f}")
    print("\nThreshold used in this TP:")
    print("  probability >= 0.5 -> class 1")
    print("  probability <  0.5 -> class 0")
    print("  الاحتمال الأكبر أو المساوي لـ 0.5 يصنف إلى الفئة 1.")


def lesson_cost() -> None:
    title("6. COST FUNCTION / دالة التكلفة")
    explain(
        "A cost (loss) function measures how far predictions are from the "
        "correct answers. Training attempts to find parameters that make "
        "the cost small. Linear Regression commonly uses Mean Squared Error; "
        "the Logistic Regression code in the supplied TP uses binary log loss.",
        "دالة التكلفة تقيس مدى ابتعاد توقعات النموذج عن الإجابات الصحيحة. "
        "يحاول التدريب إيجاد معاملات تجعل التكلفة صغيرة. الانحدار الخطي "
        "يستعمل غالباً متوسط مربع الخطأ، أما كود الانحدار اللوجستي في هذا "
        "العمل فيستعمل الخسارة اللوغاريتمية الثنائية."
    )
    show_formula("MSE", "MSE = (1/m) * sum((y - y_pred)^2)",
                 "Average squared prediction error / متوسط مربعات أخطاء التنبؤ.")
    show_formula(
        "Binary Log Loss",
        "J = -(1/m) * sum[y log(p) + (1-y) log(1-p)]",
        "Penalizes confident wrong probability predictions / تعاقب التوقعات الاحتمالية الخاطئة الواثقة."
    )
    print("\nLower cost is generally better on the same evaluation data.")
    print("انخفاض التكلفة أفضل عادةً عند التقييم على نفس البيانات.")


def lesson_gradient_descent() -> None:
    title("7. GRADIENT DESCENT / الانحدار المتدرج")
    explain(
        "Gradient Descent is an optimization method. It repeatedly updates "
        "weights and bias in the direction that reduces the cost. The learning "
        "rate alpha controls the size of each update.",
        "الانحدار المتدرج طريقة للتحسين. يحدّث الأوزان والانحياز مراراً "
        "في الاتجاه الذي يقلل دالة التكلفة. معدل التعلم alpha يحدد حجم كل تحديث."
    )
    show_formula("Update rule / قاعدة التحديث",
                 "w := w - alpha * dJ/dw",
                 "b := b - alpha * dJ/db")
    print("\nLearning rate / معدل التعلم:")
    print("  Too small: training can be very slow. / صغير جدا: التدريب بطيء.")
    print("  Too large: updates may overshoot or diverge. / كبير جدا: قد يتجاوز الحل.")
    print("  Suitable: cost often decreases steadily. / مناسب: تنخفض التكلفة غالبا.")
    print("\nIn the supplied code: alpha is the learning rate and num_iters is")
    print("the number of update steps. / num_iters هو عدد خطوات التحديث.")


# ---------------------------------------------------------------------------
# 3. MANUAL LOGISTIC REGRESSION / الانحدار اللوجستي اليدوي
# ---------------------------------------------------------------------------

def initialize_parameters(n_features: int):
    """Start all weights at zero and bias at zero."""
    return np.zeros((n_features, 1)), 0.0


def logistic_cost_gradients(X, y, w, b, lambda_=0.0, penalty="none", rho=0.5):
    """
    Binary cross-entropy plus optional regularization.
    X: (m, n), y: (m, 1), w: (n, 1)
    """
    m = X.shape[0]
    y = y.reshape(-1, 1)
    z = X @ w + b
    p = sigmoid(z)
    cost = -(1 / m) * np.sum(
        y * np.log(p + EPSILON) + (1 - y) * np.log(1 - p + EPSILON)
    )
    dw = (X.T @ (p - y)) / m
    db = float(np.sum(p - y) / m)

    if penalty == "l2":
        cost += (lambda_ / (2 * m)) * np.sum(w ** 2)
        dw += (lambda_ / m) * w
    elif penalty == "l1":
        cost += (lambda_ / m) * np.sum(np.abs(w))
        dw += (lambda_ / m) * np.sign(w)
    elif penalty == "elasticnet":
        cost += (lambda_ * rho / m) * np.sum(np.abs(w))
        cost += (lambda_ * (1 - rho) / (2 * m)) * np.sum(w ** 2)
        dw += (lambda_ * rho / m) * np.sign(w)
        dw += (lambda_ * (1 - rho) / m) * w
    elif penalty != "none":
        raise ValueError("penalty must be none, l1, l2 or elasticnet")

    return float(cost), dw, db


def train_manual_logistic(X, y, alpha=0.1, iterations=1000,
                          lambda_=0.0, penalty="none", rho=0.5):
    """Train logistic regression using Gradient Descent."""
    w, b = initialize_parameters(X.shape[1])
    costs = []
    for step in range(iterations):
        cost, dw, db = logistic_cost_gradients(
            X, y, w, b, lambda_=lambda_, penalty=penalty, rho=rho
        )
        w -= alpha * dw
        b -= alpha * db
        costs.append(cost)
    return w, b, costs


def manual_predict(X, w, b, threshold=0.5):
    probabilities = sigmoid(X @ w + b)
    return (probabilities >= threshold).astype(int).ravel()


def lesson_logistic_code() -> None:
    title("8. HOW MANUAL LOGISTIC REGRESSION WORKS")
    explain(
        "The implementation first calculates z = Xw + b, applies sigmoid "
        "to get probabilities, calculates log loss and gradients, then updates "
        "w and b. Repeating this process trains the classifier.",
        "يحسب التطبيق أولا z = Xw + b، ثم يطبق سيغمويد للحصول على الاحتمالات، "
        "ويحسب الخسارة والمشتقات، ثم يحدث w و b. تكرار العملية يدرب المصنف."
    )
    print("\nMain steps / الخطوات:")
    print("  1. Initialize w and b. / تهيئة الأوزان والانحياز.")
    print("  2. Calculate z = X @ w + b. / حساب القيمة الخطية.")
    print("  3. Calculate p = sigmoid(z). / حساب الاحتمال.")
    print("  4. Calculate log loss and gradients. / حساب الخسارة والمشتقات.")
    print("  5. Update w and b. / تحديث الأوزان والانحياز.")
    print("  6. Repeat for many iterations. / تكرار العملية.")
    print("\nThe @ symbol performs matrix multiplication in NumPy.")
    print("الرمز @ ينفذ ضرب المصفوفات في NumPy.")


# ---------------------------------------------------------------------------
# 4. REGULARIZATION / التنظيم
# ---------------------------------------------------------------------------

def lesson_regularization() -> None:
    title("9. OVERFITTING & REGULARIZATION / فرط التعلم والتنظيم")
    explain(
        "Overfitting happens when a model fits training examples too closely "
        "(including noise) and generalizes poorly to new examples. "
        "Regularization adds a penalty for large or complex weights to help "
        "control model complexity.",
        "يحدث فرط التعلم عندما يلائم النموذج بيانات التدريب بشكل مفرط، حتى "
        "الضوضاء، فيصبح أداؤه ضعيفا على بيانات جديدة. يضيف التنظيم عقوبة "
        "للأوزان الكبيرة أو تعقيد النموذج للحد من هذه المشكلة."
    )
    print("\nL1 / Lasso:")
    print("  Penalty: lambda * sum(abs(w))")
    print("  Can push some coefficients exactly to zero.")
    print("  قد يجعل بعض المعاملات تساوي صفرا، ويساعد في اختيار الخصائص.")
    print("\nL2 / Ridge:")
    print("  Penalty: (lambda / 2) * sum(w ** 2)")
    print("  Shrinks weights, usually without making them exactly zero.")
    print("  يقلص الأوزان عادة دون جعلها صفرا تماما.")
    print("\nElastic Net:")
    print("  Combines L1 and L2 penalties.")
    print("  يجمع بين عقوبتي L1 وL2.")
    print("\nHyperparameters:")
    print("  lambda (or alpha in sklearn estimators) controls regularization strength.")
    print("  rho / l1_ratio controls the L1-L2 mixture in Elastic Net.")
    print("\nNote: in scikit-learn Ridge/Lasso/ElasticNet, alpha is the regularization")
    print("strength, not the Gradient Descent learning rate.")


# ---------------------------------------------------------------------------
# 5. EVALUATION / التقييم
# ---------------------------------------------------------------------------

def lesson_metrics() -> None:
    title("10. MODEL EVALUATION / تقييم النموذج")
    explain(
        "Metrics summarize model performance. Choose metrics that match the "
        "task. Regression predicts numbers; classification predicts classes. "
        "Accuracy alone can be misleading when classes are imbalanced.",
        "مقاييس التقييم تلخص أداء النموذج. اختر المقياس المناسب للمهمة. "
        "الانحدار يتنبأ بأرقام، والتصنيف يتنبأ بفئات. قد تكون الدقة وحدها "
        "مضللة عندما تكون الفئات غير متوازنة."
    )
    print("\nREGRESSION:")
    print("  MSE = average squared difference between actual and predicted values.")
    print("  R² = proportion of target variance explained by the model.")
    print("  R² can be negative on test data if the model performs very poorly.")
    print("\nCLASSIFICATION:")
    print("  Accuracy = correct predictions / all predictions.")
    print("  Confusion matrix for binary classes, with sklearn labels [0, 1]:")
    print("                 Predicted 0   Predicted 1")
    print("    Actual 0         TN            FP")
    print("    Actual 1         FN            TP")
    print("  TN = true negative; FP = false positive;")
    print("  FN = false negative; TP = true positive.")
    print("\nIn medical screening, false negatives can be especially important.")
    print("في الفحص الطبي، قد تكون الحالات السلبية الكاذبة خطيرة بشكل خاص.")


# ---------------------------------------------------------------------------
# 6. LIBRARIES / المكتبات
# ---------------------------------------------------------------------------

def lesson_libraries() -> None:
    title("11. PYTHON LIBRARIES / مكتبات بايثون")
    items = [
        ("NumPy (np)", "Arrays, matrices and numerical calculations", "المصفوفات والحسابات العددية"),
        ("Pandas (pd)", "Read CSV files and manipulate tables", "قراءة CSV ومعالجة الجداول"),
        ("Matplotlib (plt)", "Create plots and charts", "إنشاء الرسوم البيانية"),
        ("Seaborn (sns)", "Statistical visualizations", "رسوم إحصائية"),
        ("Scikit-learn (sklearn)", "Models, preprocessing, splitting and metrics", "النماذج والمعالجة والتقييم"),
        ("Pathlib", "Work with file paths", "التعامل مع مسارات الملفات"),
    ]
    for name, en, ar in items:
        print(f"\n{name}\n  EN: {en}\n  AR: {ar}")


# ---------------------------------------------------------------------------
# 7. PRACTICAL DEMO A: LINEAR REGRESSION / الانحدار الخطي
# ---------------------------------------------------------------------------

def load_salary_data():
    csv_path = BASE_DIR / "salary_data.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        required = {"YearsExperience", "Salary"}
        if not required.issubset(df.columns):
            raise ValueError(
                "salary_data.csv must contain YearsExperience and Salary columns."
            )
        print(f"Loaded real TP file: {csv_path}")
        return df, True

    print("salary_data.csv was not found.")
    print("Using a small synthetic teaching dataset instead (not official TP data).")
    rng = np.random.default_rng(42)
    years = np.array([1.1, 1.3, 1.5, 2.0, 2.2, 2.9, 3.0, 3.2, 3.7,
                      4.0, 4.5, 5.0, 5.2, 5.9, 6.0, 6.8, 7.1, 7.9,
                      8.2, 9.0, 9.5, 10.0]).reshape(-1, 1)
    salary = 25000 + 8500 * years.ravel() + rng.normal(0, 3500, len(years))
    return pd.DataFrame({"YearsExperience": years.ravel(), "Salary": salary}), False


def linear_regression_demo() -> None:
    title("PRACTICAL A — LINEAR REGRESSION: SALARY PREDICTION")
    explain(
        "Goal: learn a relationship between years of experience (input X) "
        "and salary (target y), then predict salary for unseen experience values.",
        "الهدف: تعلم العلاقة بين سنوات الخبرة (المدخل X) والراتب (القيمة الهدف y)، "
        "ثم توقع راتب لقيم خبرة جديدة."
    )
    df, official_data = load_salary_data()
    print("\nFirst rows:")
    print(df.head().to_string(index=False))
    print("\nDescriptive statistics:")
    print(df.describe().to_string())

    X = df[["YearsExperience"]].to_numpy()
    y = df["Salary"].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("\nLearned model / النموذج المتعلم:")
    print(f"  Intercept (b): {model.intercept_:.3f}")
    print(f"  Slope (w):     {model.coef_[0]:.3f}")
    print(f"  Formula: salary = {model.coef_[0]:.3f} * years + {model.intercept_:.3f}")
    print(f"\nTest MSE: {mse:.2f}")
    print(f"Test R²:  {r2:.4f}")
    print("\nActual vs predicted test values:")
    for actual, pred in zip(y_test, predictions):
        print(f"  actual={actual:10.2f} | predicted={pred:10.2f}")

    try:
        years = float(input("\nEnter years of experience to predict salary: "))
        print(f"Predicted salary: {model.predict(np.array([[years]]))[0]:.2f}")
    except ValueError:
        print("No valid number entered; skipping custom prediction.")

    print("\nRegularized regression comparison:")
    print("Note: sklearn alpha below is regularization strength.")
    rows = []
    for alpha in [0.1, 1.0, 10.0]:
        estimators = [
            ("Ridge", Ridge(alpha=alpha)),
            ("Lasso", Lasso(alpha=alpha, max_iter=10000)),
            ("ElasticNet", ElasticNet(alpha=alpha, l1_ratio=0.5, max_iter=10000)),
        ]
        for name, estimator in estimators:
            estimator.fit(X_train, y_train)
            pred = estimator.predict(X_test)
            rows.append({
                "Model": name,
                "alpha": alpha,
                "MSE": mean_squared_error(y_test, pred),
                "R2": r2_score(y_test, pred),
                "Coefficient": estimator.coef_[0],
            })
    print(pd.DataFrame(rows).to_string(index=False))

    if plt is not None:
        show = input("\nShow graphs? (y/n): ").strip().lower()
        if show == "y":
            plt.figure(figsize=(8, 5))
            if sns is not None:
                sns.scatterplot(data=df, x="YearsExperience", y="Salary")
            else:
                plt.scatter(X.ravel(), y)
            x_line = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
            plt.plot(x_line, model.predict(x_line), label="Linear Regression")
            plt.xlabel("Years of Experience")
            plt.ylabel("Salary")
            plt.title("Salary vs Experience — Linear Regression")
            plt.legend()
            plt.tight_layout()
            plt.show()

    if not official_data:
        print("\nReminder: this run used generated teaching data, not salary_data.csv.")


# ---------------------------------------------------------------------------
# 8. PRACTICAL DEMO B: LOGISTIC REGRESSION / الانحدار اللوجستي
# ---------------------------------------------------------------------------

def load_heart_dataset():
    """Try the OpenML dataset used in the supplied TP; fallback is clearly labelled."""
    print("Trying to download OpenML heart-disease dataset (internet required)...")
    try:
        data = fetch_openml(name="heart-disease", version=1, as_frame=True)
        df = data.frame.copy()
        source = "OpenML heart-disease dataset (same dataset source as supplied TP)"
        if "target" not in df.columns:
            raise ValueError("OpenML data did not contain the expected target column.")
        return df, source
    except Exception as exc:
        warnings.warn(f"Could not load OpenML heart-disease dataset: {exc}")
        print("\nOpenML dataset unavailable. Using sklearn breast-cancer dataset.")
        print("IMPORTANT: this is only a fallback teaching dataset, not the TP heart dataset.")
        bunch = datasets.load_breast_cancer(as_frame=True)
        df = bunch.frame.copy()
        df = df.rename(columns={"target": "target"})
        return df, "Scikit-learn breast-cancer fallback (NOT the TP heart dataset)"


def prepare_binary_dataset(df: pd.DataFrame):
    """Clean basic tabular data, encode categories and split before scaling."""
    df = df.copy()
    df = df.dropna().reset_index(drop=True)

    y = df["target"]
    # Convert target to numeric binary labels when possible.
    if not pd.api.types.is_numeric_dtype(y):
        y = pd.Series(pd.factorize(y)[0], index=y.index)
    y = y.astype(int)

    X = df.drop(columns=["target"])
    # One-hot encode any categorical columns.
    X = pd.get_dummies(X, drop_first=True)
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="all")
    # Ensure all columns are numeric and remove any remaining problematic rows.
    X = X.apply(pd.to_numeric, errors="coerce")
    valid = X.notna().all(axis=1) & y.notna()
    X = X.loc[valid]
    y = y.loc[valid]

    # Remove constant columns (they contain no useful variation).
    X = X.loc[:, X.nunique(dropna=True) > 1]
    if y.nunique() != 2:
        raise ValueError(
            f"Expected a binary target, but found {y.nunique()} target classes."
        )
    return X.to_numpy(dtype=float), y.to_numpy(dtype=int), list(X.columns)


def logistic_regression_demo() -> None:
    title("PRACTICAL B — LOGISTIC REGRESSION: BINARY CLASSIFICATION")
    explain(
        "Goal: use patient measurements as features to classify a target into "
        "two classes. This is an educational demonstration, not a medical tool.",
        "الهدف: استعمال قياسات المرضى كخصائص لتصنيف الهدف إلى فئتين. "
        "هذا مثال تعليمي وليس أداة للتشخيص الطبي."
    )
    df, source = load_heart_dataset()
    print(f"\nDataset source: {source}")
    print("\nFirst rows:")
    print(df.head().to_string(index=False))
    print("\nMissing values (first columns):")
    print(df.isnull().sum().head(15).to_string())

    X, y, feature_names = prepare_binary_dataset(df)
    print(f"\nSamples: {len(y)} | Features: {X.shape[1]}")
    print("Target class counts:")
    print(pd.Series(y).value_counts().sort_index().to_string())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Important: fit scaler ONLY on training data to avoid data leakage.
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    y_train_col = y_train.reshape(-1, 1)
    print("\nTraining manual Logistic Regression with Gradient Descent...")
    w, b, costs = train_manual_logistic(
        X_train_scaled, y_train_col, alpha=0.1, iterations=1000
    )
    y_pred = manual_predict(X_test_scaled, w, b)
    print(f"Manual Logistic Regression accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("Confusion matrix [ [TN, FP], [FN, TP] ] for labels [0, 1]:")
    print(confusion_matrix(y_test, y_pred, labels=[0, 1]))
    print("\nClassification report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\nCompare regularization techniques using manual Gradient Descent:")
    configs = [
        ("No regularization", "none", 0.0),
        ("L2", "l2", 1.0),
        ("L1", "l1", 0.1),
        ("Elastic Net", "elasticnet", 0.1),
    ]
    results = []
    for name, penalty, strength in configs:
        w_reg, b_reg, reg_costs = train_manual_logistic(
            X_train_scaled, y_train_col,
            alpha=0.1, iterations=1000,
            lambda_=strength, penalty=penalty, rho=0.5
        )
        pred = manual_predict(X_test_scaled, w_reg, b_reg)
        results.append({
            "Method": name,
            "Accuracy": accuracy_score(y_test, pred),
            "Final training cost": reg_costs[-1],
        })
    print(pd.DataFrame(results).to_string(index=False))

    print("\nScikit-learn LogisticRegression reference model:")
    # C is inverse regularization strength in sklearn LogisticRegression.
    sklearn_model = LogisticRegression(max_iter=3000, C=1.0)
    sklearn_model.fit(X_train_scaled, y_train)
    sklearn_pred = sklearn_model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, sklearn_pred):.4f}")
    print("Confusion matrix:")
    print(confusion_matrix(y_test, sklearn_pred, labels=[0, 1]))

    if plt is not None:
        show = input("\nShow training cost graph? (y/n): ").strip().lower()
        if show == "y":
            plt.figure(figsize=(8, 5))
            plt.plot(costs)
            plt.xlabel("Iteration")
            plt.ylabel("Log Loss")
            plt.title("Manual Logistic Regression — Cost over iterations")
            plt.tight_layout()
            plt.show()

    print("\nMedical caution: predictions are not diagnoses. Do not use this demo")
    print("to make real healthcare decisions.")


# ---------------------------------------------------------------------------
# 9. GLOSSARY / قاموس المصطلحات
# ---------------------------------------------------------------------------

GLOSSARY = {
    "artificial intelligence": ("AI: systems performing tasks associated with intelligence.",
                                "الذكاء الاصطناعي: أنظمة تنفذ مهام مرتبطة بالذكاء."),
    "machine learning": ("A branch of AI that learns patterns from data.",
                         "فرع من الذكاء الاصطناعي يتعلم الأنماط من البيانات."),
    "supervised learning": ("Learning from labelled examples.",
                            "التعلم من أمثلة لها إجابات معروفة."),
    "unsupervised learning": ("Finding structure in data without labels.",
                              "اكتشاف بنية البيانات دون تسميات."),
    "reinforcement learning": ("Learning through actions and rewards.",
                               "التعلم عبر الأفعال والمكافآت."),
    "linear regression": ("Predicts continuous numerical values.",
                          "يتنبأ بقيم رقمية مستمرة."),
    "logistic regression": ("A classification model that estimates probabilities.",
                            "نموذج تصنيف يقدر الاحتمالات."),
    "sigmoid": ("Maps a real number to a value between 0 and 1.",
                "تحول العدد إلى قيمة بين 0 و1."),
    "gradient descent": ("Optimization method that updates parameters to reduce cost.",
                         "طريقة تحسين تحدث المعاملات لتقليل التكلفة."),
    "cost function": ("Measures model prediction error.",
                      "تقيس خطأ توقعات النموذج."),
    "overfitting": ("Fitting training data too closely and generalizing poorly.",
                    "ملاءمة مفرطة لبيانات التدريب وضعف التعميم."),
    "regularization": ("Penalty that helps control model complexity.",
                       "عقوبة تساعد على التحكم في تعقيد النموذج."),
    "lasso": ("L1 regularization; can set coefficients to zero.",
              "تنظيم L1 ويمكنه جعل بعض المعاملات صفرا."),
    "ridge": ("L2 regularization; shrinks coefficients.",
              "تنظيم L2 ويقلص المعاملات."),
    "elastic net": ("Combines L1 and L2.",
                    "يجمع بين L1 وL2."),
    "accuracy": ("Fraction of predictions that are correct.",
                 "نسبة التوقعات الصحيحة."),
    "confusion matrix": ("Table of correct and incorrect classification counts.",
                         "جدول لعدد التصنيفات الصحيحة والخاطئة."),
    "normalization": ("Rescaling feature values to a common range.",
                      "إعادة تحجيم قيم الخصائص إلى مجال مشترك."),
    "feature": ("An input variable used by the model.",
                "متغير مدخل يستعمله النموذج."),
    "target": ("The value the model tries to predict.",
               "القيمة التي يحاول النموذج توقعها."),
}


def glossary_search() -> None:
    title("12. SEARCH THE GLOSSARY / ابحث في قاموس المصطلحات")
    print("Type a term such as sigmoid, overfitting, feature, L1, accuracy.")
    print("اكتب مصطلحا مثل sigmoid أو overfitting أو feature.")
    query = input("\nSearch term: ").strip().lower()
    if not query:
        return
    matches = [(k, v) for k, v in GLOSSARY.items() if query in k]
    if not matches:
        print("No exact glossary match. Available terms:")
        print(", ".join(GLOSSARY.keys()))
        return
    for term, (en, ar) in matches:
        print(f"\n{term.upper()}\n  EN: {en}\n  AR: {ar}")


# ---------------------------------------------------------------------------
# 10. TP QUESTIONS / أسئلة محتملة في العمل التطبيقي
# ---------------------------------------------------------------------------

TP_QUESTIONS = [
    ("What is the difference between regression and classification?",
     "Regression predicts numerical values; classification predicts categories.",
     "الانحدار يتنبأ بقيم رقمية، والتصنيف يتنبأ بفئات."),
    ("Why do we split data into training and testing sets?",
     "To train on one part and evaluate generalization on unseen data.",
     "للتدريب على جزء وتقييم قدرة النموذج على التعميم على بيانات جديدة."),
    ("What does fit() do?",
     "It trains/estimates the model parameters from the supplied training data.",
     "تدرب النموذج وتقدر معاملاته باستعمال بيانات التدريب."),
    ("What does predict() do?",
     "It produces predictions for supplied input examples.",
     "تنتج توقعات للبيانات المدخلة."),
    ("Why does Logistic Regression use sigmoid?",
     "To map the linear score to a probability between 0 and 1.",
     "لتحويل النتيجة الخطية إلى احتمال بين 0 و1."),
    ("What is the role of the learning rate?",
     "It controls the size of each Gradient Descent update.",
     "تحدد حجم كل تحديث في الانحدار المتدرج."),
    ("What is the difference between L1 and L2?",
     "L1 penalizes absolute weights; L2 penalizes squared weights.",
     "L1 يعاقب القيم المطلقة للأوزان، وL2 يعاقب مربعاتها."),
    ("What is Elastic Net?",
     "A combination of L1 and L2 regularization.",
     "مزيج من تنظيمي L1 وL2."),
    ("What does accuracy measure?",
     "The fraction of predictions that are correct.",
     "نسبة التوقعات الصحيحة من مجموع التوقعات."),
    ("What does a confusion matrix show?",
     "Counts of true/false positives and negatives for classification.",
     "أعداد الإيجابيات والسلبيات الصحيحة والخاطئة في التصنيف."),
    ("Why scale features?",
     "Features on very different scales can make optimization harder.",
     "اختلاف مقاييس الخصائص كثيرا قد يجعل التحسين أصعب."),
    ("What is overfitting?",
     "When a model fits training data too closely and performs poorly on new data.",
     "عندما يحفظ النموذج بيانات التدريب بشكل مفرط ويفشل مع بيانات جديدة."),
]


def tp_questions() -> None:
    title("13. COMMON TP QUESTIONS & ANSWERS / أسئلة وأجوبة")
    for i, (question, answer, arabic) in enumerate(TP_QUESTIONS, 1):
        print(f"\nQ{i}. {question}")
        print(f"  EN: {answer}")
        print(f"  AR: {arabic}")


# ---------------------------------------------------------------------------
# 11. QUIZ / اختبار
# ---------------------------------------------------------------------------

QUIZ = [
    ("Which algorithm predicts a salary?",
     ["Logistic Regression", "Linear Regression", "K-Means"], 1,
     "Linear Regression predicts continuous numerical values."),
    ("Which algorithm is mainly used for classification?",
     ["Logistic Regression", "Linear Regression", "Pandas"], 0,
     "Logistic Regression is used for classification."),
    ("What range does sigmoid output?",
     ["0 to 1", "-infinity to infinity", "0 to 1000"], 0,
     "Sigmoid output is between 0 and 1."),
    ("What does Gradient Descent try to minimize?",
     ["Number of rows", "Cost function", "Feature names"], 1,
     "Gradient Descent updates parameters to reduce cost."),
    ("Which regularization can set coefficients to zero?",
     ["L1", "L2 only", "Neither"], 0,
     "L1 can make some coefficients exactly zero."),
    ("What does test_size=0.3 mean?",
     ["30% training, 70% testing", "70% training, 30% testing", "30 rows"], 1,
     "0.3 means 30% of the data is held out for testing."),
]


def run_quiz() -> None:
    title("14. MINI QUIZ / اختبار قصير")
    score = 0
    for i, (question, options, correct, explanation) in enumerate(QUIZ, 1):
        print(f"\n{i}. {question}")
        for j, option in enumerate(options, 1):
            print(f"   {j}. {option}")
        try:
            answer = int(input("Your answer (1, 2 or 3): ").strip()) - 1
        except ValueError:
            answer = -1
        if answer == correct:
            print("Correct! / صحيح!")
            score += 1
        else:
            print(f"Not quite. Correct answer: {options[correct]}")
        print("Explanation:", explanation)
    print(f"\nFINAL SCORE: {score}/{len(QUIZ)}")
    print("راجع الدروس التي أخطأت فيها ثم أعد الاختبار.")


# ---------------------------------------------------------------------------
# 12. QUICK REFERENCE / ملخص سريع
# ---------------------------------------------------------------------------

def quick_reference() -> None:
    title("15. QUICK REVISION SHEET / ورقة مراجعة سريعة")
    print("""
LINEAR REGRESSION
  Task: predict a continuous number / توقع رقم مستمر
  Formula: y_hat = w*x + b
  Example: salary prediction / توقع الراتب
  Common metric: MSE, R²

LOGISTIC REGRESSION
  Task: classification / التصنيف
  z = Xw + b
  sigmoid(z) = 1 / (1 + exp(-z))
  probability >= 0.5 -> class 1; otherwise class 0
  Loss: binary cross-entropy / الخسارة اللوغاريتمية الثنائية

GRADIENT DESCENT
  w := w - alpha * dw
  b := b - alpha * db
  alpha = learning rate / معدل التعلم
  iterations = number of updates / عدد التحديثات

REGULARIZATION
  L1 / Lasso: sum(abs(w)) — may set weights to zero
  L2 / Ridge: sum(w**2) — shrinks weights
  Elastic Net: combines L1 and L2

DATA
  X = features / الخصائص
  y = target / القيمة الهدف
  train = learn / تدريب
  test = evaluate / اختبار
  fit = train / درّب
  predict = make predictions / تنبأ
  MinMaxScaler = scale features / وحّد مقاييس الخصائص

IMPORTANT DIFFERENCE
  alpha in Gradient Descent = learning rate.
  alpha in sklearn Ridge/Lasso/ElasticNet = regularization strength.
  They are different meanings in different functions.
""")


# ---------------------------------------------------------------------------
# MAIN MENU / القائمة الرئيسية
# ---------------------------------------------------------------------------

MENU = {
    "1": ("AI & Machine Learning basics", lesson_ai_ml),
    "2": ("Types of Machine Learning", lesson_ml_types),
    "3": ("Dataset vocabulary", lesson_vocabulary),
    "4": ("Training, testing & preprocessing", lesson_train_test),
    "5": ("Sigmoid function", lesson_sigmoid),
    "6": ("Cost function", lesson_cost),
    "7": ("Gradient Descent", lesson_gradient_descent),
    "8": ("Manual Logistic Regression code", lesson_logistic_code),
    "9": ("Overfitting & Regularization (L1/L2/Elastic Net)", lesson_regularization),
    "10": ("Evaluation metrics", lesson_metrics),
    "11": ("Python libraries", lesson_libraries),
    "12": ("Run Linear Regression salary practical", linear_regression_demo),
    "13": ("Run Logistic Regression classification practical", logistic_regression_demo),
    "14": ("Search glossary", glossary_search),
    "15": ("Common TP questions and answers", tp_questions),
    "16": ("Mini quiz", run_quiz),
    "17": ("Quick revision sheet", quick_reference),
}


def main() -> None:
    title("MACHINE LEARNING — COMPLETE STUDY & TP HANDBOOK")
    print("English + العربية | Based on your supplied tp1.py")
    print("Choose a topic. You can return here whenever you need help.")
    while True:
        print("\n" + "-" * 78)
        for key, (label, _) in MENU.items():
            print(f"{key:>2}. {label}")
        print(" 0. Exit / خروج")
        choice = input("\nChoose (0-17): ").strip()
        if choice == "0":
            print("\nGood luck in your TP! بالتوفيق في العمل التطبيقي!")
            break
        item = MENU.get(choice)
        if item is None:
            print("Invalid choice. Please choose a number from 0 to 17.")
            continue
        try:
            item[1]()
        except KeyboardInterrupt:
            print("\nOperation interrupted.")
        except Exception as exc:
            print(f"\nSomething went wrong: {exc}")
            print("Check that dependencies and required data are available.")
        pause()


if __name__ == "__main__":
    main()
