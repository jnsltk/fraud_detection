from dotenv import load_dotenv
import data_loader
import feature_transformer
import tester
import model

load_dotenv()


def run():
    df = data_loader.load_data()
    df = feature_transformer.transform(df)
    tester.test(df)  # throws if any test fails
    model_output = model.create(df)
    print(model_output)


if __name__ == '__main__':
    run()
