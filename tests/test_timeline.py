def test_list_eras(client):
    response = client.get("/api/eras")
    assert response.status_code == 200
    eras = response.json()
    assert len(eras) > 0
    assert {"id", "nome", "periodo", "descricao"} <= eras[0].keys()


def test_list_timeline_sorted_chronologically(client):
    response = client.get("/api/timeline")
    assert response.status_code == 200
    marcos = response.json()
    assert len(marcos) > 0
    anos = [m["ano"] for m in marcos]
    assert anos == sorted(anos)


def test_list_timeline_filtered_by_era(client):
    response = client.get("/api/timeline", params={"era": "arcade"})
    assert response.status_code == 200
    marcos = response.json()
    assert len(marcos) > 0
    assert all(m["era"] == "arcade" for m in marcos)


def test_list_timeline_unknown_era_returns_empty(client):
    response = client.get("/api/timeline", params={"era": "nao-existe"})
    assert response.status_code == 200
    assert response.json() == []


def test_get_marco_by_id(client):
    response = client.get("/api/timeline/pac-man-1980")
    assert response.status_code == 200
    marco = response.json()
    assert marco["id"] == "pac-man-1980"
    assert marco["ano"] == 1980
    assert "fontes" in marco


def test_get_marco_not_found(client):
    response = client.get("/api/timeline/nao-existe")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
