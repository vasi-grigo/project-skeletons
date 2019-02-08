import pyskull_grpc
import pyskull_pb2

from pyskull.common import Ctx, api, PROFILE_GRPC


class Greeter(pyskull_grpc.GreeterBase):

    def __init__(self, c: Ctx):
        super().__init__()
        self.ctx = c

    @api('SayHello', PROFILE_GRPC)
    async def SayHello(self, stream):
        if self.ctx.tracer_current_span:
            with self.ctx.tracer.start_span('blah', child_of=self.ctx.tracer_current_span) as child_span:
                self.ctx.tracer_current_span.log_kv({'from_blah': 'fooblah'})
                child_span.log_kv({'blah': 'blah blah'})

        request = await stream.recv_message()
        message = f'Hello, {request.name}!'
        await stream.send_message(pyskull_pb2.HelloReply(message=message))