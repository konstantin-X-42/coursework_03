from unittest.mock import patch
import main

# ====================================================================
# Проверка функции main()
# ====================================================================

@patch("main.user_interaction")
def test_main_function(mock_user):
    """Проверяет запуск главной функции программы."""
    main.main()
    mock_user.assert_called_once()


# ====================================================================
# Проверка загрузки данных из API и сохранения в БД
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_user_interaction_loads_planes(mock_db, mock_api, monkeypatch, fake_api_data):
    """Проверяет получение данных API и их сохранение в БД при старте."""
    mock_api.return_value.aeroplanes = fake_api_data

    # Пользователь сразу выбирает пункт 6 (Выход) после автозагрузки 10 стран
    inputs = iter(["6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()

    # Проверяем, что метод сохранения данных в БД вызвался для каждой из 10 стран
    assert mock_db.return_value.save_aeroplanes_data.call_count == 10


# ====================================================================
# Проверка меню 1 ->> Количество самолетов по странам
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_menu_countries_count(mock_db, mock_api, monkeypatch, fake_api_data, capsys):
    """Проверяет вывод количества самолетов по странам."""
    mock_api.return_value.aeroplanes = fake_api_data
    mock_db.return_value.get_countries_and_aeroplanes_count.return_value = [
        {"country": "Canada", "aeroplanes_count": 5}
    ]

    inputs = iter(["1", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()
    output = capsys.readouterr().out

    assert "Canada" in output
    assert "5" in output


# ====================================================================
# Проверка меню 2 ->> Полный список судов
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_menu_show_all_planes(mock_db, mock_api, monkeypatch, fake_api_data, capsys):
    """Проверяет вывод полного списка всех воздушных судов из БД."""
    mock_api.return_value.aeroplanes = fake_api_data
    mock_db.return_value.get_all_aeroplanes.return_value = [
        {"callsign": "AAA111", "origin_country": "Canada", "velocity": 250.5, "altitude": 10000.0}
    ]

    inputs = iter(["2", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()
    output = capsys.readouterr().out

    assert "AAA111" in output
    assert "250.5" in output


# ====================================================================
# Проверка меню 3 ->> Средняя скорость
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_menu_avg_speed(mock_db, mock_api, monkeypatch, fake_api_data, capsys):
    """Проверяет вывод средней скорости."""
    mock_api.return_value.aeroplanes = fake_api_data
    mock_db.return_value.get_avg_speed.return_value = 215.75

    inputs = iter(["3", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()
    output = capsys.readouterr().out

    assert "215.75" in output


# ====================================================================
# Проверка меню 4 ->> Скорость выше средней
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_menu_higher_speed(mock_db, mock_api, monkeypatch, fake_api_data, capsys):
    """Проверяет вывод самолетов со скоростью выше средней."""
    mock_api.return_value.aeroplanes = fake_api_data
    mock_db.return_value.get_aeroplanes_with_higher_speed.return_value = [
        {"callsign": "FAST99", "origin_country": "USA", "velocity": 350.0}
    ]

    inputs = iter(["4", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()
    output = capsys.readouterr().out

    assert "FAST99" in output
    assert "350.0" in output


# ====================================================================
# Проверка меню 5 ->> Поиск по ключевому слову
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_menu_search_keyword(mock_db, mock_api, monkeypatch, fake_api_data, capsys):
    """Проверяет поиск самолетов по части позывного."""
    mock_api.return_value.aeroplanes = fake_api_data
    mock_db.return_value.get_aeroplanes_with_keyword.return_value = [
        {"callsign": "ACA123", "origin_country": "Canada", "altitude": 9000.0}
    ]

    inputs = iter(["5", "ACA", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()
    output = capsys.readouterr().out

    assert "ACA123" in output


# ====================================================================
# Проверка неверного пункта меню
# ====================================================================

@patch("main.APIAdapter")
@patch("main.DBManager")
def test_invalid_menu_choice(mock_db, mock_api, monkeypatch, capsys):
    """Проверяет обработку некорректного пункта меню."""
    mock_api.return_value.aeroplanes = None

    inputs = iter(["9", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.user_interaction()
    output = capsys.readouterr().out

    assert "Неверный пункт меню" in output





# from unittest.mock import patch
#
# import main
#
# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# # запуск тестов в модуле main/py:
# # poetry run pytest tests/test_main.py -v
# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# # запуск тестов в модуле test_main.py с покрытием в html
# # poetry run pytest tests/test_main.py --cov=main --cov-report=html
# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# # ====================================================================
# # Проверка функции main()
# # ====================================================================
#
# @patch("main.user_interaction")
# def test_main_function(mock_user):
#     """
#     Проверяет запуск главной функции программы.
#     """
#
#     main.main()
#
#     mock_user.assert_called_once()
#
#
# # ====================================================================
# # Проверка загрузки данных из API и сохранения
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_user_interaction_loads_planes(
#     mock_storage, mock_api, monkeypatch, fake_api_data
# ):
#     """
#     Проверяет:
#     - получение данных API;
#     - создание Aeroplane;
#     - сохранение самолетов.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     inputs = iter(["Canada", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     assert mock_storage.return_value.add_aeroplane.call_count == 2
#
#
# # ====================================================================
# # Проверка меню 1 ->> Показать все самолеты
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_show_all_planes(
#     mock_storage, mock_api, monkeypatch, fake_api_data, capsys
# ):
#     """
#     Проверяет вывод всех самолетов.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250.5,
#             "altitude": 10000,
#         }
#     ]
#
#     inputs = iter(["Canada", "1", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "AAA111" in output
#     assert "10000" in output
#
#
# # ====================================================================
# # Проверка меню 2 ->> TOP-N по высоте
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_top_altitude(mock_storage, mock_api, monkeypatch, fake_api_data, capsys):
#     """
#     Проверяет сортировку по высоте.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "HIGH",
#             "origin_country": "Canada",
#             "velocity": 300,
#             "altitude": 12000,
#         },
#         {"callsign": "LOW", "origin_country": "USA", "velocity": 150, "altitude": 3000},
#     ]
#
#     inputs = iter(["Canada", "2", "1", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "HIGH" in output
#     assert "12000" in output
#
#
# # ====================================================================
# # Проверка ошибки TOP-N
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_top_invalid_number(mock_storage, mock_api, monkeypatch, capsys):
#     """
#     Проверяет ввод неправильного числа TOP-N.
#     """
#
#     mock_api.return_value.aeroplanes = None
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250,
#             "altitude": 10000,
#         }
#     ]
#
#     inputs = iter(["Canada", "2", "abc", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "корректное целое число" in output
#
#
# # ====================================================================
# # Проверка меню 3 ->> Фильтр по стране
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_filter_country(
#     mock_storage, mock_api, monkeypatch, fake_api_data, capsys
# ):
#     """
#     Проверяет поиск самолетов по стране.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250,
#             "altitude": 10000,
#         },
#         {
#             "callsign": "BBB222",
#             "origin_country": "USA",
#             "velocity": 150,
#             "altitude": 5000,
#         },
#     ]
#
#     inputs = iter(["Canada", "3", "Canada", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "AAA111" in output
#     assert "BBB222" not in output
#
#
# # ====================================================================
# # Проверка меню 4 ->> Удаление самолета
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_delete_plane(mock_storage, mock_api, monkeypatch, fake_api_data):
#     """
#     Проверяет удаление самолета по позывному.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     inputs = iter(["Canada", "4", "AAA111", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     (
#         mock_storage.return_value.delete_aeroplanes_by_callsign.assert_called_once_with(
#             "AAA111"
#         )
#     )
#
#
# # ====================================================================
# # Проверка меню 5 ->> Выход из программы
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_exit(mock_storage, mock_api, monkeypatch, capsys):
#     """
#     Проверяет корректный выход.
#     """
#
#     mock_api.return_value.aeroplanes = None
#
#     inputs = iter(["Canada", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "Программа мониторинга авиарейсов ✈️ успешно завершена." in output
#
#
# # ====================================================================
# # Проверка неверного пункта меню
# # ====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_invalid_menu_choice(mock_storage, mock_api, monkeypatch, capsys):
#     """
#     Проверяет обработку неизвестного пункта меню.
#     """
#
#     mock_api.return_value.aeroplanes = None
#
#     inputs = iter(["Canada", "9", "5"])
#
#     monkeypatch.setattr("builtins.input", lambda _: next(inputs))
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "Неверный пункт меню" in output
