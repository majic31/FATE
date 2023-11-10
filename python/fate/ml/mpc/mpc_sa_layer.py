from typing import Any

import torch

from fate.arch.context import Context
from fate.arch.protocol.mpc.primitives import ArithmeticSharedTensor


class SSHEAggregatorLayer(torch.nn.Module):
    def __init__(
        self, ctx: Context, in_features_a, in_features_b, out_features, rank_a, rank_b, lr=0.05, generator=None
    ):
        self.aggregator = SSHEAggregator(
            ctx, in_features_a, in_features_b, out_features, rank_a, rank_b, lr, generator=generator
        )
        super().__init__()

    def set_lr(self, lr):
        self.aggregator.learning_rate = lr

    def forward(self, input):
        return SSHEAggregatorFunction.apply(input, self.aggregator)

    def get_wa(self):
        return self.aggregator.wa.get_plain_text()

    def get_wb(self):
        return self.aggregator.wb.get_plain_text()


class SSHEAggregatorFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input, aggregator: "SSHEAggregator"):
        ctx.save_for_backward(input)
        output = aggregator.forward(input)
        ctx.aggregator = aggregator
        return output

    @staticmethod
    def backward(ctx: Any, *grad_outputs: Any) -> Any:
        aggregator: "SSHEAggregator" = ctx.aggregator
        aggregator.ctx.mpc.info(f"grad_outputs={grad_outputs}", dst=[0, 1])
        ha = ctx.saved_tensors[0] if aggregator.ctx.rank == aggregator.rank_a else None
        hb = ctx.saved_tensors[0] if aggregator.ctx.rank == aggregator.rank_b else None
        dz = grad_outputs[0] if aggregator.ctx.rank == aggregator.rank_b else None
        return aggregator.backward(dz, ha, hb), None


class SSHEAggregator:
    def __init__(
        self,
        ctx: Context,
        in_features_a,
        in_features_b,
        out_features,
        rank_a,
        rank_b,
        lr,
        precision_bits=None,
        generator=None,
    ):
        self.ctx = ctx
        self.wa = ctx.mpc.random_tensor(shape=(in_features_a, out_features), src=rank_a, generator=generator)
        self.wb = ctx.mpc.random_tensor(shape=(in_features_b, out_features), src=rank_b, generator=generator)
        self.phe_cipher = ctx.cipher.phe.setup()
        self.rank_a = rank_a
        self.rank_b = rank_b
        self.lr = lr
        self.precision_bits = precision_bits

    def forward(self, input):
        xa = input if self.ctx.rank == self.rank_a else None
        xb = input if self.ctx.rank == self.rank_b else None
        out = self.ctx.mpc.sshe.cross_smm(
            ctx=self.ctx,
            xa=xa,
            xb=xb,
            wa=self.wa,
            wb=self.wb,
            rank_a=self.rank_a,
            rank_b=self.rank_b,
            phe_cipher=self.phe_cipher,
            precision_bits=self.precision_bits,
        )
        output = out.get_plain_text(dst=self.rank_b)
        if self.ctx.rank == self.rank_b:
            return output
        else:
            # return a fake tensor to avoid error
            # because backward() has nothing to do with forward output in rank_a
            return torch.zeros(1)

    def backward(self, dz, ha, hb):
        from fate.arch.protocol.mpc.mpc import FixedPointEncoder

        encoder = FixedPointEncoder(self.precision_bits)
        ha_encoded_t = self.ctx.mpc.cond_call(lambda: encoder.encode(ha).T, lambda: None, dst=self.rank_a)
        dz_encoded = self.ctx.mpc.cond_call(lambda: encoder.encode(dz), lambda: None, dst=self.rank_b)

        dh = _backward(
            self.ctx, self.wa, self.wb, self.rank_a, self.rank_b, tensor_b=dz_encoded, phe_cipher=self.phe_cipher
        )

        # update wa
        ga = self.ctx.mpc.sshe.smm_lc(
            self.ctx,
            tensor_a=ha_encoded_t,
            tensor_b=dz_encoded,
            rank_a=self.rank_a,
            rank_b=self.rank_b,
            cipher=self.phe_cipher,
        )
        ga.share = ga.div_(encoder.scale).share
        self.wa -= self.lr * ga

        # update wb
        if self.ctx.rank == self.rank_b:
            gb = hb.T @ dz
            self.wb.share = self.wb.share - self.wb.encoder.encode(self.lr * gb)

        return dh


def _backward(
    ctx: Context, wa: ArithmeticSharedTensor, wb: ArithmeticSharedTensor, rank_a, rank_b, tensor_b, phe_cipher
):
    if ctx.rank == rank_a:
        enc_wa_share = phe_cipher.get_tensor_encryptor().encrypt_tensor(wa.share.T)
        ctx.mpc.communicator.send(enc_wa_share, rank_b)
        enc_dha = ctx.mpc.communicator.recv(None, rank_b)
        dha = phe_cipher.get_tensor_decryptor().decrypt_tensor(enc_dha)
        dha = dha / wa.encoder.scale
        dha = dha / wa.encoder.scale

        enc_wb_share = phe_cipher.get_tensor_encryptor().encrypt_tensor(wb.share.T)
        ctx.mpc.communicator.send(enc_wb_share, rank_b)
        enc_dhb = ctx.mpc.communicator.recv(None, rank_b)
        dhb = phe_cipher.get_tensor_decryptor().decrypt_tensor(enc_dhb)
        ctx.mpc.communicator.send(dhb, rank_b)

        return dha

    if ctx.rank == rank_b:
        enc_wa_share = ctx.mpc.communicator.recv(None, rank_a)
        enc_dha = tensor_b @ (enc_wa_share + wa.share.T)
        ctx.mpc.communicator.send(enc_dha, rank_a)

        enc_wb_share = ctx.mpc.communicator.recv(None, rank_a)
        enc_dhb = tensor_b @ enc_wb_share
        # enc_dhb = enc_dhb + epsilon
        ctx.mpc.communicator.send(enc_dhb, rank_a)
        dhb = ctx.mpc.communicator.recv(None, rank_a)
        dhb += tensor_b @ wb.share.T
        dhb = dhb / wb.encoder.scale
        dhb = dhb / wb.encoder.scale
        return dhb