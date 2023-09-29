from pymilvus import (
    FieldSchema,
    CollectionSchema,
    DataType)

conv_id = FieldSchema(
  name="conv_id",
  dtype=DataType.INT64,
  is_primary=True,
    auto_id=True
)
conv_text = FieldSchema(
    name="conv_text",
    dtype=DataType.VARCHAR,
    max_length=65535
)
conv_vector = FieldSchema(
  name="conv_vector",
  dtype=DataType.FLOAT_VECTOR,
  dim=1536
)
human_msg = FieldSchema(
  name="human_msg",
  dtype=DataType.VARCHAR,
    max_length=65535

)
ai_msg = FieldSchema(
  name="ai_msg",
  dtype=DataType.VARCHAR,
    max_length=65535

)
timestamp = FieldSchema(
  name="timestamp",
  dtype=DataType.INT64
)

token_count  = FieldSchema(
  name="token_count",
  dtype=DataType.INT64
)

schema = CollectionSchema(
  fields=[conv_id, conv_text, conv_vector, human_msg, ai_msg, timestamp, token_count],
  description="chat conversation"
)
