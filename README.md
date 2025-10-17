-Бизнес-домен: “Система обработки онлайн-заказов в ресторане доставки еды”
-Имя: Мунгой Шеллер Валмиро Да Линда
-Группа: 5130904/30108
-Вариант: 2 [ИБ; И32; П31; Д1031; Д10O3; Д2П2; Д2Б2; OР2; ОД2]


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



## 1.1. Sequence диаграмма (Успешная обработка заказа):

<img width="753" height="765" alt="image" src="https://github.com/user-attachments/assets/c5bee9cb-5ebd-48b9-825a-5f83c1f0bdd5" />


## 1.2. Sequence диаграмма (Переполнение буфера и отказ старого заказа):

<img width="829" height="633" alt="image" src="https://github.com/user-attachments/assets/da6da9ae-4f5f-4417-a97e-1defe0d040fe" />


## 2. Диаграмма классов:

<img width="1205" height="1650" alt="domain-model" src="https://github.com/user-attachments/assets/bcf19589-92fc-4abc-9a11-aa2ace2d90e1" />


### 4. Flowchart:
<img width="1192" height="1650" alt="flowchart2" src="https://github.com/user-attachments/assets/44323ff2-3fae-442d-8d58-f1dab87f95f5" />
