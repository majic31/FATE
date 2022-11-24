from fate.components import cpn
from fate.components.spec import DatasetArtifact, Output, roles


@cpn.component(roles=[roles.GUEST, roles.HOST], provider="fate", version="2.0.0.alpha")
@cpn.parameter("path", type=str, default=None, optional=False)
@cpn.parameter("format", type=str, default="csv", optional=False)
@cpn.parameter("id_name", type=str, default="id", optional=True)
@cpn.parameter("delimiter", type=str, default=",", optional=True)
@cpn.parameter("label_name", type=str, default=None, optional=True)
@cpn.parameter("label_type", type=str, default="float32", optional=True)
@cpn.parameter("dtype", type=str, default="float32", optional=True)
@cpn.artifact("output_data", type=Output[DatasetArtifact], roles=[roles.GUEST, roles.HOST])
def reader(
    ctx,
    role,
    path,
    format,
    id_name,
    delimiter,
    label_name,
    label_type,
    dtype,
    output_data,
):
    read_data(ctx, path, format, id_name, delimiter, label_name, label_type, dtype, output_data)


def read_data(ctx, path, format, id_name, delimiter, label_name, label_type, dtype, output_data):
    from types import SimpleNamespace

    if format == "csv":
        data_meta = SimpleNamespace(
            uri=path,
            name="data",
            metadata=dict(
                format=format,
                id_name=id_name,
                delimiter=delimiter,
                label_name=label_name,
                label_type=label_type,
                dtype=dtype,
            ),
        )
        data = ctx.reader(data_meta).read_dataframe()
        ctx.writer(output_data).write_dataframe(data)
