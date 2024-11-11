from services.crawler import CrawlerService
from services.mq import MQ
from services.cdc import CDCService
from services.bytewax import Bytewax
from services.datagen import Datagen
from services.inference_endpoint import Inference

from security.sg import SecurityGroup as SG

from hosting_component.function import LambdaService
from hosting_component.farget import FargateService


lambdas = LambdaService()
lambdas.add_lambda(CrawlerService(boundary_sgs=[SG.crawler.id]))
lambdas.add_lambda(Datagen(boundary_sgs=[SG.datagen.id]))
lambdas.add_lambda(Inference(boundary_sgs=[SG.inference.id]))

containers = FargateService()
containers.add_service(MQ(boundary_sgs=[SG.mq.id, SG.bytewax.id, SG.cdc.id]))
containers.add_service(CDCService(boundary_sgs=[SG.cdc.id, SG.mq.id]))
containers.add_service(Bytewax(boundary_sgs=[SG.bytewax.id, SG.mq.id]))

if __name__ == "__main__":
    lambdas.deploy_all_lambda_with_as_api()
    containers.deploy_all()
