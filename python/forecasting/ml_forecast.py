"""Module docstring."""
from sklearn.linear_model import LinearRegression
import numpy as np


class MLForecast:
    """Class docstring."""

    def train(self, values):
        """Function docstring."""

        x = np.arange(len(values)).reshape(-1, 1)
        y = np.array(values)

        model = LinearRegression()
        model.fit(x, y)

        return model

    def predict(self, model, future_day):
        """Function docstring."""

        return model.predict(
            [[future_day]]
        )[0]
