Бизнес-домен: “Система обработки онлайн-заказов в ресторане доставки еды” 
Имя: Мунгой Шеллер Валмиро Да Линда
Группа: 5130904/30108
Вариант: 2


# Restaurant Delivery SMO System

A simulation model for restaurant order processing based on Queueing Theory.

## Model Parameters
-ИБ: Источник (бесконечный)
-И32: Источник 3, закон распределения (равномерный-ИЗ2)
-П31: Прибор 3, закон обслуживания (экспоненциальный-ПЗ1)
-Д1031: Дисциплина постановки в буфер (по кольцу-Д1ОЗ1)
-Д10O3: Дисциплина постановки в буфер (по кольцу-Д1ОЗ1)
-Д2П2: Дисциплина выбора прибора заявка идёт на первый свободный прибор
-Д2Б2: Дисциплина выбора заявки из буфера (в порядке поступления “FIFO”)
-OР2: Отображение результатов (графики по значениям параметров)
-ОД2: Динамическое отображение (формализованная схема модели и текущее состояние)


## Diagrams
- `domain-model.mmd` - UML Class Diagram
- `sequence-happy-flow.mmd` - Successful order flow
- `sequence-negative-flow.mmd` - Order rejection flow



1. sd
<img width="750" height="766" alt="image" src="https://github.com/user-attachments/assets/56a267bc-1366-40c3-a424-ac251eb7a021" />

2. ddc

3. dsx
