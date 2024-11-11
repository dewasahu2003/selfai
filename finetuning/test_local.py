from pandas import DataFrame
from qwak.model.tools import run_local
from model import MixtralModel

if __name__ == "__main__":

    model = MixtralModel()
    input_vector = DataFrame(
        [
            {
                "instruction": "write me a medium post for qwak use case",
            }
        ]
    ).to_json()

    prediction = run_local(model, input_vector)
    print(prediction)
