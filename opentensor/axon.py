from concurrent import futures
from loguru import logger

import grpc
import random
import threading
import torch

from opentensor import opentensor_pb2_grpc as opentensor_grpc
from opentensor import opentensor_pb2
import opentensor

class Axon(opentensor_grpc.OpentensorServicer):
    """ Processes Fwd and Bwd requests for a set of local Synapses """
    def __init__(self, config: opentensor.Config):
        self._config = config

        # Init server objects.
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        opentensor_grpc.add_OpentensorServicer_to_server(self, self._server)
        self._server.add_insecure_port('[::]:' + str(self._config.axon_port))

        # Local synapses
        self._local_synapses = {}

        # Serving thread.
        self._thread = None

    def __del__(self):
        """ Delete the synapse terminal. """
        self.stop()

    def start(self):
        """ Start the synapse terminal server. """
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        try:
            self._server.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()
        except Exception as e:
            logger.error(e)

    def stop(self):
        """ Stop the synapse terminal server """
        self._server.stop(0)

    def subscribe(self, synapse_proto: opentensor_pb2.Synapse, synapse: opentensor.Synapse):
        """ Adds an Synapse to the serving set """
        self._local_synapses[synapse_proto.identity] = synapse
        
        
    async def Forward(self, request: opentensor_pb2.TensorMessage, context: grpc.ServicerContext):
        # TODO (const): optionally check signature.
        # Return null response if the target does not exist.
        if request.synapse_key not in self._local_synapses:
            return opentensor_pb2.TensorMessage()
        synapse = self._local_synapses[request.synapse_key]
        
        # Make local call.
        xs = [opentensor.PyTorchSerializer.deserialize(x) for x in request.tensors]
        ys = synapse (xs)
        ys_serialized = [opentensor.PyTorchSerializer.serialize(y) for y in ys]

        response = opentensor_pb2.TensorMessage(
            version = opentensor.PROTOCOL_VERSION,
            neuron_key = self._config.identity.neuron_key(),
            synapse_key = request.synapse_key,
            tensors = output_tensors)
        return response

    async def Backward(self, request: opentensor_pb2.TensorMessage, context: grpc.ServicerContext):
        # TODO (const): optionally check signature.
        # Return null response if the target does not exist.
        if request.synapse_key not in self._local_synapses:
            return opentensor_pb2.TensorMessage()
        synapse = self._local_synapses[request.synapse_key]
        
        # Make local call.
        xs = [opentensor.PyTorchSerializer.deserialize(x) for x in request.tensors]
        ys = synapse.backward(xs)
        ys_serialized = [opentensor.PyTorchSerializer.serialize(y) for y in ys]

        response = opentensor_pb2.TensorMessage(
            version = opentensor.PROTOCOL_VERSION,
            neuron_key = self._config.identity.neuron_key(),
            synapse_key = request.synapse_key,
            tensors = output_tensors)
        return response