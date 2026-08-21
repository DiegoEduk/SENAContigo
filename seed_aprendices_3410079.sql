-- Script de Inserción de Aprendices y Matrícula para la Ficha 3410079
-- Generado automáticamente desde AprendicesFicha3410079.xlsx

-- [1] Aprendiz: JUAN FERNANDO GONZALEZ MORALES (1004719846)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1004719846', 'JUAN FERNANDO', 'GONZALEZ MORALES', 'juanfego51@gmail.com', '3174767793', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1004719846' ON CONFLICT DO NOTHING;

-- [2] Aprendiz: SAMUEL MUÑOZ ARICAPA (1004734508)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1004734508', 'SAMUEL', 'MUÑOZ ARICAPA', 'samuelarica0@gmail.com', NULL, true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1004734508' ON CONFLICT DO NOTHING;

-- [3] Aprendiz: JOSEPH DAVID RAMIREZ RAMIREZ (1031651707)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1031651707', 'JOSEPH DAVID', 'RAMIREZ RAMIREZ', 'joseph.ramirez@juan23pereira.edu.co', '3017771463', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1031651707' ON CONFLICT DO NOTHING;

-- [4] Aprendiz: DANILO MACHADO CASTRO (1078179889)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1078179889', 'DANILO', 'MACHADO CASTRO', 'danilitodmc@gmail.com', '3103102843', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1078179889' ON CONFLICT DO NOTHING;

-- [5] Aprendiz: JHOIFER ESTEBAN RENTERIA MENA (1078458530)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1078458530', 'JHOIFER ESTEBAN', 'RENTERIA MENA', 'jhoiferenteria@gmail.com', '3105959882', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1078458530' ON CONFLICT DO NOTHING;

-- [6] Aprendiz: ANDRES FELIPE CATAÑO GUEVARA (1088245058)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1088245058', 'ANDRES FELIPE', 'CATAÑO GUEVARA', 'felipecatano89@gmail.com', '3215673261', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1088245058' ON CONFLICT DO NOTHING;

-- [7] Aprendiz: THOMAS PABON CORRALES (1088251982)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1088251982', 'THOMAS', 'PABON CORRALES', 'adrianafcorrales@gmail.com', NULL, true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1088251982' ON CONFLICT DO NOTHING;

-- [8] Aprendiz: FREDY ANDRES HURTADO JORDAN (1088267601)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1088267601', 'FREDY ANDRES', 'HURTADO JORDAN', 'fredyandreshj1989@gmail.com', '3234176845', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1088267601' ON CONFLICT DO NOTHING;

-- [9] Aprendiz: YEINER STIVEN LOPEZ ORJUELA (1089098838)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1089098838', 'YEINER STIVEN', 'LOPEZ ORJUELA', 'yeinerlopez20066@gmail.com', '3136347739', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1089098838' ON CONFLICT DO NOTHING;

-- [10] Aprendiz: JUAN JOSE GOMEZ HURTADO (1089382868)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1089382868', 'JUAN JOSE', 'GOMEZ HURTADO', 'juanjosegomezhurta@gmail.com', '3158850758', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1089382868' ON CONFLICT DO NOTHING;

-- [11] Aprendiz: MARIO ANDRES RAMIREZ TORRES (1089936154)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1089936154', 'MARIO ANDRES', 'RAMIREZ TORRES', 'serfinanciero14@gmail.com', '3136647878', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1089936154' ON CONFLICT DO NOTHING;

-- [12] Aprendiz: SEBASTIAN PARRA ARANGO (1114153189)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('CC', '1114153189', 'SEBASTIAN', 'PARRA ARANGO', 'cuentadeplaystation320@gmail.com', '3126051599', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1114153189' ON CONFLICT DO NOTHING;

-- [13] Aprendiz: JARVIS JOSE ROMERO ARRIETA (5988645)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('PPT', '5988645', 'JARVIS JOSE', 'ROMERO ARRIETA', 'romerojarvis119@gmail.com', NULL, true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '5988645' ON CONFLICT DO NOTHING;

-- [14] Aprendiz: WILLIAM STEVEN HOYOS CASALLAS (1030140920)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1030140920', 'WILLIAM STEVEN', 'HOYOS CASALLAS', 'maru.31450@gmail.com', '3012890595', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1030140920' ON CONFLICT DO NOTHING;

-- [15] Aprendiz: NAIROVY ALEJANDRA HERRERA ARIZA (1030141119)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1030141119', 'NAIROVY ALEJANDRA', 'HERRERA ARIZA', 'nairovyherrera820@gmail.com', '3234457288', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1030141119' ON CONFLICT DO NOTHING;

-- [16] Aprendiz: YURI VANESSA BUENO ANDICA (1059702942)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1059702942', 'YURI VANESSA', 'BUENO ANDICA', 'andicayuribueno@gmail.com', '3166034180', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1059702942' ON CONFLICT DO NOTHING;

-- [17] Aprendiz: EDWIN ANDRES VINASCO GRANADA (1060536494)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1060536494', 'EDWIN ANDRES', 'VINASCO GRANADA', 'Evinasco169@gmail.com', '3126854062', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1060536494' ON CONFLICT DO NOTHING;

-- [18] Aprendiz: EDINSON DANIEL RIVAS MEDINA (1079096138)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1079096138', 'EDINSON DANIEL', 'RIVAS MEDINA', 'edinsonrivas834@gmail.com', '3138055276', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1079096138' ON CONFLICT DO NOTHING;

-- [19] Aprendiz: EDER HUMBERTO OTALVARO LADINO (1085718712)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1085718712', 'EDER HUMBERTO', 'OTALVARO LADINO', 'betootalvaro31@gmail.com', NULL, true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1085718712' ON CONFLICT DO NOTHING;

-- [20] Aprendiz: ZARA MUÑOZ MONSALVE (1088277552)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1088277552', 'ZARA', 'MUÑOZ MONSALVE', 'munozzara0@gmail.com', '3233032131', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1088277552' ON CONFLICT DO NOTHING;

-- [21] Aprendiz: CARLOS HANSK GOMEZ CARDONA (1088830333)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1088830333', 'CARLOS HANSK', 'GOMEZ CARDONA', 'carlosgomezcardona05@gmail.com', '3207654476', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1088830333' ON CONFLICT DO NOTHING;

-- [22] Aprendiz: KEVIN ZEA TELLEZ (1089384562)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1089384562', 'KEVIN', 'ZEA TELLEZ', 'kevinzeatellez@gmail.com', '3184611554', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1089384562' ON CONFLICT DO NOTHING;

-- [23] Aprendiz: SANTIAGO RAMIREZ CARMONA (1089603479)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1089603479', 'SANTIAGO', 'RAMIREZ CARMONA', 'santyrami.0706@gmail.com', NULL, true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1089603479' ON CONFLICT DO NOTHING;

-- [24] Aprendiz: ESTIVEN ALEXANDER HIGUITA CORDERO (1090275705)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1090275705', 'ESTIVEN ALEXANDER', 'HIGUITA CORDERO', 'estivemhiguta0901@gmail.com', NULL, true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1090275705' ON CONFLICT DO NOTHING;

-- [25] Aprendiz: BRAHIAN CAMILO HENAO DUQUE (1091274106)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1091274106', 'BRAHIAN CAMILO', 'HENAO DUQUE', 'henaoduquecamilo@gmail.com', '3170985135', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1091274106' ON CONFLICT DO NOTHING;

-- [26] Aprendiz: LAURA MARIANA RENDON GUTIERREZ (1116724388)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1116724388', 'LAURA MARIANA', 'RENDON GUTIERREZ', 'gutierrezgilbia@gmail.com', '3118289663', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1116724388' ON CONFLICT DO NOTHING;

-- [27] Aprendiz: FRENMAR ELIANA MAYORA MERCADO (1127609171)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1127609171', 'FRENMAR ELIANA', 'MAYORA MERCADO', 'frenmarEliana@gmail.com', '3044936600', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1127609171' ON CONFLICT DO NOTHING;

-- [28] Aprendiz: BRAHIAM ABAD JIMENEZ FLORES (1127920682)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1127920682', 'BRAHIAM ABAD', 'JIMENEZ FLORES', 'probrahiamyt@gmail.com', '3227793988', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1127920682' ON CONFLICT DO NOTHING;

-- [29] Aprendiz: SANTIAGO ESTRADA CARMONA (1137061173)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1137061173', 'SANTIAGO', 'ESTRADA CARMONA', 'estradasantiago407@gmail.com', '3134587731', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1137061173' ON CONFLICT DO NOTHING;

-- [30] Aprendiz: SAMUEL OCAMPO VARGAS (1142516751)
INSERT INTO aprendices (tipo_documento, numero_documento, nombres, apellidos, correo, celular, activo) VALUES ('TI', '1142516751', 'SAMUEL', 'OCAMPO VARGAS', 'ocampolvargas1905@gmail.com', '3136238387', true) ON CONFLICT (numero_documento) DO UPDATE SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos, correo = EXCLUDED.correo, celular = EXCLUDED.celular;

INSERT INTO matriculas (aprendiz_id, ficha_id, estado_matricula) SELECT id, '3410079', 'En formación' FROM aprendices WHERE numero_documento = '1142516751' ON CONFLICT DO NOTHING;
