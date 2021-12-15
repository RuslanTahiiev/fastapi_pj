from fastapi import Query, Path


query_q = Query(
    None,
    title='My query!',
    description='Its a test query!',
    alias='query',
    max_length=10
)


path_item_id = Path(
    ...,
    title='Some title for path',
    gt=0,
    le=100
)
