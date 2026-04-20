from sediment_palace.domain.frontmatter import compose_frontmatter, split_frontmatter


def test_frontmatter_roundtrip():
    metadata = {"id": "mem_1", "layer": "shallow", "tags": ["idea"]}
    body = "Hello memory"
    text = compose_frontmatter(metadata, body)
    parsed_meta, parsed_body = split_frontmatter(text)
    assert parsed_meta["id"] == "mem_1"
    assert parsed_meta["layer"] == "shallow"
    assert parsed_body.strip() == body
