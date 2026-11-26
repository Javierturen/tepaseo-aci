def test_index_status_code(client):
    response = client.get("/")

    assert response.status_code == 200


def test_index_content(client):
    response = client.get("/")

    assert "Bienvenido a Tepaseo.cl" in response.get_data(
        as_text=True
    )


def test_page_not_found(client):
    response = client.get("/pagina-inexistente")

    assert response.status_code == 404
