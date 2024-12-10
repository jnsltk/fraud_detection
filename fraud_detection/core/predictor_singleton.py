from detector.models import FraudDetectionModel
from detector.services.ml_pipeline import Predictor


class PredictorSingleton:
    """
        Singleton class to manage the predictor instance. It will only create one instance of the predictor,
        and will return the same instance every time it is called. It can also change the model used by the predictor,
        by replacing the current predictor with a new one. On initialization, it will try to load the deployed model.

        Usage:
        predictor = PredictorSingleton.get_instance().get_predictor()
        prediction = predictor.predict(input)

    """
    _instance: 'PredictorSingleton' = None
    _predictor: Predictor = None

    def __init__(self):
        raise Exception("Call get_instance instead")

    @classmethod
    def get_instance(cls) -> 'PredictorSingleton':
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            try:
                model_id = FraudDetectionModel.objects.get(is_deployed=True).id,
                cls._instance._predictor = Predictor(model_id=str(model_id[0]))
            except FraudDetectionModel.DoesNotExist:
                print("No model is deployed")
                cls._instance._predictor = None

        return cls._instance

    def change_model(self, model_id: int) -> Predictor:
        self._predictor = Predictor(model_id=str(model_id))
        return self._predictor

    def get_predictor(self) -> Predictor:
        return self._predictor