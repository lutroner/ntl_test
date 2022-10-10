# Тестовое задание


### Как установить

Python3 должен быть уже установлен.
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для
установки зависимостей:

```
pip install -r requirement.txt
```

Рекомендуется использовать [virtualenv/venv](https://docs.python.org/3/library/venv.html) 
для изоляции проекта.

Также необходимо добавить переменную окружения ```TOKEN``` в которую поместить токен API 
сервиса FindFace.

### Пример использования

1. Поиск по карточке:

```console
$ python3 main.py  --card_id=839
```
где ```card_id``` - номер карточки с именем ```find him```. В результате будет сформирован 
отчет с найденными событиями с участием данного лица.
2. Поиск похожих лиц по id события, если, например, карточка еще не заведена: 
```console
$ python3 main.py --event_id=4469884292355629956
```
в результате также получим отчет со всеми событиями лица.

Также в репозитории примеры отчетов:
- ```report_from_script.xlsx``` - пример отчета сформированного данным скриптом по
card_id=829 (find him). В отчет включено имя, заданное в карточке. Также в нижней части
информация по количеству визитов и времени последнего.
- ```report_from_webinterface.xlsx``` похожий отчет из веб-интерфейса.