# Trees summary: Частные балы, ц2

Source: figma-mcp-express get_node, origin grace, channel auto-1, full depth. Raw replies saved next to this file as tree_<id>.json.

Columns: root x/y = canvas coordinates (absolute). Descendant x/y = section-relative (sum of parent offsets from the root). parent = parent node id. w/h = node size.
Fill: hex paints from styles.fills; IMAGE paints show imageHash and scaleMode; stroke-only nodes show 'stroke ...'. Style: T = textStyle, F = fillStyle, names as the reply gives them (the reply has no style ids).
Visible: visible=false = hidden node; opacity=0 = transparent but not hidden. Text is cut to 80 characters.

## Roots

| id | name | abs x | abs y | w | h | fills | fillStyle |
|---|---|---|---|---|---|---|---|
| 207:1958 | Section / 08 Этикет · A+D «Книжка» · ore · 1 Кавалерам | 0 | 10364 | 1440 | 1672 | #060606 | v2/Surface/Ink |
| 207:2000 | Section / 08 Этикет · A+D «Книжка» · ore · 2 Дамам | 12442 | 13604 | 1440 | 1672 | #060606 | v2/Surface/Ink |
| 352:2053 | B — гигант на двух поверхностях | 1840 | 200 | 1440 | 900 | #060606 | v2/Surface/Ink |

## 207:1958 — Section / 08 Этикет · A+D «Книжка» · ore · 1 Кавалерам

- Absolute x/y: 0 / 10364; w × h: 1440 × 1672; fills: #060606; fillStyle: v2/Surface/Ink
- Descendants listed: 48; VECTOR nodes skipped: 0

| id | parent | type | name | x | y | w | h | fill | text | font family / style / size | style (T/F) | visible / opacity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 330:4028 | 207:1958 | FRAME | Фото · Бал | 0 | 876 | 656 | 496 | #00000000 |  |  |  |  |
| 330:4029 | 330:4028 | RECTANGLE | Снимок | 0 | 646 | 1100 | 733 | IMAGE + imageHash a5d2f3aa78bd67eb9330d59c548d07393126000b + FILL |  |  |  |  |
| 207:1959 | 207:1958 | TEXT | Метка | 64 | 104 | 137 | 15 | #aba79acc | 08 — Этикет | Unbounded / Regular / 11 | F: v2/Text/Greige 80 |  |
| 207:1960 | 207:1958 | TEXT | Заголовок · строка 1 | 64 | 160 | 871 | 120 | #aba79a | Танцевальный | Old Standard TT / Regular / 150 | F: v2/Text/Greige 100 |  |
| 207:1961 | 207:1958 | TEXT | Заголовок · строка 2 (курсив, на оси 720) | 720 | 280 | 498 | 120 | #aba79a | этикет | Old Standard TT / Italic / 150 | F: v2/Text/Greige 100 |  |
| 207:1962 | 207:1958 | TEXT | Интро 1 | 64 | 424 | 320 | 54 | #aba79acc | Этикет на балу — несколько правил, которые делают вечер комфортным для всех. | Unbounded / Regular / 12 | F: v2/Text/Greige 80 |  |
| 207:1963 | 207:1958 | TEXT | Интро 2 | 400 | 496 | 320 | 72 | #aba79acc | Это не строгие нормы, а рекомендации: знание базовых вещей снимает напряжение и … | Unbounded / Regular / 12 | F: v2/Text/Greige 80 |  |
| 207:1964 | 207:1958 | TEXT | Интро 3 | 720 | 586 | 400 | 90 | #aba79acc | Современный бал — не историческая реконструкция. Искренность здесь важнее идеаль… | Unbounded / Regular / 12 | F: v2/Text/Greige 80 |  |
| 207:1965 | 207:1958 | RECTANGLE | Панель | 720 | 924 | 656 | 448 | #c6c2b6 |  |  | F: v2/Surface/Panel |  |
| 207:1966 | 207:1958 | TEXT | Счётчик | 752 | 956 | 92 | 17 | #060606 | 01 / 02 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1967 | 207:1958 | RECTANGLE | Строка 1 | 752 | 1012 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:1968 | 207:1958 | RECTANGLE | Строка 2 | 752 | 1068 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:1969 | 207:1958 | RECTANGLE | Строка 3 | 752 | 1124 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:1970 | 207:1958 | RECTANGLE | Строка 4 | 752 | 1180 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:1971 | 207:1958 | TEXT | Правило · К1 | 752 | 1024 | 272 | 18 | #060606 | Первыми приглашать на танец. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1972 | 207:1958 | TEXT | Правило · К2 | 752 | 1080 | 496 | 18 | #060606 | Следить, чтобы партнёрше было комфортно на паркете. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1973 | 207:1958 | TEXT | Правило · К3 | 752 | 1136 | 334 | 18 | #060606 | Учитывать ритм и другие пары вокруг. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1974 | 207:1958 | TEXT | Правило · К4 | 752 | 1192 | 386 | 18 | #060606 | Быть вежливыми и тактичными в общении. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1975 | 207:1958 | TEXT | Правило · Д1 | 752 | 1040 | 482 | 18 | #060606 | Принимать приглашения или корректно отклонять их. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:1976 | 207:1958 | TEXT | Правило · Д2 | 752 | 1096 | 477 | 18 | #060606 | Следовать темпу и направлению движения партнёра. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:1977 | 207:1958 | TEXT | Правило · Д3 | 752 | 1152 | 198 | 18 | #060606 | Соблюдать дресс-код. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:1978 | 207:1958 | TEXT | Правило · Д4 | 752 | 1208 | 417 | 18 | #060606 | Проявлять доброжелательность и открытость. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:1979 | 207:1958 | TEXT | Номер 01 | 1320 | 1024 | 24 | 17 | #060606 | 01 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1980 | 207:1958 | TEXT | Номер 02 | 1316 | 1080 | 28 | 17 | #060606 | 02 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1981 | 207:1958 | TEXT | Номер 03 | 1316 | 1136 | 28 | 17 | #060606 | 03 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1982 | 207:1958 | TEXT | Номер 04 | 1316 | 1192 | 28 | 17 | #060606 | 04 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:1983 | 207:1958 | TEXT | Роль · Кавалерам | 787 | 1238 | 557 | 102 | #a84c2c | Кавалерам | Old Standard TT / Regular / 128 | F: v2/Accent/Terracotta Deep |  |
| 207:1984 | 207:1958 | TEXT | Роль · Дамам | 1000 | 1254 | 344 | 102 | #a84c2c | Дамам | Old Standard TT / Regular / 128 | F: v2/Accent/Terracotta Deep | opacity=0 |
| 207:1989 | 207:1958 | LINE | + | 688 | 876 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1990 | 207:1958 | LINE | + | 696 | 884 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1991 | 207:1958 | LINE | + | 1392 | 876 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1992 | 207:1958 | LINE | + | 1400 | 884 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1993 | 207:1958 | LINE | + | 688 | 1372 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1994 | 207:1958 | LINE | + | 696 | 1380 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1995 | 207:1958 | LINE | + | 1392 | 1372 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1996 | 207:1958 | LINE | + | 1400 | 1380 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:1997 | 207:1958 | TEXT | Финал · строка 1 | 64 | 1412 | 1215 | 120 | #aba79a | Запоминать заранее | Old Standard TT / Regular / 150 | F: v2/Text/Greige 100 |  |
| 207:1998 | 207:1958 | TEXT | Финал · строка 2 (от поля) | 64 | 1532 | 739 | 120 | #aba79a | не нужно — | Old Standard TT / Regular / 150 | F: v2/Text/Greige 100 |  |
| 207:1999 | 207:1958 | TEXT | Финал · продолжение капсом (к правому полю) | 976 | 1616 | 400 | 36 | #c6c2b6 | танцмейстер подскажет на паркете. В моменте, с юмором, без давления. | Unbounded / Regular / 12 | F: v2/Text/Greige Light |  |
| 207:2042 | 207:1958 | FRAME | Зона / Панель | 720 | 924 | 656 | 448 | #00000000 |  |  |  |  |
| 330:4022 | 207:1958 | RECTANGLE | Вкладка · Кавалерам · активна | 720 | 876 | 328 | 48 | #c6c2b6 |  |  |  |  |
| 330:4023 | 207:1958 | TEXT | Вкладка · Кавалерам · текст | 744 | 890 | 130 | 20 | #060606 | Кавалерам | Unbounded / Regular / 16 |  |  |
| 330:4024 | 207:1958 | TEXT | Вкладка · Кавалерам · номер | 1000 | 892 | 24 | 15 | #060606 | 01 | Unbounded / Regular / 12 |  |  |
| 330:4025 | 207:1958 | RECTANGLE | Вкладка · Дамам | 1048.5 | 876.5 | 327 | 47.5 | stroke #aba79a66 |  |  |  |  |
| 330:4026 | 207:1958 | TEXT | Вкладка · Дамам · текст | 1072 | 890 | 84 | 20 | #c6c2b6 | Дамам | Unbounded / Regular / 16 |  |  |
| 207:2043 | 207:1958 | FRAME | Зона / Вкладка · Кавалерам | 720 | 876 | 328 | 48 | #00000000 |  |  |  |  |
| 207:2044 | 207:1958 | FRAME | Зона / Вкладка · Дамам | 1048 | 876 | 328 | 48 | #00000000 |  |  |  |  |
| 330:4027 | 207:1958 | TEXT | Вкладка · Дамам · номер | 1328 | 892 | 28 | 15 | #c6c2b6 | 02 | Unbounded / Regular / 12 |  |  |

## 207:2000 — Section / 08 Этикет · A+D «Книжка» · ore · 2 Дамам

- Absolute x/y: 12442 / 13604; w × h: 1440 × 1672; fills: #060606; fillStyle: v2/Surface/Ink
- Descendants listed: 48; VECTOR nodes skipped: 0

| id | parent | type | name | x | y | w | h | fill | text | font family / style / size | style (T/F) | visible / opacity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 330:4036 | 207:2000 | FRAME | Фото · Бал | 0 | 876 | 656 | 496 | #00000000 |  |  |  |  |
| 330:4037 | 330:4036 | RECTANGLE | Снимок | 0 | 646 | 1100 | 733 | IMAGE + imageHash a5d2f3aa78bd67eb9330d59c548d07393126000b + FILL |  |  |  |  |
| 207:2001 | 207:2000 | TEXT | Метка | 64 | 104 | 137 | 15 | #aba79acc | 08 — Этикет | Unbounded / Regular / 11 | F: v2/Text/Greige 80 |  |
| 207:2002 | 207:2000 | TEXT | Заголовок · строка 1 | 64 | 160 | 871 | 120 | #aba79a | Танцевальный | Old Standard TT / Regular / 150 | F: v2/Text/Greige 100 |  |
| 207:2003 | 207:2000 | TEXT | Заголовок · строка 2 (курсив, на оси 720) | 720 | 280 | 498 | 120 | #aba79a | этикет | Old Standard TT / Italic / 150 | F: v2/Text/Greige 100 |  |
| 207:2004 | 207:2000 | TEXT | Интро 1 | 64 | 424 | 320 | 54 | #aba79acc | Этикет на балу — несколько правил, которые делают вечер комфортным для всех. | Unbounded / Regular / 12 | F: v2/Text/Greige 80 |  |
| 207:2005 | 207:2000 | TEXT | Интро 2 | 400 | 496 | 320 | 72 | #aba79acc | Это не строгие нормы, а рекомендации: знание базовых вещей снимает напряжение и … | Unbounded / Regular / 12 | F: v2/Text/Greige 80 |  |
| 207:2006 | 207:2000 | TEXT | Интро 3 | 720 | 586 | 400 | 90 | #aba79acc | Современный бал — не историческая реконструкция. Искренность здесь важнее идеаль… | Unbounded / Regular / 12 | F: v2/Text/Greige 80 |  |
| 207:2007 | 207:2000 | RECTANGLE | Панель | 720 | 924 | 656 | 448 | #c6c2b6 |  |  | F: v2/Surface/Panel |  |
| 207:2008 | 207:2000 | TEXT | Счётчик | 752 | 956 | 96 | 17 | #060606 | 02 / 02 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2009 | 207:2000 | RECTANGLE | Строка 1 | 752 | 1012 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:2010 | 207:2000 | RECTANGLE | Строка 2 | 752 | 1068 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:2011 | 207:2000 | RECTANGLE | Строка 3 | 752 | 1124 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:2012 | 207:2000 | RECTANGLE | Строка 4 | 752 | 1180 | 592 | 1 | #060606 |  |  | F: v2/Text/Ink |  |
| 207:2013 | 207:2000 | TEXT | Правило · К1 | 752 | 1040 | 272 | 18 | #060606 | Первыми приглашать на танец. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:2014 | 207:2000 | TEXT | Правило · К2 | 752 | 1096 | 496 | 18 | #060606 | Следить, чтобы партнёрше было комфортно на паркете. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:2015 | 207:2000 | TEXT | Правило · К3 | 752 | 1152 | 334 | 18 | #060606 | Учитывать ритм и другие пары вокруг. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:2016 | 207:2000 | TEXT | Правило · К4 | 752 | 1208 | 386 | 18 | #060606 | Быть вежливыми и тактичными в общении. | Unbounded / Regular / 12 | F: v2/Text/Ink | opacity=0 |
| 207:2017 | 207:2000 | TEXT | Правило · Д1 | 752 | 1024 | 482 | 18 | #060606 | Принимать приглашения или корректно отклонять их. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2018 | 207:2000 | TEXT | Правило · Д2 | 752 | 1080 | 477 | 18 | #060606 | Следовать темпу и направлению движения партнёра. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2019 | 207:2000 | TEXT | Правило · Д3 | 752 | 1136 | 198 | 18 | #060606 | Соблюдать дресс-код. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2020 | 207:2000 | TEXT | Правило · Д4 | 752 | 1192 | 417 | 18 | #060606 | Проявлять доброжелательность и открытость. | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2021 | 207:2000 | TEXT | Номер 01 | 1320 | 1024 | 24 | 17 | #060606 | 01 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2022 | 207:2000 | TEXT | Номер 02 | 1316 | 1080 | 28 | 17 | #060606 | 02 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2023 | 207:2000 | TEXT | Номер 03 | 1316 | 1136 | 28 | 17 | #060606 | 03 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2024 | 207:2000 | TEXT | Номер 04 | 1316 | 1192 | 28 | 17 | #060606 | 04 | Unbounded / Regular / 12 | F: v2/Text/Ink |  |
| 207:2025 | 207:2000 | TEXT | Роль · Кавалерам | 787 | 1254 | 557 | 102 | #a84c2c | Кавалерам | Old Standard TT / Regular / 128 | F: v2/Accent/Terracotta Deep | opacity=0 |
| 207:2026 | 207:2000 | TEXT | Роль · Дамам | 1000 | 1238 | 344 | 102 | #a84c2c | Дамам | Old Standard TT / Regular / 128 | F: v2/Accent/Terracotta Deep |  |
| 207:2031 | 207:2000 | LINE | + | 688 | 876 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2032 | 207:2000 | LINE | + | 696 | 884 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2033 | 207:2000 | LINE | + | 1392 | 876 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2034 | 207:2000 | LINE | + | 1400 | 884 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2035 | 207:2000 | LINE | + | 688 | 1372 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2036 | 207:2000 | LINE | + | 696 | 1380 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2037 | 207:2000 | LINE | + | 1392 | 1372 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2038 | 207:2000 | LINE | + | 1400 | 1380 | 16 | 0 | stroke #c6c2b6 |  |  |  |  |
| 207:2039 | 207:2000 | TEXT | Финал · строка 1 | 64 | 1412 | 1215 | 120 | #aba79a | Запоминать заранее | Old Standard TT / Regular / 150 | F: v2/Text/Greige 100 |  |
| 207:2040 | 207:2000 | TEXT | Финал · строка 2 (от поля) | 64 | 1532 | 739 | 120 | #aba79a | не нужно — | Old Standard TT / Regular / 150 | F: v2/Text/Greige 100 |  |
| 207:2041 | 207:2000 | TEXT | Финал · продолжение капсом (к правому полю) | 976 | 1616 | 400 | 36 | #c6c2b6 | танцмейстер подскажет на паркете. В моменте, с юмором, без давления. | Unbounded / Regular / 12 | F: v2/Text/Greige Light |  |
| 207:2045 | 207:2000 | FRAME | Зона / Панель | 720 | 924 | 656 | 448 | #00000000 |  |  |  |  |
| 330:4030 | 207:2000 | RECTANGLE | Вкладка · Кавалерам | 720.5 | 876.5 | 327 | 47.5 | stroke #aba79a66 |  |  |  |  |
| 330:4031 | 207:2000 | TEXT | Вкладка · Кавалерам · текст | 744 | 890 | 130 | 20 | #c6c2b6 | Кавалерам | Unbounded / Regular / 16 |  |  |
| 330:4032 | 207:2000 | TEXT | Вкладка · Кавалерам · номер | 1000 | 892 | 24 | 15 | #c6c2b6 | 01 | Unbounded / Regular / 12 |  |  |
| 330:4033 | 207:2000 | RECTANGLE | Вкладка · Дамам · активна | 1048 | 876 | 328 | 48 | #c6c2b6 |  |  |  |  |
| 330:4034 | 207:2000 | TEXT | Вкладка · Дамам · текст | 1072 | 890 | 84 | 20 | #060606 | Дамам | Unbounded / Regular / 16 |  |  |
| 207:2046 | 207:2000 | FRAME | Зона / Вкладка · Кавалерам | 720 | 876 | 328 | 48 | #00000000 |  |  |  |  |
| 207:2047 | 207:2000 | FRAME | Зона / Вкладка · Дамам | 1048 | 876 | 328 | 48 | #00000000 |  |  |  |  |
| 330:4035 | 207:2000 | TEXT | Вкладка · Дамам · номер | 1328 | 892 | 28 | 15 | #060606 | 02 | Unbounded / Regular / 12 |  |  |

## 352:2053 — B — гигант на двух поверхностях

- Absolute x/y: 1840 / 200; w × h: 1440 × 900; fills: #060606; fillStyle: v2/Surface/Ink
- Descendants listed: 17; VECTOR nodes skipped: 0

| id | parent | type | name | x | y | w | h | fill | text | font family / style / size | style (T/F) | visible / opacity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 352:2054 | 352:2053 | FRAME | Половина / Кавалерам | 0 | 0 | 720 | 900 | #222222 |  |  | F: v2/Surface/Slate |  |
| 352:2055 | 352:2054 | RECTANGLE | Фото | 0 | 300 | 720 | 960 | IMAGE + imageHash d27e3cdc2b19e83cfcc7c440b527c493a1c67d4e + FILL + #808080 + #aba599 + #222222 + IMAGE + imageHash d27e3cdc2b19e83cfcc7c440b527c493a1c67d4e + FILL |  |  |  |  |
| 352:2056 | 352:2054 | RECTANGLE | Тон | 0 | 300 | 720 | 960 | GRADIENT_LINEAR {} |  |  |  |  |
| 352:2057 | 352:2054 | RECTANGLE | Поле | 0 | 0 | 720 | 560 | #222222 |  |  | F: v2/Surface/Slate |  |
| 352:2058 | 352:2053 | FRAME | Половина / Дамам | 720 | 0 | 720 | 900 | #653624 |  |  | F: v2/Surface/Terra |  |
| 352:2059 | 352:2058 | RECTANGLE | Фото | 520 | -180 | 1080 | 1440 | IMAGE + imageHash 213f0323ef084a3b2fea15a018a168987a3d95ff + FILL |  |  |  |  |
| 352:2060 | 352:2058 | RECTANGLE | Тон | 720 | 300 | 720 | 960 | GRADIENT_LINEAR {} |  |  |  |  |
| 352:2061 | 352:2058 | RECTANGLE | Поле | 720 | 0 | 720 | 560 | #653624 |  |  | F: v2/Surface/Terra |  |
| 352:2062 | 352:2053 | TEXT | Гигант · Этикет | 64 | 176 | 1008 | 170 | #c6c2b6 | Этикет | Unbounded / Bold / 200 | F: v2/Text/Greige Light |  |
| 352:2065 | 352:2053 | TEXT | Номер 01 | 64 | 432 | 24 | 17 | #c6c2b6 | 01 | Unbounded / Regular / 12 | T: v2/Label/Wide; F: v2/Text/Greige Light |  |
| 352:2066 | 352:2053 | TEXT | Для кого 01 | 128 | 432 | 98 | 18 | #c6c2b6 | Кавалерам | Unbounded / Regular / 12 | T: v2/Body/Text; F: v2/Text/Greige Light |  |
| 352:2067 | 352:2053 | TEXT | Номер 02 | 784 | 432 | 28 | 17 | #c6c2b6 | 02 | Unbounded / Regular / 12 | T: v2/Label/Wide; F: v2/Text/Greige Light |  |
| 352:2068 | 352:2053 | TEXT | Для кого 02 | 848 | 432 | 63 | 18 | #c6c2b6 | Дамам | Unbounded / Regular / 12 | T: v2/Body/Text; F: v2/Text/Greige Light |  |
| 353:2114 | 352:2053 | TEXT | Метка | 64 | 104 | 137 | 15 | #c96a42 | 08 — Этикет | Unbounded / Regular / 11 | T: v2/Label/Section; F: v2/Accent/Terracotta |  |
| 353:2115 | 352:2053 | TEXT | Капс · фрагмент 1 · интро | 784 | 104 | 416 | 54 | #c6c2b6 | Несколько правил, которые делают вечер комфортным для всех. Не строгие нормы — р… | Unbounded / Regular / 12 | T: v2/Body/Text; F: v2/Text/Greige Light |  |
| 353:2116 | 352:2053 | TEXT | Капс · фрагмент 2 · Кавалерам | 64 | 472 | 416 | 36 | #c6c2b6 | Первыми приглашать на танец. Следить, чтобы партнёрше было комфортно. | Unbounded / Regular / 12 | T: v2/Body/Text; F: v2/Text/Greige Light |  |
| 353:2117 | 352:2053 | TEXT | Капс · фрагмент 3 · Дамам | 784 | 472 | 416 | 36 | #c6c2b6 | Принимать приглашения или корректно отклонять их. Следовать темпу партнёра. | Unbounded / Regular / 12 | T: v2/Body/Text; F: v2/Text/Greige Light |  |

## Distinct IMAGE fills

| imageHash | scaleMode | node id | name | size w × h | tree |
|---|---|---|---|---|---|
| 213f0323ef084a3b2fea15a018a168987a3d95ff | FILL | 352:2059 | Фото | 1080 × 1440 | 352:2053 |
| a5d2f3aa78bd67eb9330d59c548d07393126000b | FILL | 330:4029 | Снимок | 1100 × 733 | 207:1958 |
| a5d2f3aa78bd67eb9330d59c548d07393126000b | FILL | 330:4037 | Снимок | 1100 × 733 | 207:2000 |
| d27e3cdc2b19e83cfcc7c440b527c493a1c67d4e | FILL | 352:2055 | Фото | 720 × 960 | 352:2053 |

Distinct imageHash values: 3

