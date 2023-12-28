"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1beta1 import run_function_pb2 as fnv1beta1
from crossplane.function.proto.v1beta1 import run_function_pb2_grpc as grpcv1beta1


class FunctionRunner(grpcv1beta1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()

    async def RunFunction(
        self, req: fnv1beta1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1beta1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        rsp = response.to(req)

        in_ = req.input
        values = in_["valuesXrPath"]

        for value in values:
          r = in_["resources"][0]["base"]
          name = f'{in_["namePrefix"]}{value["name"]}'

          for k in value:
            if "name" in k:
              r["metadata"] = {"labels": {"function" : "loop"}}
              r["metadata"]["name"] = (name)
            else:
              r["spec"]["forProvider"][f"{k}"] = (value[k])

        response.normal(rsp, f"I was run with input {in_}!")
        log.info("I was run!", input=in_)

        return rsp
