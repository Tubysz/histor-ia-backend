from app.services import knowledge, prompt


def test_search_relevant_matches_title():
    results = knowledge.search_relevant("Pac-Man fantasmas")
    assert any(m["id"] == "pac-man-1980" for m in results)


def test_search_relevant_matches_year():
    results = knowledge.search_relevant("O que aconteceu em 1997?")
    assert any(m["id"] == "deep-blue-1997" for m in results)


def test_search_relevant_returns_empty_when_nothing_matches():
    results = knowledge.search_relevant("qual é a capital da frança")
    assert results == []


def test_build_system_prompt_injects_marcos_when_found():
    marcos = knowledge.search_relevant("Pac-Man")
    text = prompt.build_system_prompt(marcos)
    assert "Pac-Man" in text


def test_build_system_prompt_falls_back_to_eras_when_nothing_matches():
    text = prompt.build_system_prompt([])
    assert "Nenhum marco específico" in text
    for era in knowledge.list_eras():
        assert era["nome"] in text
