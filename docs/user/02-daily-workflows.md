# 02. Ежедневные Сценарии

## Сценарий A: Зафиксировать новую идею
1. Вызвать `write_memory`:
```json
{
  "layer": "shallow",
  "path": "ideas/auth-refresh-flow",
  "content": "Описание идеи...",
  "tags": ["idea", "auth"]
}
```
2. Проверить через `read_memory` по `path`.

## Сценарий B: Найти заметки по теме
1. Вызвать `search_room`:
```json
{
  "room": "01_Shallow/ideas",
  "query": "auth"
}
```
2. Проверить `result.data.matches`.

## Сценарий C: Повысить запись в следующий слой вручную
1. Вызвать `move_file`:
```json
{
  "source": "01_Shallow/ideas/auth-refresh-flow.md",
  "dest_layer": "sediment"
}
```
2. Проверить новый путь в `result.data.destination`.

## Сценарий D: Обновить карту связей
1. Добавить ссылку:
```json
{
  "action": "add_link",
  "details": { "link": "[[02_Sediment/auth-refresh-flow.md]]" }
}
```
2. Удалить ссылку аналогично через `action = "remove_link"`.

## Сценарий E: Запустить седиментацию
1. Dry-run:
```json
{
  "dry_run": true
}
```
2. Реальное выполнение:
```json
{
  "dry_run": false,
  "confirm": true
}
```

## Сценарий F: Архивация ошибочной записи
`purge_memory` требует `confirm=true`:
```json
{
  "path": "01_Shallow/ideas/wrong.md",
  "reason": "invalid context",
  "confirm": true
}
```
