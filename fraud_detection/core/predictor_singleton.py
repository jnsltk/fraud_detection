from detector.models import FraudDetectionModel
from detector.services.ml_pipeline import Predictor
import os

VERSION_TAG = os.environ.get('VERSION_TAG')


class PredictorSingleton:
    """
        Singleton class to manage the predictor instance. It will only create one instance of the predictor,
        and will return the same instance every time it is called. It can also change the model used by the predictor,
        by replacing the current predictor with a new one. On initialization, it will try to load the deployed model.

        Example usage:
        predictor = PredictorSingleton.get_instance().get_predictor()
        prediction = predictor.predict(input) # See the Predictor class for more details

    """
    _instance: 'PredictorSingleton' = None
    _predictor: Predictor = None

    def __init__(self):
        raise Exception("Call get_instance instead")

    @classmethod
    def get_instance(cls) -> 'PredictorSingleton':
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

            model_data = FraudDetectionModel.objects.filter(is_deployed=True).values('version', 'id').first()

            if model_data is None:
                print("No model is deployed")
                cls._instance._predictor = None

            elif model_data['version'].split('.')[0][1:] != VERSION_TAG.split('.')[0]:
                print("Model version does not match software version")
                cls._instance._predictor = None

            else:
                cls._instance._predictor = Predictor(model_id=str(model_data['id']))

        return cls._instance

    def change_model(self, model_id: str) -> Predictor:
        self._predictor = Predictor(model_id=model_id)
        return self._predictor

    def get_predictor(self) -> Predictor:
        return self._predictor
