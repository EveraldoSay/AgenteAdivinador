-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         11.7.2-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para agenteadivinador
CREATE DATABASE IF NOT EXISTS `agenteadivinador` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci */;
USE `agenteadivinador`;

-- Volcando estructura para tabla agenteadivinador.jugadores
CREATE TABLE IF NOT EXISTS `jugadores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `mundial_id` int(11) NOT NULL,
  `posicion_id` int(11) NOT NULL,
  `titular` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `mundial_id` (`mundial_id`),
  KEY `posicion_id` (`posicion_id`),
  CONSTRAINT `jugadores_ibfk_1` FOREIGN KEY (`mundial_id`) REFERENCES `mundiales` (`id`),
  CONSTRAINT `jugadores_ibfk_2` FOREIGN KEY (`posicion_id`) REFERENCES `posiciones` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=224 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Volcando datos para la tabla agenteadivinador.jugadores: ~223 rows (aproximadamente)
REPLACE INTO `jugadores` (`id`, `nombre`, `mundial_id`, `posicion_id`, `titular`) VALUES
	(1, 'Gilmar', 1, 1, 1),
	(2, 'Djalma Santos', 1, 2, 1),
	(3, 'Nilton Santos', 1, 2, 1),
	(4, 'Bellini', 1, 2, 1),
	(5, 'Orlando', 1, 2, 1),
	(6, 'Zito', 1, 3, 1),
	(7, 'Didi', 1, 3, 1),
	(8, 'Garrincha', 1, 4, 1),
	(9, 'Pelé', 1, 4, 1),
	(10, 'Vavá', 1, 4, 1),
	(11, 'Zagallo', 1, 4, 1),
	(12, 'Castilho', 1, 1, 0),
	(13, 'Mauro', 1, 2, 0),
	(14, 'Dino Sani', 1, 3, 0),
	(15, 'Joel', 1, 4, 0),
	(16, 'Moacir', 1, 3, 0),
	(17, 'Gilmar', 2, 1, 1),
	(18, 'Djalma Santos', 2, 2, 1),
	(19, 'Mauro', 2, 2, 1),
	(20, 'Zózimo', 2, 2, 1),
	(21, 'Nilton Santos', 2, 2, 1),
	(22, 'Zito', 2, 3, 1),
	(23, 'Didi', 2, 3, 1),
	(24, 'Garrincha', 2, 4, 1),
	(25, 'Amarildo', 2, 4, 1),
	(26, 'Vavá', 2, 4, 1),
	(27, 'Zagallo', 2, 4, 1),
	(28, 'Castilho', 2, 1, 0),
	(29, 'Altair', 2, 2, 0),
	(30, 'Mengálvio', 2, 3, 0),
	(31, 'Jair da Costa', 2, 4, 0),
	(32, 'Félix', 3, 1, 1),
	(33, 'Carlos Alberto', 3, 2, 1),
	(34, 'Brito', 3, 2, 1),
	(35, 'Piazza', 3, 2, 1),
	(36, 'Everaldo', 3, 2, 1),
	(37, 'Clodoaldo', 3, 3, 1),
	(38, 'Gerson', 3, 3, 1),
	(39, 'Jairzinho', 3, 4, 1),
	(40, 'Pelé', 3, 4, 1),
	(41, 'Tostão', 3, 4, 1),
	(42, 'Rivelino', 3, 4, 1),
	(43, 'Leão', 3, 1, 0),
	(44, 'Fontana', 3, 2, 0),
	(45, 'Paulo Cézar', 3, 3, 0),
	(46, 'Edu', 3, 4, 0),
	(47, 'Roberto', 3, 2, 0),
	(48, 'Taffarel', 4, 1, 1),
	(49, 'Jorginho', 4, 2, 1),
	(50, 'Aldair', 4, 2, 1),
	(51, 'Márcio Santos', 4, 2, 1),
	(52, 'Branco', 4, 2, 1),
	(53, 'Dunga', 4, 3, 1),
	(54, 'Mauro Silva', 4, 3, 1),
	(55, 'Bebeto', 4, 4, 1),
	(56, 'Romário', 4, 4, 1),
	(57, 'Mazinho', 4, 4, 1),
	(58, 'Zinho', 4, 4, 1),
	(59, 'Gilmar', 4, 1, 0),
	(60, 'Cafú', 4, 2, 0),
	(61, 'Ronaldo', 4, 4, 0),
	(62, 'Viola', 4, 4, 0),
	(63, 'Raí', 4, 3, 0),
	(64, 'Marcos', 5, 1, 1),
	(65, 'Cafú', 5, 2, 1),
	(66, 'Lúcio', 5, 2, 1),
	(67, 'Edmílson', 5, 2, 1),
	(68, 'Roque Júnior', 5, 2, 1),
	(69, 'Roberto Carlos', 5, 2, 1),
	(70, 'Gilberto Silva', 5, 3, 1),
	(71, 'Kleberson', 5, 3, 1),
	(72, 'Rivaldo', 5, 4, 1),
	(73, 'Ronaldo', 5, 4, 1),
	(74, 'Ronaldinho', 5, 4, 1),
	(75, 'Dida', 5, 1, 0),
	(76, 'Belletti', 5, 2, 0),
	(77, 'Ricardinho', 5, 3, 0),
	(78, 'Edílson', 5, 4, 0),
	(79, 'Juninho Paulista', 5, 3, 0),
	(80, 'Toni Turek', 6, 1, 1),
	(81, 'Jupp Posipal', 6, 2, 1),
	(82, 'Werner Liebrich', 6, 2, 1),
	(83, 'Josef Posipal', 6, 2, 1),
	(84, 'Horst Eckel', 6, 3, 1),
	(85, 'Karl Mai', 6, 3, 1),
	(86, 'Fritz Walter', 6, 3, 1),
	(87, 'Helmut Rahn', 6, 4, 1),
	(88, 'Hans Schäfer', 6, 4, 1),
	(89, 'Max Morlock', 6, 4, 1),
	(90, 'Ottmar Walter', 6, 4, 1),
	(91, 'Heinrich Kwiatkowski', 6, 1, 0),
	(92, 'Richard Herrmann', 6, 3, 0),
	(93, 'Alfred Pfaff', 6, 4, 0),
	(94, 'Sepp Maier', 7, 1, 1),
	(95, 'Paul Breitner', 7, 2, 1),
	(96, 'Franz Beckenbauer', 7, 2, 1),
	(97, 'Berti Vogts', 7, 2, 1),
	(98, 'Schwarzenbeck', 7, 2, 1),
	(99, 'Wolfgang Overath', 7, 3, 1),
	(100, 'Rainer Bonhof', 7, 3, 1),
	(101, 'Uli Hoeneß', 7, 3, 1),
	(102, 'Jürgen Grabowski', 7, 4, 1),
	(103, 'Gerd Müller', 7, 4, 1),
	(104, 'Bernd Hölzenbein', 7, 4, 1),
	(105, 'Norbert Nigbur', 7, 1, 0),
	(106, 'Helmut Kremers', 7, 2, 0),
	(107, 'Dietmar Danner', 7, 3, 0),
	(108, 'Bodo Illgner', 8, 1, 1),
	(109, 'Andreas Brehme', 8, 2, 1),
	(110, 'Klaus Augenthaler', 8, 2, 1),
	(111, 'Jürgen Kohler', 8, 2, 1),
	(112, 'Lothar Matthäus', 8, 3, 1),
	(113, 'Guido Buchwald', 8, 3, 1),
	(114, 'Thomas Häßler', 8, 3, 1),
	(115, 'Rudi Völler', 8, 4, 1),
	(116, 'Jürgen Klinsmann', 8, 4, 1),
	(117, 'Pierre Littbarski', 8, 4, 1),
	(118, 'Andreas Möller', 8, 4, 1),
	(119, 'Raimond Aumann', 8, 1, 0),
	(120, 'Stefan Reuter', 8, 2, 0),
	(121, 'Olaf Thon', 8, 3, 0),
	(122, 'Manuel Neuer', 9, 1, 1),
	(123, 'Philipp Lahm', 9, 2, 1),
	(124, 'Mats Hummels', 9, 2, 1),
	(125, 'Jérôme Boateng', 9, 2, 1),
	(126, 'Benedikt Höwedes', 9, 2, 1),
	(127, 'Bastian Schweinsteiger', 9, 3, 1),
	(128, 'Toni Kroos', 9, 3, 1),
	(129, 'Sami Khedira', 9, 3, 1),
	(130, 'Thomas Müller', 9, 4, 1),
	(131, 'Miroslav Klose', 9, 4, 1),
	(132, 'Mesut Özil', 9, 4, 1),
	(133, 'Roman Weidenfeller', 9, 1, 0),
	(134, 'Erik Durm', 9, 2, 0),
	(135, 'André Schürrle', 9, 4, 0),
	(136, 'Mario Götze', 9, 4, 0),
	(137, 'Dino Zoff', 10, 1, 1),
	(138, 'Claudio Gentile', 10, 2, 1),
	(139, 'Gaetano Scirea', 10, 2, 1),
	(140, 'Fulvio Collovati', 10, 2, 1),
	(141, 'Marco Tardelli', 10, 3, 1),
	(142, 'Gabriele Oriali', 10, 3, 1),
	(143, 'Bruno Conti', 10, 3, 1),
	(144, 'Paolo Rossi', 10, 4, 1),
	(145, 'Francesco Graziani', 10, 4, 1),
	(146, 'Antonio Cabrini', 10, 4, 1),
	(147, 'Giancarlo Antognoni', 10, 4, 1),
	(148, 'Ivano Bordon', 10, 1, 0),
	(149, 'Giuseppe Bergomi', 10, 2, 0),
	(150, 'Franco Causio', 10, 3, 0),
	(151, 'Gianluigi Buffon', 11, 1, 1),
	(152, 'Fabio Cannavaro', 11, 2, 1),
	(153, 'Marco Materazzi', 11, 2, 1),
	(154, 'Gianluca Zambrotta', 11, 2, 1),
	(155, 'Fabio Grosso', 11, 2, 1),
	(156, 'Andrea Pirlo', 11, 3, 1),
	(157, 'Gennaro Gattuso', 11, 3, 1),
	(158, 'Daniele De Rossi', 11, 3, 1),
	(159, 'Francesco Totti', 11, 4, 1),
	(160, 'Luca Toni', 11, 4, 1),
	(161, 'Alessandro Del Piero', 11, 4, 1),
	(162, 'Angelo Peruzzi', 11, 1, 0),
	(163, 'Simone Barone', 11, 3, 0),
	(164, 'Vincenzo Iaquinta', 11, 4, 0),
	(165, 'Emiliano Martínez', 12, 1, 1),
	(166, 'Nicolás Otamendi', 12, 2, 1),
	(167, 'Cristian Romero', 12, 2, 1),
	(168, 'Lisandro Martínez', 12, 2, 1),
	(169, 'Rodrigo De Paul', 12, 3, 1),
	(170, 'Enzo Fernández', 12, 3, 1),
	(171, 'Alexis Mac Allister', 12, 3, 1),
	(172, 'Lionel Messi', 12, 4, 1),
	(173, 'Julián Álvarez', 12, 4, 1),
	(174, 'Ángel Di María', 12, 4, 1),
	(175, 'Franco Armani', 12, 1, 0),
	(176, 'Nahuel Molina', 12, 2, 0),
	(177, 'Leandro Paredes', 12, 3, 0),
	(178, 'Paulo Dybala', 12, 4, 0),
	(179, 'Lautaro Martínez', 12, 4, 0),
	(180, 'Hugo Lloris', 13, 1, 1),
	(181, 'Benjamin Pavard', 13, 2, 1),
	(182, 'Raphaël Varane', 13, 2, 1),
	(183, 'Samuel Umtiti', 13, 2, 1),
	(184, 'Lucas Hernández', 13, 2, 1),
	(185, 'N\'Golo Kanté', 13, 3, 1),
	(186, 'Paul Pogba', 13, 3, 1),
	(187, 'Blaise Matuidi', 13, 3, 1),
	(188, 'Antoine Griezmann', 13, 4, 1),
	(189, 'Kylian Mbappé', 13, 4, 1),
	(190, 'Olivier Giroud', 13, 4, 1),
	(191, 'Steve Mandanda', 13, 1, 0),
	(192, 'Presnel Kimpembe', 13, 2, 0),
	(193, 'Corentin Tolisso', 13, 3, 0),
	(194, 'Ousmane Dembélé', 13, 4, 0),
	(195, 'Iker Casillas', 14, 1, 1),
	(196, 'Sergio Ramos', 14, 2, 1),
	(197, 'Gerard Piqué', 14, 2, 1),
	(198, 'Carles Puyol', 14, 2, 1),
	(199, 'Joan Capdevila', 14, 2, 1),
	(200, 'Xavi Hernández', 14, 3, 1),
	(201, 'Sergio Busquets', 14, 3, 1),
	(202, 'Andrés Iniesta', 14, 3, 1),
	(203, 'Pedro Rodríguez', 14, 4, 1),
	(204, 'David Villa', 14, 4, 1),
	(205, 'Xabi Alonso', 14, 4, 1),
	(206, 'Pepe Reina', 14, 1, 0),
	(207, 'Cesc Fàbregas', 14, 3, 0),
	(208, 'Fernando Torres', 14, 4, 0),
	(209, 'Juan Mata', 14, 4, 0),
	(210, 'Gordon Banks', 15, 1, 1),
	(211, 'George Cohen', 15, 2, 1),
	(212, 'Bobby Moore', 15, 2, 1),
	(213, 'Jack Charlton', 15, 2, 1),
	(214, 'Ray Wilson', 15, 2, 1),
	(215, 'Nobby Stiles', 15, 3, 1),
	(216, 'Alan Ball', 15, 3, 1),
	(217, 'Bobby Charlton', 15, 3, 1),
	(218, 'Geoff Hurst', 15, 4, 1),
	(219, 'Roger Hunt', 15, 4, 1),
	(220, 'Martin Peters', 15, 4, 1),
	(221, 'Ron Springett', 15, 1, 0),
	(222, 'Jimmy Greaves', 15, 4, 0),
	(223, 'Ron Flowers', 15, 3, 0);

-- Volcando estructura para tabla agenteadivinador.mundiales
CREATE TABLE IF NOT EXISTS `mundiales` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `anio` int(11) NOT NULL,
  `pais_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `anio` (`anio`),
  KEY `pais_id` (`pais_id`),
  CONSTRAINT `mundiales_ibfk_1` FOREIGN KEY (`pais_id`) REFERENCES `paises` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Volcando datos para la tabla agenteadivinador.mundiales: ~15 rows (aproximadamente)
REPLACE INTO `mundiales` (`id`, `anio`, `pais_id`) VALUES
	(1, 1958, 1),
	(2, 1962, 1),
	(3, 1970, 1),
	(4, 1994, 1),
	(5, 2002, 1),
	(6, 1954, 2),
	(7, 1974, 2),
	(8, 1990, 2),
	(9, 2014, 2),
	(10, 1982, 3),
	(11, 2006, 3),
	(12, 2022, 4),
	(13, 2018, 5),
	(14, 2010, 6),
	(15, 1966, 7);

-- Volcando estructura para tabla agenteadivinador.paises
CREATE TABLE IF NOT EXISTS `paises` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Volcando datos para la tabla agenteadivinador.paises: ~7 rows (aproximadamente)
REPLACE INTO `paises` (`id`, `nombre`) VALUES
	(1, 'BRASIL'),
	(2, 'ALEMANIA'),
	(3, 'ITALIA'),
	(4, 'ARGENTINA'),
	(5, 'FRANCIA'),
	(6, 'ESPAÑA'),
	(7, 'INGLATERRA');

-- Volcando estructura para tabla agenteadivinador.posiciones
CREATE TABLE IF NOT EXISTS `posiciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `abreviatura` varchar(5) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `abreviatura` (`abreviatura`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- Volcando datos para la tabla agenteadivinador.posiciones: ~4 rows (aproximadamente)
REPLACE INTO `posiciones` (`id`, `nombre`, `abreviatura`) VALUES
	(1, 'Portero', 'POR'),
	(2, 'Defensa', 'DEF'),
	(3, 'Mediocampista', 'MED'),
	(4, 'Delantero', 'DEL');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
