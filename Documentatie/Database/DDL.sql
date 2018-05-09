-- MySQL Script generated by MySQL Workbench
-- Sun Mar 25 16:20:38 2018
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering
-- -----------------------------------------------------
-- Schema kiwibank
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `kiwibank` DEFAULT CHARACTER SET latin1 ;
USE `kiwibank` ;
-- -----------------------------------------------------
-- Table `kiwibank`.`gebruikers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kiwibank`.`gebruikers` (
  `klantid` INT(11) NOT NULL AUTO_INCREMENT,
  `naam` VARCHAR(45) NOT NULL,
  `pincode` VARCHAR(128) NOT NULL,
  `tagid` VARCHAR(128) NOT NULL,
  `rol` VARCHAR(64) NOT NULL,
  `geblokkeerd` VARCHAR(3) NOT NULL,
  `pogingen` VARCHAR(45) NOT NULL DEFAULT '0',
  PRIMARY KEY (`klantid`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = latin1;
-- -----------------------------------------------------
-- Table `kiwibank`.`logboek`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kiwibank`.`logboek` (
  `logboekid` INT(11) NOT NULL AUTO_INCREMENT,
  `datum` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `actie` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`logboekid`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1;
-- -----------------------------------------------------
-- Table `kiwibank`.`rekeningen`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kiwibank`.`rekeningen` (
  `rekeningnr` INT(11) NOT NULL AUTO_INCREMENT,
  `klantid` INT(11) NOT NULL,
  `saldo` VARCHAR(45) NOT NULL DEFAULT '0',
  PRIMARY KEY (`rekeningnr`),
  INDEX `klantid_idx` (`klantid` ASC),
  CONSTRAINT `klantid`
    FOREIGN KEY (`klantid`)
    REFERENCES `kiwibank`.`gebruikers` (`klantid`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = latin1;
-- -----------------------------------------------------
-- Table `kiwibank`.`transacties`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kiwibank`.`transacties` (
  `transactieid` INT(11) NOT NULL AUTO_INCREMENT,
  `klantid` INT(11) NOT NULL,
  `vanrekeningnr` INT(11) NOT NULL,
  `naarrekeningnr` INT(11) NULL DEFAULT NULL,
  `transactietype` VARCHAR(45) NOT NULL,
  `bedrag` VARCHAR(45) NOT NULL,
  `omschrijving` VARCHAR(45) NOT NULL,
  `datum` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`transactieid`),
  INDEX `klantid_idx` (`klantid` ASC),
  INDEX `rekeningnr_idx` (`vanrekeningnr` ASC),
  CONSTRAINT `klantid`
    FOREIGN KEY (`klantid`)
    REFERENCES `kiwibank`.`gebruikers` (`klantid`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `rekeningnr`
    FOREIGN KEY (`vanrekeningnr`)
    REFERENCES `kiwibank`.`rekeningen` (`rekeningnr`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;
