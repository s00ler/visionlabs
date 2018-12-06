## Решения делались на python 3.6.5
**Задача 1**: Напишите функцию сравнения двух json-объектов (float поля должны сравниваться с точностью до 5 знаков)

**Решение**: ```json_compare.py```

**Задача 2**: Есть сервер. На нём ресурс /images, который умеет сохранять картинки, если к нему обратишься методом POST. Необходимо написать загрузчик картинок из данной папки на данный сервис. Скрипт принимает на вход путь до папки. Запрещено пользоваться волшебными функциями из библиотек "загрузи всё сам".

**Решение**: ```upload_images.py```

**Задача 3**: Вы были приняты в компанию "Рога и копыта". Первым же делом Вас попросили узнать какие функции на сервере тормозят. Политика компании запрещает устанавливать дополнительные непроверенные модули, пакеты и т.д. Вам доступны стандартные функции и бибиотеки. Вы можете внести свои изменения в код и загрузить код на тестовый сервер, может быть несколько раз, далее вам доступны только логи с него. Что делать?

**Решение**: Первое, что приходит в голову - методами опрашивания коллег, пристального взгляда и научного тыка сузить область поиска боттлнеков в коде. Далее в подозрительные места понавесил бы декораторов ```timeit``` и ```cache_profile``` (написаны на скорую руку, скорее концептуальная идея, чем реализация. К ним, как минимум, стоит прикрутить пакет ```logging```, для нормальной записи логов и т.д.) из файла ```decorators.py```. После раскладки на тестовый сервер изучил бы логи работы и, итеративно, повторил операции несколько раз, локализуя проблемы. Есть еще идея посмотреть в сторону пакета ```trace```, он вроде умеет считать время и количество вызовов функций. Если отойти от решения тестовой задачи в сторону решения реальной проблемы, то использовал бы пакет ```cProfile``` вместе с ```snakeviz``` и ```gprof2dot```. Для этого когда-то давно написал декоратор ```profile```, который вешается где-то на внешнем уровне (на хэндлер запроса, например) и позволяет детально изучить его работу.

**Задача 4**: У компании "Рога и копыта" есть сервис "RED", который работает по REST и определяет количество красного цвета на изображении. Сервис стал очень популярным и компания решила добавить ещё один сервис "RED_STATS", в который "RED" скидывает сообщения о том что у такого-то клиента пришла картинка с таким-то количеством красного цвета. Для клиентов у "RED_STATS" должны появиться две следующие функции: возможность подписаться на оповещения, что пришла картинка, у которой красного больше, чем заданное клиентом значение. Получать статистику по времени, сколько вообще за данный промежуток было послано изображений, сколько изображений у которых красного было больше заданного значения. Ваша задача спроектировать работу "RED_STATS", как он будет общаться с клиентами, как хранить данные, как масштабироваться и т.д

**Решение**:
  0. Допустим, что картинки, приходящие в RED, открыты для всех клиентов. Тогда, клиенты, подписанные на оповещения, и запрашивающие статистику, получают информацию обо всех картинках, а не только о своих. Изменить это поведение не сложно, информация о том, какой клиент прислал картинку все равно будет храниться в базе.

  1. У RED_STATS должна быть ручка для сохранения информации о пришедшей картинке, которую дергает RED после обработки изображения. Например:

  ```POST /stats с json-payload {"image_id": 0, "timestamp": 0, "client_id": 0, "red": 0.85}
  ```

  Для хранения данных можно использовать, например, колоночную БД ClickHouse. Информация будет сразу отсортирована по времени, поэтому чтение будет быстрым, удалять и изменять данные нам не нужно. Это даст возможность быстро записывать и читать данные из базы.
  2. Для клиентов, которые хотят получить статистику по картинкам за указанный промежуток и/или указанным red, нужна ручка, которая будет доставать из базы количество картинок и возвращать результат. Фильтрация по времени будет быстрой, из-за заранее отсортированных данных. Например:

  ```GET /stats с параметрами to: timestamp, from: timestamp, red: float
  ```

  3. Для подписки клиентов на оповещения о пришедшей картинке, клиенты присоединяются к веб-сокету с указанием порогового значения для получения оповещения. Храним записи о подключенных клиентах в, например, PostgreSQL в таблице client_connections(id, client_id, min_red, active). Добавляем записи о новых клиентах, ставим active =  false при разрыве соединения, обновляем active и red при переподключении. При получении информации о картинке делаем запрос в базу, чтобы достать активных юзеров с min_red <= red картинки. Отправляем найденным клиентам сообщения.

  Если возникнет потребность в масштабировании можно сделать следующее: сделать несколько инстансов RED_STATS, к какому обратится RED будет определять балансировщик нагрузки. Выбранный инстанс делает запись в базу и отправляет сообщение в очередь, что пришла информация о картинке. С другой стороны, опять же через балансировщик, клиент подключается к одной из нескольких нод, которые хранят у себя записи о подключениях. Ноды видят сообщение, проверяют есть ли у них пользователи, которым нужно отправить оповещение, если надо - отправляют. Все ноды просмотрели - удаляем из очереди.
