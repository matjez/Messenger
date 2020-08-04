-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Czas generowania: 04 Sie 2020, 23:05
-- Wersja serwera: 10.1.35-MariaDB
-- Wersja PHP: 7.2.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Baza danych: `messenger`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `contacts`
--

CREATE TABLE `contacts` (
  `contact_id` int(16) NOT NULL,
  `user_id` int(16) NOT NULL,
  `friend_id` int(16) NOT NULL,
  `contact_name` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci;

--
-- Zrzut danych tabeli `contacts`
--

INSERT INTO `contacts` (`contact_id`, `user_id`, `friend_id`, `contact_name`) VALUES
(1, 1, 2, 1),
(2, 2, 1, 1);

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `invites`
--

CREATE TABLE `invites` (
  `invite_id` int(16) NOT NULL,
  `user_id` int(16) NOT NULL,
  `invited_user_id` int(16) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` int(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci;


-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `password_change`
--

CREATE TABLE `password_change` (
  `change_id` varchar(32) COLLATE utf8_polish_ci NOT NULL,
  `user_id` int(32) NOT NULL,
  `status` int(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci;


-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `users`
--

CREATE TABLE `users` (
  `user_id` int(16) NOT NULL,
  `login` varchar(32) COLLATE utf8_polish_ci NOT NULL,
  `password` varchar(64) COLLATE utf8_polish_ci NOT NULL,
  `email` varchar(64) COLLATE utf8_polish_ci NOT NULL,
  `phone_number` varchar(15) COLLATE utf8_polish_ci NOT NULL,
  `first_name` varchar(32) COLLATE utf8_polish_ci NOT NULL,
  `second_name` varchar(32) COLLATE utf8_polish_ci DEFAULT NULL,
  `last_name` varchar(48) COLLATE utf8_polish_ci NOT NULL,
  `acc_type` varchar(16) COLLATE utf8_polish_ci NOT NULL,
  `active` varchar(16) COLLATE utf8_polish_ci NOT NULL,
  `date_of_birth` date NOT NULL,
  `date_of_create` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `token` text COLLATE utf8_polish_ci NOT NULL,
  `description` text COLLATE utf8_polish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci;

--
-- Zrzut danych tabeli `users`
--

INSERT INTO `users` (`user_id`, `login`, `password`, `email`, `phone_number`, `first_name`, `second_name`, `last_name`, `acc_type`, `active`, `date_of_birth`, `date_of_create`, `token`, `description`) VALUES
(1, 'test1', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'test@gmail.com', '456456456', 'Adadr', NULL, 'Douglas', 'user', '1', '2000-02-22', '2019-09-17 22:00:00', '5FxZ2LkA7ux7kBzFEPtBmi9aEwqAYkcc', 'Some description'),
(2, 'test2', 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', 'test2@gmail.com', '456456456', 'John', 'Jack', 'Hack', 'user', '1', '0000-00-00', '2019-09-17 22:00:00', 'rm2d1w3MgISBDKZl02g49lM8bu3g3ZIx', 'Some description2');

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`contact_id`);

--
-- Indeksy dla tabeli `invites`
--
ALTER TABLE `invites`
  ADD PRIMARY KEY (`invite_id`);

--
-- Indeksy dla tabeli `password_change`
--
ALTER TABLE `password_change`
  ADD PRIMARY KEY (`change_id`);

--
-- Indeksy dla tabeli `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT dla tabeli `contacts`
--
ALTER TABLE `contacts`
  MODIFY `contact_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT dla tabeli `invites`
--
ALTER TABLE `invites`
  MODIFY `invite_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT dla tabeli `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
