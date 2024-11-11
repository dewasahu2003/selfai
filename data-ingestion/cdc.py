import json
import logging

from bson import json_util
from config import settings
from db import MongoDBConnector
from mq import publish_to_mq


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename="app.log"),
    ],
)


def stream_process():
    try:
        mongo_clinet = MongoDBConnector()
        db = mongo_clinet[settings.MONGO_DB_NAME]
        logging.info("connected to mongo")

        changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])
        for change in changes:
            data_type = change["ns"]["coll"]
            entry_id = str(change["fullDocument"]["_id"])

            change["fullDocument"].pop("_id")
            change["fullDocument"]["type"] = data_type
            change["fullDocument"]["entry_id"] = entry_id

            if data_type not in ["articles", "posts", "repositories"]:
                logging.info(f"unsupported data type: {data_type}")

            data = json.dumps(change["fullDocument"], default=json_util.default)
            logging.info(f"changed detected and serialised for data sample:{data}")

            publish_to_mq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=data)
            logging.info(f"data of type:'{data_type}' publised to RabbitMQ")
    except Exception as e:
        logging.error(f"failed to stream data: {e}")


if __name__ == "__main__":
    stream_process()
