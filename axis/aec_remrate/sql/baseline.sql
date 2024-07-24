-- MySQL dump 10.13  Distrib 8.0.32, for macos13.0 (arm64)
--
-- Host: 127.0.0.1    Database: remrate
-- ------------------------------------------------------
-- Server version	5.5.5-10.9.3-MariaDB-1:10.9.3+maria~ubu2204-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `remrate`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `remrate` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `remrate`;

--
-- Table structure for table `AGWall`
--

DROP TABLE IF EXISTS `AGWall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AGWall` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZAGNAME` varchar(31) DEFAULT NULL,
  `FAGAREA` double DEFAULT NULL,
  `NAGLOC` double DEFAULT NULL,
  `NAGCOL` double DEFAULT NULL,
  `FAGUO` double DEFAULT NULL,
  `LAGWALLTNO` double DEFAULT NULL,
  `SAGRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `AccMeas`
--

DROP TABLE IF EXISTS `AccMeas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AccMeas` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LAMAMNO` int(11) NOT NULL,
  `LAMCRNO` int(11) NOT NULL,
  `LAMPARNO` double DEFAULT NULL,
  `NAMMULT` double DEFAULT NULL,
  `SAMCOMP` varchar(51) DEFAULT NULL,
  `SAMEXIST` varchar(51) DEFAULT NULL,
  `SAMPROP` varchar(51) DEFAULT NULL,
  `SAMTREAT` varchar(121) DEFAULT NULL,
  `SAMTREATD` varchar(121) DEFAULT NULL,
  `FAMLIFE` double DEFAULT NULL,
  `FAMCOST` double DEFAULT NULL,
  `FAMYRSAV` double DEFAULT NULL,
  `FAMSIR` double DEFAULT NULL,
  `FAMPVSAV` double DEFAULT NULL,
  `FAMSP` double DEFAULT NULL,
  `FAMRATING` double DEFAULT NULL,
  `FAM1YCF` double DEFAULT NULL,
  PRIMARY KEY (`LAMAMNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=2500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ActSolar`
--

DROP TABLE IF EXISTS `ActSolar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ActSolar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `NASSYSTEM` double DEFAULT NULL,
  `NASLOOP` double DEFAULT NULL,
  `FASCOLAREA` double DEFAULT NULL,
  `NASOR` double DEFAULT NULL,
  `NASTILT` double DEFAULT NULL,
  `NASSPECS` double DEFAULT NULL,
  `FASSTGVOL` double DEFAULT NULL,
  `SASRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=3500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `AddMass`
--

DROP TABLE IF EXISTS `AddMass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AddMass` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZAMNAME` varchar(31) DEFAULT NULL,
  `FAMAREA` double DEFAULT NULL,
  `NAMLOC` double DEFAULT NULL,
  `NAMTYPE` double DEFAULT NULL,
  `FAMTHK` double DEFAULT NULL,
  `SAMRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=4500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `AshpType`
--

DROP TABLE IF EXISTS `AshpType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AshpType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LASTASTNO` double DEFAULT NULL,
  `SASTTYPE` varchar(31) DEFAULT NULL,
  `NASTFUEL` double DEFAULT NULL,
  `FASTHCAP47` double DEFAULT NULL,
  `FASTHEFF` double DEFAULT NULL,
  `NASTHEFFU` double DEFAULT NULL,
  `FASTCCAP` double DEFAULT NULL,
  `FASTCEFF` double DEFAULT NULL,
  `NASTCEFFU` double DEFAULT NULL,
  `FASTSHF` double DEFAULT NULL,
  `NASTDSHTR` double DEFAULT NULL,
  `SASTNOTE` varchar(255) DEFAULT NULL,
  `FASTBKUPCP` double DEFAULT NULL,
  `NASTFNCTRL` int(11) DEFAULT 0,
  `NASTFNDEF` int(11) DEFAULT 0,
  `FASTFNHSPD` double DEFAULT 0,
  `FASTFNLSPD` double DEFAULT 0,
  `FASTHCAP17` double DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=5500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BldgInfo`
--

DROP TABLE IF EXISTS `BldgInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BldgInfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `FBIVOLUME` double DEFAULT NULL,
  `FBIACOND` double DEFAULT NULL,
  `NBIHTYPE` double DEFAULT NULL,
  `NBILTYPE` double DEFAULT NULL,
  `NBISTORIES` double DEFAULT NULL,
  `NBIFTYPE` double DEFAULT NULL,
  `NBIBEDS` double DEFAULT NULL,
  `NBIUNITS` double DEFAULT NULL,
  `SBIRATENO` varchar(31) DEFAULT NULL,
  `NBICTYPE` double DEFAULT NULL,
  `NBIYEARBLT` int(11) DEFAULT 0,
  `NBITHBNDRY` int(11) DEFAULT NULL,
  `NBISTORYWCB` int(11) DEFAULT NULL,
  `NBIINFLTVOL` int(255) DEFAULT NULL,
  `nBITotalStories` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=6500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Block`
--

DROP TABLE IF EXISTS `Block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Block` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLSRNO` int(11) NOT NULL,
  `FBLBLCKMAX` double DEFAULT NULL,
  `FBLRATE` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=7500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BuildRun`
--

DROP TABLE IF EXISTS `BuildRun`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BuildRun` (
  `LBLDGRUNNO` int(11) NOT NULL,
  `SBRDATE` varchar(31) DEFAULT NULL,
  `SBRPROGVER` varchar(40) DEFAULT NULL,
  `SBRRATENO` varchar(31) DEFAULT NULL,
  `SBRFLAG` varchar(30) DEFAULT NULL,
  `LBREXPTPE` double DEFAULT NULL,
  `NINSTANCE` double DEFAULT NULL,
  `SBRPROGFLVR` varchar(255) DEFAULT NULL,
  `SBRUDRNAME` varchar(255) DEFAULT NULL,
  `SBRUDRCHK` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`LBLDGRUNNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=8500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Building`
--

DROP TABLE IF EXISTS `Building`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Building` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SBUBLDGNAM` varchar(255) DEFAULT NULL,
  `SBURATENO` varchar(31) DEFAULT NULL,
  `NBUBLGTYPE` double DEFAULT NULL,
  `FCEILATRO` double DEFAULT NULL,
  `FCEILATAR` double DEFAULT NULL,
  `FCEILCARO` double DEFAULT NULL,
  `FCEILCAAR` double DEFAULT NULL,
  `FAGWCORO` double DEFAULT NULL,
  `FAGWCOAR` double DEFAULT NULL,
  `FAGWBORO` double DEFAULT NULL,
  `FAGWBOAR` double DEFAULT NULL,
  `FJOICORO` double DEFAULT NULL,
  `FJOICOAR` double DEFAULT NULL,
  `FJOIBORO` double DEFAULT NULL,
  `FJOIBOAR` double DEFAULT NULL,
  `FFNDCORO` double DEFAULT NULL,
  `FFNDCOAR` double DEFAULT NULL,
  `FFNDBORO` double DEFAULT NULL,
  `FFNDBOAR` double DEFAULT NULL,
  `FFRFCARO` double DEFAULT NULL,
  `FFRFCAAR` double DEFAULT NULL,
  `FWINCORO` double DEFAULT NULL,
  `FWINCOAR` double DEFAULT NULL,
  `FSKYCORO` double DEFAULT NULL,
  `FSKYCOAR` double DEFAULT NULL,
  `FDORCORO` double DEFAULT NULL,
  `FDORCOAR` double DEFAULT NULL,
  `FAMTHDRY` double DEFAULT NULL,
  `FWINWALL` double DEFAULT NULL,
  `FWINFLOOR` double DEFAULT NULL,
  `sNotes` longtext DEFAULT NULL,
  `SCEILATDOM` varchar(255) DEFAULT NULL,
  `SCEILSADOM` varchar(255) DEFAULT NULL,
  `SCEILCADOM` varchar(255) DEFAULT NULL,
  `SAGWDOM` varchar(255) DEFAULT NULL,
  `SFNDWDOM` varchar(255) DEFAULT NULL,
  `SSLABDOM` varchar(255) DEFAULT NULL,
  `SFRFDOM` varchar(255) DEFAULT NULL,
  `SWINDOM` varchar(255) DEFAULT NULL,
  `SDUCTDOM` varchar(255) DEFAULT NULL,
  `SHTGDOM` varchar(255) DEFAULT NULL,
  `SCLGDOM` varchar(255) DEFAULT NULL,
  `SDHWDOM` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`LBLDGNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=9500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CeilType`
--

DROP TABLE IF EXISTS `CeilType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CeilType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LCTCTNO` int(11) NOT NULL,
  `FCTGYPTHK` double DEFAULT NULL,
  `FCTRFTRWDT` double DEFAULT NULL,
  `FCTRFTRHGT` double DEFAULT NULL,
  `FCTRFTRSPC` double DEFAULT NULL,
  `FCTCONTINS` double DEFAULT NULL,
  `FCTCVTYINS` double DEFAULT NULL,
  `FCTCINSTHK` double DEFAULT NULL,
  `NCTCEILTYP` double DEFAULT NULL,
  `LCTCOMPNO` double DEFAULT NULL,
  `BCTQFVALID` double DEFAULT NULL,
  `NCTINSTYP` int(11) DEFAULT 0,
  `FCTUNRDEP` double DEFAULT 0,
  `FCTUNRRVL` double DEFAULT 0,
  `FCTCLGWID` double DEFAULT 0,
  `FCTCLGRSE` double DEFAULT 0,
  `FCTTRSHGT` double DEFAULT 0,
  `FCTHELHGT` double DEFAULT 0,
  `FCTVNTSPC` double DEFAULT 0,
  `NCTQFTYP` int(11) DEFAULT 0,
  `FCTFF` double DEFAULT NULL,
  `BCTDFLTFF` int(11) DEFAULT NULL,
  `SCTNOTE` varchar(255) DEFAULT NULL,
  `NCTINSGRDE` int(11) DEFAULT NULL,
  PRIMARY KEY (`LCTCTNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=10500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ClgType`
--

DROP TABLE IF EXISTS `ClgType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ClgType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LCETCETNO` double DEFAULT NULL,
  `SCETTYPE` varchar(31) DEFAULT NULL,
  `NCETSYSTTP` double DEFAULT NULL,
  `NCETFUELTP` double DEFAULT NULL,
  `FCETRATCAP` double DEFAULT NULL,
  `FCETEFF` double DEFAULT NULL,
  `FCETSHF` double DEFAULT NULL,
  `NCETEFFUTP` double DEFAULT NULL,
  `NCETDSHTR` double DEFAULT NULL,
  `NCETFNCTRL` int(11) DEFAULT 0,
  `NCETFNDEF` int(11) DEFAULT 0,
  `FCETFNHSPD` double DEFAULT 0,
  `FCETFNLSPD` double DEFAULT 0,
  `SCETNOTE` varchar(255) DEFAULT NULL,
  `FCETFANPWR` double DEFAULT 0,
  `FCETPMPENG` double DEFAULT 0,
  `NCETPMPTYP` int(11) DEFAULT 0,
  `NCETFANDEF` int(11) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=11500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CompType`
--

DROP TABLE IF EXISTS `CompType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CompType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LTCTTCTTNO` int(11) NOT NULL,
  `STCTTYPE` varchar(31) DEFAULT NULL,
  `NTCTQFVAL` double DEFAULT NULL,
  `STCTLNM1` varchar(31) DEFAULT NULL,
  `STCTLNM2` varchar(31) DEFAULT NULL,
  `STCTLNM3` varchar(31) DEFAULT NULL,
  `STCTLNM4` varchar(31) DEFAULT NULL,
  `STCTLNM5` varchar(31) DEFAULT NULL,
  `STCTLNM6` varchar(31) DEFAULT NULL,
  `FTCTUO` double DEFAULT NULL,
  PRIMARY KEY (`LTCTTCTTNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=12500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Compliance`
--

DROP TABLE IF EXISTS `Compliance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Compliance` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `FHERSSCOR` double DEFAULT NULL,
  `FHERSCOST` double DEFAULT NULL,
  `FHERSSTARS` double DEFAULT NULL,
  `FHERSRHCN` double DEFAULT NULL,
  `FHERSRCCN` double DEFAULT NULL,
  `FHERSRDCN` double DEFAULT NULL,
  `FHERSRLACN` double DEFAULT NULL,
  `FHERSRPVCN` double DEFAULT NULL,
  `FHERSRTCN` double DEFAULT NULL,
  `FHERSDHCN` double DEFAULT NULL,
  `FHERSDCCN` double DEFAULT NULL,
  `FHERSDDCN` double DEFAULT NULL,
  `FHERSDLACN` double DEFAULT NULL,
  `FHERSDPVCN` double DEFAULT NULL,
  `FHERSDTCN` double DEFAULT NULL,
  `F98IERHCN` double DEFAULT NULL,
  `F98IERCCN` double DEFAULT NULL,
  `F98IERDCN` double DEFAULT NULL,
  `F98IERLACN` double DEFAULT NULL,
  `F98IERPVCN` double DEFAULT NULL,
  `F98IERTCN` double DEFAULT NULL,
  `F98IEDHCN` double DEFAULT NULL,
  `F98IEDCCN` double DEFAULT NULL,
  `F98IEDDCN` double DEFAULT NULL,
  `F98IEDLACN` double DEFAULT NULL,
  `F98IEDPVCN` double DEFAULT NULL,
  `F98IEDTCN` double DEFAULT NULL,
  `B98IECC` double DEFAULT NULL,
  `F00IERHCN` double DEFAULT NULL,
  `F00IERCCN` double DEFAULT NULL,
  `F00IERDCN` double DEFAULT NULL,
  `F00IERLACN` double DEFAULT NULL,
  `F00IERPVCN` double DEFAULT NULL,
  `F00IERTCN` double DEFAULT NULL,
  `F00IEDHCN` double DEFAULT NULL,
  `F00IEDCCN` double DEFAULT NULL,
  `F00IEDDCN` double DEFAULT NULL,
  `F00IEDLACN` double DEFAULT NULL,
  `F00IEDPVCN` double DEFAULT NULL,
  `F00IEDTCN` double DEFAULT NULL,
  `B00IECC` double DEFAULT NULL,
  `F01IERHCN` double DEFAULT NULL,
  `F01IERCCN` double DEFAULT NULL,
  `F01IERDCN` double DEFAULT NULL,
  `F01IERLACN` double DEFAULT NULL,
  `F01IERPVCN` double DEFAULT NULL,
  `F01IERTCN` double DEFAULT NULL,
  `F01IEDHCN` double DEFAULT NULL,
  `F01IEDCCN` double DEFAULT NULL,
  `F01IEDDCN` double DEFAULT NULL,
  `F01IEDLACN` double DEFAULT NULL,
  `F01IEDPVCN` double DEFAULT NULL,
  `F01IEDTCN` double DEFAULT NULL,
  `B01IECC` double DEFAULT NULL,
  `F03IERHCN` double DEFAULT NULL,
  `F03IERCCN` double DEFAULT NULL,
  `F03IERDCN` double DEFAULT NULL,
  `F03IERLACN` double DEFAULT NULL,
  `F03IERPVCN` double DEFAULT NULL,
  `F03IERTCN` double DEFAULT NULL,
  `F03IEDHCN` double DEFAULT NULL,
  `F03IEDCCN` double DEFAULT NULL,
  `F03IEDDCN` double DEFAULT NULL,
  `F03IEDLACN` double DEFAULT NULL,
  `F03IEDPVCN` double DEFAULT NULL,
  `F03IEDTCN` double DEFAULT NULL,
  `B03IECC` double DEFAULT NULL,
  `F04IERHCT` double DEFAULT NULL,
  `F04IERCCT` double DEFAULT NULL,
  `F04IERDCT` double DEFAULT NULL,
  `F04IERLACT` double DEFAULT NULL,
  `F04IERPVCT` double DEFAULT NULL,
  `F04IERSVCT` double DEFAULT NULL,
  `F04IERTCT` double DEFAULT NULL,
  `F04IEDHCT` double DEFAULT NULL,
  `F04IEDCCT` double DEFAULT NULL,
  `F04IEDDCT` double DEFAULT NULL,
  `F04IEDLACT` double DEFAULT NULL,
  `F04IEDPVCT` double DEFAULT NULL,
  `F04IEDSVCT` double DEFAULT NULL,
  `F04IEDTCT` double DEFAULT NULL,
  `B04IECC` double DEFAULT NULL,
  `F06IERHCT` double DEFAULT NULL,
  `F06IERCCT` double DEFAULT NULL,
  `F06IERDCT` double DEFAULT NULL,
  `F06IERLACT` double DEFAULT NULL,
  `F06IERPVCT` double DEFAULT NULL,
  `F06IERSVCT` double DEFAULT NULL,
  `F06IERTCT` double DEFAULT NULL,
  `F06IEDHCT` double DEFAULT NULL,
  `F06IEDCCT` double DEFAULT NULL,
  `F06IEDDCT` double DEFAULT NULL,
  `F06IEDLACT` double DEFAULT NULL,
  `F06IEDPVCT` double DEFAULT NULL,
  `F06IEDSVCT` double DEFAULT NULL,
  `F06IEDTCT` double DEFAULT NULL,
  `B06IECC` double DEFAULT NULL,
  `FNYECRHCN` double DEFAULT NULL,
  `FNYECRCCN` double DEFAULT NULL,
  `FNYECRDCN` double DEFAULT NULL,
  `FNYECRLACN` double DEFAULT NULL,
  `FNYECRPVCN` double DEFAULT NULL,
  `FNYECRTCN` double DEFAULT NULL,
  `FNYECDHCN` double DEFAULT NULL,
  `FNYECDCCN` double DEFAULT NULL,
  `FNYECDDCN` double DEFAULT NULL,
  `FNYECDLACN` double DEFAULT NULL,
  `FNYECDPVCN` double DEFAULT NULL,
  `FNYECDTCN` double DEFAULT NULL,
  `BNYECC` double DEFAULT NULL,
  `FNVECRHCN` double DEFAULT NULL,
  `FNVECRCCN` double DEFAULT NULL,
  `FNVECRDCN` double DEFAULT NULL,
  `FNVECRLACN` double DEFAULT NULL,
  `FNVECRPVCN` double DEFAULT NULL,
  `FNVECRTCN` double DEFAULT NULL,
  `FNVECDHCN` double DEFAULT NULL,
  `FNVECDCCN` double DEFAULT NULL,
  `FNVECDDCN` double DEFAULT NULL,
  `FNVECDLACN` double DEFAULT NULL,
  `FNVECDPVCN` double DEFAULT NULL,
  `FNVECDTCN` double DEFAULT NULL,
  `BNVECC` double DEFAULT NULL,
  `F92MECREUO` double DEFAULT NULL,
  `F92MECADUO` double DEFAULT NULL,
  `B92MECDUP` double DEFAULT NULL,
  `B92MECUOP` double DEFAULT NULL,
  `F93MECREUO` double DEFAULT NULL,
  `F93MECADUO` double DEFAULT NULL,
  `B93MECDUP` double DEFAULT NULL,
  `B93MECUOP` double DEFAULT NULL,
  `F95MECREUO` double DEFAULT NULL,
  `F95MECADUO` double DEFAULT NULL,
  `B95MECDUP` double DEFAULT NULL,
  `B95MECUOP` double DEFAULT NULL,
  `F98IECCRUO` double DEFAULT NULL,
  `F98IECCDUO` double DEFAULT NULL,
  `B98IECCDUP` int(11) DEFAULT NULL,
  `B98IECCUOP` int(11) DEFAULT NULL,
  `F00IECCRUO` double DEFAULT NULL,
  `F00IECCDUO` double DEFAULT NULL,
  `B00IECCDUP` int(11) DEFAULT NULL,
  `B00IECCUOP` int(11) DEFAULT NULL,
  `F01IECCRUO` double DEFAULT NULL,
  `F01IECCDUO` double DEFAULT NULL,
  `B01IECCDUP` int(11) DEFAULT NULL,
  `B01IECCUOP` int(11) DEFAULT NULL,
  `F03IECCRUO` double DEFAULT NULL,
  `F03IECCDUO` double DEFAULT NULL,
  `B03IECCDUP` int(11) DEFAULT NULL,
  `B03IECCUOP` int(11) DEFAULT NULL,
  `F04IECCRUA` double DEFAULT NULL,
  `F04IECCDUA` double DEFAULT NULL,
  `B04IECCDUP` int(11) DEFAULT NULL,
  `B04IECCUAP` int(11) DEFAULT NULL,
  `F06IECCRUA` double DEFAULT NULL,
  `F06IECCDUA` double DEFAULT NULL,
  `B06IECCDUP` int(11) DEFAULT NULL,
  `B06IECCUAP` int(11) DEFAULT NULL,
  `F92MECRHCN` double DEFAULT NULL,
  `F92MECRCCN` double DEFAULT NULL,
  `F92MECRDCN` double DEFAULT NULL,
  `F92MECRLCN` double DEFAULT NULL,
  `F92MECRPCN` double DEFAULT NULL,
  `F92MECRTCN` double DEFAULT NULL,
  `F92MECDHCN` double DEFAULT NULL,
  `F92MECDCCN` double DEFAULT NULL,
  `F92MECDDCN` double DEFAULT NULL,
  `F92MECDLCN` double DEFAULT NULL,
  `F92MECDPCN` double DEFAULT NULL,
  `F92MECDTCN` double DEFAULT NULL,
  `B92MECCC` double DEFAULT NULL,
  `F93MECRHCN` double DEFAULT NULL,
  `F93MECRCCN` double DEFAULT NULL,
  `F93MECRDCN` double DEFAULT NULL,
  `F93MECRLCN` double DEFAULT NULL,
  `F93MECRPCN` double DEFAULT NULL,
  `F93MECRTCN` double DEFAULT NULL,
  `F93MECDHCN` double DEFAULT NULL,
  `F93MECDCCN` double DEFAULT NULL,
  `F93MECDDCN` double DEFAULT NULL,
  `F93MECDLCN` double DEFAULT NULL,
  `F93MECDPCN` double DEFAULT NULL,
  `F93MECDTCN` double DEFAULT NULL,
  `B93MECCC` double DEFAULT NULL,
  `F95MECRHCN` double DEFAULT NULL,
  `F95MECRCCN` double DEFAULT NULL,
  `F95MECRDCN` double DEFAULT NULL,
  `F95MECRLCN` double DEFAULT NULL,
  `F95MECRPCN` double DEFAULT NULL,
  `F95MECRTCN` double DEFAULT NULL,
  `F95MECDHCN` double DEFAULT NULL,
  `F95MECDCCN` double DEFAULT NULL,
  `F95MECDDCN` double DEFAULT NULL,
  `F95MECDLCN` double DEFAULT NULL,
  `F95MECDPCN` double DEFAULT NULL,
  `F95MECDTCN` double DEFAULT NULL,
  `B95MECCC` double DEFAULT NULL,
  `F90_2ASLC` double DEFAULT NULL,
  `B90_2ASECP` double DEFAULT NULL,
  `F90_2ASRCN` double DEFAULT NULL,
  `F90_2ASRCT` double DEFAULT NULL,
  `F90_2ASDCN` double DEFAULT NULL,
  `F90_2ASDCT` double DEFAULT NULL,
  `B90_2ASCCP` double DEFAULT NULL,
  `BTAXCREDIT` int(11) DEFAULT NULL,
  `FNYHERS` double DEFAULT NULL,
  `BESTARV2` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `F09IERHCT` double DEFAULT NULL,
  `F09IERCCT` double DEFAULT NULL,
  `F09IERDCT` double DEFAULT NULL,
  `F09IERLACT` double DEFAULT NULL,
  `F09IERPVCT` double DEFAULT NULL,
  `F09IERSVCT` double DEFAULT NULL,
  `F09IERTCT` double DEFAULT NULL,
  `F09IEDHCT` double DEFAULT NULL,
  `F09IEDCCT` double DEFAULT NULL,
  `F09IEDDCT` double DEFAULT NULL,
  `F09IEDLACT` double DEFAULT NULL,
  `F09IEDPVCT` double DEFAULT NULL,
  `F09IEDSVCT` double DEFAULT NULL,
  `F09IEDTCT` double DEFAULT NULL,
  `B09IECC` double DEFAULT NULL,
  `F09IECCRUA` double DEFAULT NULL,
  `F09IECCDUA` double DEFAULT NULL,
  `B09IECCDUP` int(11) DEFAULT NULL,
  `B09IECCUAP` int(11) DEFAULT NULL,
  `FHERS_PV` double DEFAULT 0,
  `FES_HERS` double DEFAULT 0,
  `FES_HERSSA` double DEFAULT 0,
  `BESTARV25` int(11) DEFAULT NULL,
  `BESTARV3` int(11) DEFAULT NULL,
  `FNVREBATE` double DEFAULT NULL,
  `BPASS04IECC` int(11) DEFAULT NULL,
  `BPASS06IECC` int(11) DEFAULT NULL,
  `BPASS09IECC` int(11) DEFAULT NULL,
  `BPASS12IECC` int(11) DEFAULT NULL,
  `bDOECHALL` int(11) DEFAULT NULL,
  `FHERS130` double DEFAULT NULL,
  `FES_SZADJF` double DEFAULT NULL,
  `FDOE_Hers` double DEFAULT NULL,
  `FDOE_HersSA` double DEFAULT NULL,
  `bESTARV3HI` int(11) DEFAULT NULL,
  `bESTARV31` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=13500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CostRate`
--

DROP TABLE IF EXISTS `CostRate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CostRate` (
  `LCRCRNO` int(11) NOT NULL,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `FCRHTG` double DEFAULT NULL,
  `FCRHTG2` double DEFAULT NULL,
  `FCRHTGSAV` double DEFAULT NULL,
  `FCRCLG` double DEFAULT NULL,
  `FCRCLG2` double DEFAULT NULL,
  `FCRCLGSAV` double DEFAULT NULL,
  `FCRHW` double DEFAULT NULL,
  `FCRHW2` double DEFAULT NULL,
  `FCRHWSAV` double DEFAULT NULL,
  `FCRLA` double DEFAULT NULL,
  `FCRLA2` double DEFAULT NULL,
  `FCRLASAV` double DEFAULT NULL,
  `FCRSC` double DEFAULT NULL,
  `FCRSC2` double DEFAULT NULL,
  `FCRSCSAV` double DEFAULT NULL,
  `FCRTOT` double DEFAULT NULL,
  `FCRTOT2` double DEFAULT NULL,
  `FCRTOTSAV` double DEFAULT NULL,
  `FCRRATING` double DEFAULT NULL,
  `FCRRATING2` double DEFAULT NULL,
  `FCR1YCF` double DEFAULT NULL,
  PRIMARY KEY (`LCRCRNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=14500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DOEChallenge`
--

DROP TABLE IF EXISTS `DOEChallenge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DOEChallenge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SDCBLDRID` varchar(31) DEFAULT NULL,
  `NDCFENSTRTN` int(11) DEFAULT NULL,
  `NDCINSUL` int(11) DEFAULT NULL,
  `NDCDUCTLOC` int(11) DEFAULT NULL,
  `NDCAPPL` int(11) DEFAULT NULL,
  `NDCLIGHTING` int(11) NOT NULL DEFAULT 0,
  `NDCFANEFF` int(11) DEFAULT NULL,
  `NDCAIRQUAL` int(11) DEFAULT NULL,
  `NDCSOLARE` int(11) DEFAULT NULL,
  `NDCSOLARHW` int(11) DEFAULT NULL,
  `NDCAIRPLUS` int(11) NOT NULL DEFAULT 0,
  `NDCWTRSENSE` int(11) NOT NULL DEFAULT 0,
  `NDCIBHS` int(11) NOT NULL DEFAULT 0,
  `NDCMGMT` int(11) NOT NULL DEFAULT 0,
  `NDCWAIVER` int(11) NOT NULL DEFAULT 0,
  `SDCRATENO` varchar(31) DEFAULT NULL,
  `NDCWATEREFF` int(11) DEFAULT NULL,
  `nDCPassiveHome` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=15500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DehumidType`
--

DROP TABLE IF EXISTS `DehumidType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DehumidType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `lBldgRunNo` int(11) DEFAULT NULL,
  `lDhuEqKey` int(11) DEFAULT NULL,
  `sName` varchar(31) DEFAULT NULL,
  `nSystem` int(11) DEFAULT NULL,
  `nFuel` int(11) DEFAULT NULL,
  `fCapacity` double DEFAULT NULL,
  `fEfficiency` double DEFAULT NULL,
  `sNote` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=16500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DfhpType`
--

DROP TABLE IF EXISTS `DfhpType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DfhpType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LDFTDFTNO` double DEFAULT NULL,
  `SDFTTYPE` varchar(31) DEFAULT NULL,
  `NDFTFUEL` double DEFAULT NULL,
  `FDFTHHSPF` double DEFAULT NULL,
  `FDFTHCAP47` double DEFAULT NULL,
  `NDFTBFUEL` double DEFAULT NULL,
  `NDFTBEFFU` double DEFAULT NULL,
  `FDFTBSEFF` double DEFAULT NULL,
  `FDFTBCAP` double DEFAULT NULL,
  `FDFTCSEER` double DEFAULT NULL,
  `FDFTCCAP` double DEFAULT NULL,
  `FDFTCSHF` double DEFAULT NULL,
  `NDFTDSHTR` double DEFAULT NULL,
  `FDFTSWITCH` double DEFAULT NULL,
  `NDFTFNCTRL` int(11) DEFAULT 0,
  `NDFTFNDEF` int(11) DEFAULT 0,
  `FDFTFNHSPD` double DEFAULT 0,
  `FDFTFNLSPD` double DEFAULT 0,
  `SDFTNOTE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=17500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DhwDistrib`
--

DROP TABLE IF EXISTS `DhwDistrib`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DhwDistrib` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `lDhwDistNo` int(11) DEFAULT NULL,
  `bFixLowFlow` tinyint(1) DEFAULT 0,
  `bDhwPipeIns` tinyint(1) DEFAULT 0,
  `nRecircType` int(11) DEFAULT NULL,
  `fMaxFixDist` double DEFAULT NULL,
  `fSupRetDist` double DEFAULT NULL,
  `fPipeLenDhw` double DEFAULT NULL,
  `fPipeLenRec` double DEFAULT NULL,
  `fRecPumpPwr` double DEFAULT NULL,
  `bHasDwhr` tinyint(1) DEFAULT 0,
  `fDwhrEff` double DEFAULT NULL,
  `bDwhrPrehtC` tinyint(1) DEFAULT 0,
  `bDwhrPrehtH` tinyint(1) DEFAULT 0,
  `nShwrheads` int(11) DEFAULT NULL,
  `nShwrToDwhr` int(11) DEFAULT NULL,
  `fHwCtrlEff` double DEFAULT NULL,
  `nHomesServed` int(11) DEFAULT NULL,
  `fCompactFactor` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=17500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DhwType`
--

DROP TABLE IF EXISTS `DhwType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DhwType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LDETDETNO` double DEFAULT NULL,
  `SDETTYPE` varchar(31) DEFAULT NULL,
  `NDETSYSTTP` double DEFAULT NULL,
  `NDETFUELTP` double DEFAULT NULL,
  `FDETTNKVOL` double DEFAULT NULL,
  `FDETTNKINS` double DEFAULT NULL,
  `FDETENERGY` double DEFAULT NULL,
  `FDETRECEFF` double DEFAULT NULL,
  `SDETNOTE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=18500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Door`
--

DROP TABLE IF EXISTS `Door`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Door` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZDONAME` varchar(31) DEFAULT NULL,
  `FNOAREA` double DEFAULT NULL,
  `NDOWALLNUM` double DEFAULT NULL,
  `LDODOORTNO` int(11) NOT NULL,
  `FDOUO` double DEFAULT NULL,
  `SDORATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=19500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DoorType`
--

DROP TABLE IF EXISTS `DoorType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DoorType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LDTDTNO` int(11) NOT NULL,
  `SDTTYPE` varchar(31) DEFAULT NULL,
  `NDTTYPE` double DEFAULT NULL,
  `FDTRVALUE` double DEFAULT NULL,
  `SDTNOTE` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=20500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Duct`
--

DROP TABLE IF EXISTS `Duct`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Duct` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `LDUDSNO` int(11) NOT NULL DEFAULT 0,
  `FDUAREA` double DEFAULT NULL,
  `NDULOC` int(11) DEFAULT NULL,
  `FDUINS` double DEFAULT NULL,
  `NDUDCTTYPE` int(11) DEFAULT NULL,
  `SDURATENO` varchar(31) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=21500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DuctSystem`
--

DROP TABLE IF EXISTS `DuctSystem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DuctSystem` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `LDSDSNO` int(11) NOT NULL DEFAULT 0,
  `SZDSNAME` varchar(31) DEFAULT NULL,
  `LDSHTGNO` int(11) DEFAULT 0,
  `LDSCLGNO` int(11) DEFAULT 0,
  `FDSSUPAREA` double DEFAULT NULL,
  `FDSRETAREA` double DEFAULT NULL,
  `LDSREGIS` int(11) DEFAULT NULL,
  `NDSDLEAKTY` int(11) DEFAULT NULL,
  `FDSDLEAKTO` double DEFAULT NULL,
  `FDSDLEAKSU` double DEFAULT NULL,
  `FDSDLEAKRE` double DEFAULT NULL,
  `NDSDLEAKUN` int(11) DEFAULT NULL,
  `LDSDLEAKET` int(11) DEFAULT NULL,
  `SDSRATENO` varchar(31) DEFAULT NULL,
  `NDSDLEAKTT` int(11) DEFAULT NULL,
  `FDSCFAREA` double DEFAULT NULL,
  `fDSDLEAKRTO` float DEFAULT NULL,
  `nDSDLeakRUN` int(11) DEFAULT NULL,
  `NDSDLEAKTEX` int(11) DEFAULT NULL,
  `nDSInpType` int(11) DEFAULT NULL,
  `nDSLtOType` int(11) DEFAULT NULL,
  `nDSIECCEx` int(11) DEFAULT NULL,
  `nDSRESNETEx` int(11) DEFAULT NULL,
  `nDSESTAREx` int(11) DEFAULT NULL,
  `fDSTestLtO` float DEFAULT NULL,
  `fDSTestDL` float DEFAULT NULL,
  `nDSIsDucted` int(255) DEFAULT NULL,
  `nDSTestType` int(255) DEFAULT NULL,
  `fDSDSE` double DEFAULT NULL,
  PRIMARY KEY (`LDSDSNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=22500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ENERGYSTAR`
--

DROP TABLE IF EXISTS `ENERGYSTAR`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ENERGYSTAR` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `BESTARV2` int(11) DEFAULT NULL,
  `bESTARV25` int(11) DEFAULT NULL,
  `FV25HERSPV` double DEFAULT NULL,
  `FV25HERS` double DEFAULT NULL,
  `FV25HERSSA` double DEFAULT NULL,
  `FV25SZADJF` double DEFAULT NULL,
  `bESTARV3` int(11) DEFAULT NULL,
  `FV3HERSPV` double DEFAULT NULL,
  `FV3HERS` double DEFAULT NULL,
  `FV3HERSSA` double DEFAULT NULL,
  `FV3SZADJF` double DEFAULT NULL,
  `bESTARV3HI` int(11) DEFAULT NULL,
  `FV3HIHERSPV` double DEFAULT NULL,
  `FV3HIHERS` double DEFAULT NULL,
  `Fv3HIHERSSA` double DEFAULT NULL,
  `FV3HISZADJF` double DEFAULT NULL,
  `bESTARV31` int(11) DEFAULT NULL,
  `FV31HERSPV` double DEFAULT NULL,
  `FV31HERS` double DEFAULT NULL,
  `FV31HERSSA` double DEFAULT NULL,
  `FV31SZADJF` double DEFAULT NULL,
  `BDOEPROGRAM` int(11) DEFAULT NULL,
  `FDOEHERS` double DEFAULT NULL,
  `FDOEHERSSA` double DEFAULT NULL,
  `bESTARV32W` int(11) DEFAULT NULL,
  `FV32WHERSPV` double DEFAULT NULL,
  `FV32WHERS` double DEFAULT NULL,
  `FV32WHERSSA` double DEFAULT NULL,
  `FV32WSZADJF` double DEFAULT NULL,
  `bESTARV10MF` int(255) DEFAULT NULL,
  `FV10MFHERSPV` double DEFAULT NULL,
  `FV10MFHERS` double DEFAULT NULL,
  `BESTARV11MF` int(255) DEFAULT NULL,
  `FV11MFHERSPV` double DEFAULT NULL,
  `FV11MFHERS` double DEFAULT NULL,
  `BESTARV12MF` int(255) DEFAULT NULL,
  `FV12MFHERSPV` double DEFAULT NULL,
  `FV12MFHERS` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=23500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ESRequire`
--

DROP TABLE IF EXISTS `ESRequire`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ESRequire` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `NESEQUIP` smallint(6) DEFAULT 0,
  `NESWINDOW` smallint(6) DEFAULT 0,
  `NESFIXTURE` smallint(6) DEFAULT 0,
  `NESAPPLI` smallint(6) DEFAULT 0,
  `NESCEILFAN` smallint(6) DEFAULT 0,
  `NESVENTFAN` smallint(6) DEFAULT 0,
  `nABOVERALL` smallint(6) DEFAULT 0,
  `nABGRBDJST` smallint(6) DEFAULT 0,
  `nABEVBFFLS` smallint(6) DEFAULT 0,
  `nABSLABEDG` smallint(6) DEFAULT 0,
  `nABBANDJST` smallint(6) DEFAULT 0,
  `nABTHMLBRG` smallint(6) DEFAULT 0,
  `nWLSHWRTUB` smallint(6) DEFAULT 0,
  `nWLFIREPLC` smallint(6) DEFAULT 0,
  `nWLATCSLPE` smallint(6) DEFAULT 0,
  `nWLATCKNEE` smallint(6) DEFAULT 0,
  `nWLSKYSHFT` smallint(6) DEFAULT 0,
  `nWLPORCHRF` smallint(6) DEFAULT 0,
  `nWLSTRCASE` smallint(6) DEFAULT 0,
  `nWLDOUBLE` smallint(6) DEFAULT 0,
  `nFLRABVGRG` smallint(6) DEFAULT 0,
  `nFLRCANTIL` smallint(6) DEFAULT 0,
  `nSHAFTDUCT` smallint(6) DEFAULT 0,
  `nSHAFTPIPE` smallint(6) DEFAULT 0,
  `nSHAFTFLUE` smallint(6) DEFAULT 0,
  `nATCACCPNL` smallint(6) DEFAULT 0,
  `nATDDSTAIR` smallint(6) DEFAULT 0,
  `nRFDRPSOFT` smallint(6) DEFAULT 0,
  `nRFRECSLGT` smallint(6) DEFAULT 0,
  `nRFHOMEFAN` smallint(6) DEFAULT 0,
  `nCWLBTWNUT` smallint(6) DEFAULT 0,
  `SRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=24500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Econ`
--

DROP TABLE IF EXISTS `Econ`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Econ` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LECECNO` int(11) NOT NULL,
  `LECCRNO` int(11) NOT NULL,
  `FECIMPCST` double DEFAULT NULL,
  `FECWTLIFE` double DEFAULT NULL,
  `NECMORTERM` double DEFAULT NULL,
  `FECMORRATE` double DEFAULT NULL,
  `FECPVF` double DEFAULT NULL,
  `FECSAVTOT` double DEFAULT NULL,
  `FECMAINT` double DEFAULT NULL,
  `FECNETSAV` double DEFAULT NULL,
  `FECMORCST` double DEFAULT NULL,
  `FECPVSAV` double DEFAULT NULL,
  `NECRANKCR` double DEFAULT NULL,
  `FECCUTOFF` double DEFAULT NULL,
  `FECMAXLIM` double DEFAULT NULL,
  `NECMEASINT` double DEFAULT NULL,
  PRIMARY KEY (`LECECNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=25500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `EconParam`
--

DROP TABLE IF EXISTS `EconParam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EconParam` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `NFSBaseline` int(11) DEFAULT NULL,
  `SFSBldgName` varchar(255) DEFAULT NULL,
  `FEPImpCost` double DEFAULT NULL,
  `FEPImpLife` double DEFAULT NULL,
  `FEPMortRat` double DEFAULT NULL,
  `FEPMortPer` double DEFAULT NULL,
  `FEPDownPay` double DEFAULT NULL,
  `FEPAppVal` double DEFAULT NULL,
  `FEPInf` double DEFAULT NULL,
  `FEPDisRate` double DEFAULT NULL,
  `FEPEnInf` double DEFAULT NULL,
  `FEPAnalPer` double DEFAULT NULL,
  `NEPImpLifeD` int(11) DEFAULT NULL,
  `NEPMortRatD` int(11) DEFAULT NULL,
  `NEPMortPerD` int(11) DEFAULT NULL,
  `NEPDownPayD` int(11) DEFAULT NULL,
  `NEPInfD` int(11) DEFAULT NULL,
  `NEPDisRateD` int(11) DEFAULT NULL,
  `NEPEnInfD` int(11) DEFAULT NULL,
  `NEPAnalPerD` int(11) DEFAULT NULL,
  `NEPDOECalc` int(11) DEFAULT NULL,
  `NEPCalcMthd` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=26500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `EqInst`
--

DROP TABLE IF EXISTS `EqInst`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EqInst` (
  `LEIEINO` int(11) NOT NULL,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `LEIHETNO` double DEFAULT NULL,
  `LEIGSTNO` double DEFAULT NULL,
  `LEIDFTNO` double DEFAULT NULL,
  `LEICLTNO` double DEFAULT NULL,
  `LEIDHTNO` double DEFAULT NULL,
  `LEIASTNO` double DEFAULT NULL,
  `LEIHDTNO` double DEFAULT NULL,
  `NEISYSTYPE` double DEFAULT NULL,
  `FEIPERADJ` double DEFAULT NULL,
  `NEILOC` double DEFAULT NULL,
  `FEIHLDSRV` double DEFAULT NULL,
  `FEICLDSRV` double DEFAULT NULL,
  `FEIDLDSRV` double DEFAULT NULL,
  `NEINOUNITS` int(11) DEFAULT 0,
  `fEIDSE` double DEFAULT NULL,
  `fCWLoadSrvd` double DEFAULT NULL,
  `fDWLoadSrvd` double DEFAULT NULL,
  `fDhuLoadSrvd` double DEFAULT NULL,
  `fMVHtgLoadSrvd` double DEFAULT NULL,
  `fMVClgLoadSrvd` double DEFAULT NULL,
  `nDwellUnitsDhw` int(11) DEFAULT NULL,
  `lDhuEqKey` int(11) DEFAULT NULL,
  `lSharedEqKey` int(11) DEFAULT NULL,
  `nPrecondSharedMV` int(11) DEFAULT NULL,
  PRIMARY KEY (`LEIEINO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=27500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Equip`
--

DROP TABLE IF EXISTS `Equip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Equip` (
  `LEIEINO` int(11) NOT NULL,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `FEIHSETPNT` double DEFAULT NULL,
  `FEICSETPNT` double DEFAULT NULL,
  `NEISBTHRM` double DEFAULT NULL,
  `NEISUTHRM` double DEFAULT NULL,
  `NEIVENTTYP` double DEFAULT NULL,
  `NEISBSCH` double DEFAULT NULL,
  `FEISBTEMP` double DEFAULT NULL,
  `NEIDUCTLOC` double DEFAULT NULL,
  `NEIDUCTLO2` double DEFAULT NULL,
  `NEIDUCTLO3` double DEFAULT NULL,
  `FEIDUCTINS` double DEFAULT NULL,
  `FEIDUCTIN2` double DEFAULT NULL,
  `FEIDUCTIN3` double DEFAULT NULL,
  `FEIDUCTSUP` double DEFAULT NULL,
  `FEIDUCTSU2` double DEFAULT NULL,
  `FEIDUCTSU3` double DEFAULT NULL,
  `FEIDUCTRET` double DEFAULT NULL,
  `FEIDUCTRE2` double DEFAULT NULL,
  `FEIDUCTRE3` double DEFAULT NULL,
  `NEIDUCTLK` double DEFAULT NULL,
  `NEIDTUNITS` int(11) DEFAULT 0,
  `FEIDTLKAGE` double DEFAULT 0,
  `NEIDTQUAL` int(11) DEFAULT 0,
  `SEIRATENO` varchar(31) DEFAULT NULL,
  `NEIHTGCAPWT` int(11) DEFAULT NULL,
  `NEICLGCAPWT` int(11) DEFAULT NULL,
  `NEIDHWCAPWT` int(11) DEFAULT NULL,
  `nEIDHUCAPWT` int(11) DEFAULT NULL,
  `fEIWHFFlow` double DEFAULT NULL,
  `fEIWHFWatts` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=28500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Florida`
--

DROP TABLE IF EXISTS `Florida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Florida` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) DEFAULT NULL,
  `NTYPE` int(11) DEFAULT NULL,
  `NWORSTCASE` int(11) DEFAULT NULL,
  `SPERMITOFF` varchar(51) DEFAULT NULL,
  `SPERMITNO` varchar(51) DEFAULT NULL,
  `SJURISDCTN` varchar(51) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=29500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FlrType`
--

DROP TABLE IF EXISTS `FlrType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FlrType` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LFTFTNO` int(11) NOT NULL,
  `FFTJSTWDT` double DEFAULT NULL,
  `FFTJSTHGT` double DEFAULT NULL,
  `FFTJSTSPG` double DEFAULT NULL,
  `FFTCONTINS` double DEFAULT NULL,
  `FFTCVTYINS` double DEFAULT NULL,
  `FFTCINSTHK` double DEFAULT NULL,
  `NFTCOVTYPE` double DEFAULT NULL,
  `NFTTCTNO` int(11) NOT NULL,
  `BFTQFVALID` double DEFAULT NULL,
  `NFTQFTYPE` int(11) DEFAULT 0,
  `FFTFLRWID` double DEFAULT 0,
  `FFTOUTWID` double DEFAULT 0,
  `FFTBATTHK` double DEFAULT 0,
  `FFTBATRVL` double DEFAULT 0,
  `FFTBLKTHK` double DEFAULT 0,
  `FFTBLKRVL` double DEFAULT 0,
  `NFTCNTINS` int(11) DEFAULT 0,
  `NFTOUTINS` int(11) DEFAULT 0,
  `FFTFF` double DEFAULT NULL,
  `BFTDFLTFF` int(11) DEFAULT NULL,
  `SFTNOTE` varchar(255) DEFAULT NULL,
  `NFTINSGRDE` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=30500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FndWall`
--

DROP TABLE IF EXISTS `FndWall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FndWall` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) DEFAULT NULL,
  `SZFWNAME` varchar(31) DEFAULT NULL,
  `FFWLENGTH` double DEFAULT NULL,
  `FFWHEIGHT` double DEFAULT NULL,
  `FFWDBGRADE` double DEFAULT NULL,
  `FFWHAGRADE` double DEFAULT NULL,
  `NFWLOC` double DEFAULT NULL,
  `LFWFWTNO` int(11) DEFAULT NULL,
  `SFWRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=31500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FndwType`
--

DROP TABLE IF EXISTS `FndwType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FndwType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LFWTWTNO` int(11) NOT NULL,
  `SFWTTYPE` varchar(31) DEFAULT NULL,
  `NFWTTYPE` double DEFAULT NULL,
  `NFWTSTDTYP` double DEFAULT NULL,
  `FFWTMASTHK` double DEFAULT NULL,
  `FFWTEXTINS` double DEFAULT NULL,
  `FFWTEXINST` double DEFAULT NULL,
  `FFWTEXINSB` double DEFAULT NULL,
  `NFWTEINTTP` double DEFAULT NULL,
  `NFWTEINBTP` double DEFAULT NULL,
  `FFWTININCT` double DEFAULT NULL,
  `FFWTININFC` double DEFAULT NULL,
  `FFWTININST` double DEFAULT NULL,
  `FFWTININSB` double DEFAULT NULL,
  `NFWTIINTTP` double DEFAULT NULL,
  `NFWTIINBTP` double DEFAULT NULL,
  `SFWTNOTE` varchar(255) DEFAULT NULL,
  `NFWTINSGRD` int(11) DEFAULT NULL,
  PRIMARY KEY (`LFWTWTNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=32500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FrameFlr`
--

DROP TABLE IF EXISTS `FrameFlr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FrameFlr` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZFFNAME` varchar(31) DEFAULT NULL,
  `FFFAREA` double DEFAULT NULL,
  `NFFLOC` double DEFAULT NULL,
  `FFFUO` double DEFAULT NULL,
  `LFFFLORTNO` int(11) NOT NULL,
  `SFFRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=33500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FuelSum`
--

DROP TABLE IF EXISTS `FuelSum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FuelSum` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `NFSFUEL` double DEFAULT NULL,
  `NFSUNITS` double DEFAULT NULL,
  `FFSHCONS` double DEFAULT NULL,
  `FFSCCONS` double DEFAULT NULL,
  `FFSWCONS` double DEFAULT NULL,
  `FFSLACONS` double DEFAULT NULL,
  `FFSTOTCOST` double DEFAULT NULL,
  `FFSPVCONS` double DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `FFSTOTCONS` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=34500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `GshpType`
--

DROP TABLE IF EXISTS `GshpType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GshpType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LGSTGSTNO` double DEFAULT NULL,
  `SGSTTYPE` varchar(31) DEFAULT NULL,
  `NGSTTYPE` double DEFAULT NULL,
  `NGSTFUEL` double DEFAULT NULL,
  `FGSTHCOP70` double DEFAULT NULL,
  `FGSTHCOP50` double DEFAULT NULL,
  `FGSTCEER70` double DEFAULT NULL,
  `FGSTCEER50` double DEFAULT NULL,
  `FGSTHCAP70` double DEFAULT NULL,
  `FGSTHCAP50` double DEFAULT NULL,
  `FGSTCCAP70` double DEFAULT NULL,
  `FGSTCCAP50` double DEFAULT NULL,
  `FGSTHCOP32` double DEFAULT NULL,
  `FGSTHCAP32` double DEFAULT NULL,
  `FGSTCEER77` double DEFAULT NULL,
  `FGSTCCAP77` double DEFAULT NULL,
  `FGSTSHF` double DEFAULT NULL,
  `NGSTFANDEF` double DEFAULT NULL,
  `NGSTDSHTR` double DEFAULT NULL,
  `SGSTNOTE` varchar(255) DEFAULT NULL,
  `FGSTBKUPCP` double DEFAULT NULL,
  `fGSTFANPWR` double DEFAULT NULL,
  `fGSTPmpEng` double DEFAULT NULL,
  `nGSTPmpEnT` int(11) DEFAULT NULL,
  `nGSTDbType` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=35500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `GshpWell`
--

DROP TABLE IF EXISTS `GshpWell`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GshpWell` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `lGWellNo` int(11) DEFAULT NULL,
  `nGWType` int(1) DEFAULT NULL,
  `fGWNoWells` double DEFAULT NULL,
  `fGWDepth` double DEFAULT NULL,
  `fGWLpFlow` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=36500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HERSCode`
--

DROP TABLE IF EXISTS `HERSCode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HERSCode` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `FHERSSCOR` double DEFAULT NULL,
  `FHERSCOST` double DEFAULT NULL,
  `FHERSSTARS` double DEFAULT NULL,
  `FHERSRHCN` double DEFAULT NULL,
  `FHERSRCCN` double DEFAULT NULL,
  `FHERSRDCN` double DEFAULT NULL,
  `FHERSRLACN` double DEFAULT NULL,
  `FHERSRPVCN` double DEFAULT NULL,
  `FHERSRTCN` double DEFAULT NULL,
  `FHERSDHCN` double DEFAULT NULL,
  `FHERSDCCN` double DEFAULT NULL,
  `FHERSDDCN` double DEFAULT NULL,
  `FHERSDLACN` double DEFAULT NULL,
  `FHERSDPVCN` double DEFAULT NULL,
  `FHERSDTCN` double DEFAULT NULL,
  `FNYHERS` double DEFAULT NULL,
  `BTAXCREDIT` int(11) DEFAULT NULL,
  `FHERS130` double DEFAULT NULL,
  `NBADORIENT` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=37500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HeatPath`
--

DROP TABLE IF EXISTS `HeatPath`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HeatPath` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LHPTCTTNO` double DEFAULT NULL,
  `SHPPTHNAME` varchar(31) DEFAULT NULL,
  `FHPPTHAREA` double DEFAULT NULL,
  `FHPPTHRVAL` double DEFAULT NULL,
  `FHPLRVAL1` double DEFAULT NULL,
  `FHPLRVAL2` double DEFAULT NULL,
  `FHPLRVAL3` double DEFAULT NULL,
  `FHPLRVAL4` double DEFAULT NULL,
  `FHPLRVAL5` double DEFAULT NULL,
  `FHPLRVAL6` double DEFAULT NULL,
  `FHPLRVAL7` double DEFAULT NULL,
  `FHPLRVAL8` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=38500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HercInfo`
--

DROP TABLE IF EXISTS `HercInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HercInfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) DEFAULT NULL,
  `SHIUSRITEM` varchar(255) DEFAULT NULL,
  `SHIITMTYPE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=39500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HtDhType`
--

DROP TABLE IF EXISTS `HtDhType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HtDhType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LHTDHTDNO` double DEFAULT NULL,
  `SHTDTYPE` varchar(31) DEFAULT NULL,
  `NHTDSYSTTP` double DEFAULT NULL,
  `NHTDDISTTP` double DEFAULT NULL,
  `NHTDFUEL` double DEFAULT NULL,
  `FHTDRATCAP` double DEFAULT NULL,
  `FHTDSPHTE` double DEFAULT NULL,
  `FHTDWHEF` double DEFAULT NULL,
  `FHTDWHRE` double DEFAULT NULL,
  `FHTDTNKSZ` double DEFAULT NULL,
  `FHTDTNKIN` double DEFAULT NULL,
  `NHTDFNCTRL` int(11) DEFAULT 0,
  `NHTDFNDEF` int(11) DEFAULT 0,
  `FHTDFNHSPD` double DEFAULT 0,
  `FHTDFNLSPD` double DEFAULT 0,
  `SHTDNOTE` varchar(255) DEFAULT NULL,
  `FHTDAUXELC` double DEFAULT 0,
  `NHTDAUXETP` int(11) DEFAULT 0,
  `NHTDAUXDEF` int(11) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=40500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HtgType`
--

DROP TABLE IF EXISTS `HtgType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HtgType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LHETHETNO` double DEFAULT NULL,
  `SHETTYPE` varchar(31) DEFAULT NULL,
  `NHETSYSTTP` double DEFAULT NULL,
  `NHETFUELTP` double DEFAULT NULL,
  `FHETRATCAP` double DEFAULT NULL,
  `FHETEFF` double DEFAULT NULL,
  `NHETEFFUTP` double DEFAULT NULL,
  `NHETDSHTR` double DEFAULT NULL,
  `NHETFNCTRL` int(11) DEFAULT 0,
  `NHETFNDEF` int(11) DEFAULT 0,
  `FHETFNHSPD` double DEFAULT 0,
  `FHETFNLSPD` double DEFAULT 0,
  `SHETNOTE` varchar(255) DEFAULT NULL,
  `FHETAUXELC` double DEFAULT 0,
  `NHETAUXETP` int(11) DEFAULT 0,
  `NHETAUXDEF` int(11) DEFAULT 0,
  `FHETFANPWR` double DEFAULT 0,
  `FHETPMPENG` double DEFAULT 0,
  `NHETPMPTYP` int(11) DEFAULT 0,
  `FHETRCAP17` double DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=41500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HvacCx`
--

DROP TABLE IF EXISTS `HvacCx`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HvacCx` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `lHvacCxNo` int(11) DEFAULT NULL,
  `nDuctSysNo` int(11) DEFAULT NULL,
  `nHtgEquipNo` int(11) DEFAULT NULL,
  `nClgEquipNo` int(11) DEFAULT NULL,
  `nTotDuctLeakGrade` int(11) DEFAULT NULL,
  `bTotDuctLeakExcep` int(11) DEFAULT NULL,
  `bTotDuctLeakGrdIMet` int(11) DEFAULT NULL,
  `fTotDuctLeakage` double DEFAULT NULL,
  `nBFAirflowGrade` int(11) DEFAULT NULL,
  `bBFAirflowException` int(11) DEFAULT NULL,
  `nBFAirflowDesignSpec` int(11) DEFAULT NULL,
  `nBFAirflowOpCond` int(11) DEFAULT NULL,
  `nBFWattDrawGrade` int(11) DEFAULT NULL,
  `nBFWattDraw` int(11) DEFAULT NULL,
  `fBFEffic` double DEFAULT NULL,
  `bRCSinglePkgSystem` int(11) DEFAULT NULL,
  `bRCOnboardDiagnostic` int(11) DEFAULT NULL,
  `nRCTestMethod` int(11) DEFAULT NULL,
  `nRCGrade` int(11) DEFAULT NULL,
  `fDiffDTD` double DEFAULT NULL,
  `fDiffCTOA` double DEFAULT NULL,
  `fDeviation` double DEFAULT NULL,
  `fRptdRefrigWeight` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=42500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IECC`
--

DROP TABLE IF EXISTS `IECC`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IECC` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `F98IERHCN` double DEFAULT NULL,
  `F98IERCCN` double DEFAULT NULL,
  `F98IERDCN` double DEFAULT NULL,
  `F98IERLACN` double DEFAULT NULL,
  `F98IERPVCN` double DEFAULT NULL,
  `F98IERTCN` double DEFAULT NULL,
  `F98IEDHCN` double DEFAULT NULL,
  `F98IEDCCN` double DEFAULT NULL,
  `F98IEDDCN` double DEFAULT NULL,
  `F98IEDLACN` double DEFAULT NULL,
  `F98IEDPVCN` double DEFAULT NULL,
  `F98IEDTCN` double DEFAULT NULL,
  `B98IECC` double DEFAULT NULL,
  `F98IECCRUO` double DEFAULT NULL,
  `F98IECCDUO` double DEFAULT NULL,
  `B98IECCDUP` int(11) DEFAULT NULL,
  `B98IECCUOP` int(11) DEFAULT NULL,
  `F00IERHCN` double DEFAULT NULL,
  `F00IERCCN` double DEFAULT NULL,
  `F00IERDCN` double DEFAULT NULL,
  `F00IERLACN` double DEFAULT NULL,
  `F00IERPVCN` double DEFAULT NULL,
  `F00IERTCN` double DEFAULT NULL,
  `F00IEDHCN` double DEFAULT NULL,
  `F00IEDCCN` double DEFAULT NULL,
  `F00IEDDCN` double DEFAULT NULL,
  `F00IEDLACN` double DEFAULT NULL,
  `F00IEDPVCN` double DEFAULT NULL,
  `F00IEDTCN` double DEFAULT NULL,
  `B00IECC` double DEFAULT NULL,
  `F00IECCRUO` double DEFAULT NULL,
  `F00IECCDUO` double DEFAULT NULL,
  `B00IECCDUP` int(11) DEFAULT NULL,
  `B00IECCUOP` int(11) DEFAULT NULL,
  `F01IERHCN` double DEFAULT NULL,
  `F01IERCCN` double DEFAULT NULL,
  `F01IERDCN` double DEFAULT NULL,
  `F01IERLACN` double DEFAULT NULL,
  `F01IERPVCN` double DEFAULT NULL,
  `F01IERTCN` double DEFAULT NULL,
  `F01IEDHCN` double DEFAULT NULL,
  `F01IEDCCN` double DEFAULT NULL,
  `F01IEDDCN` double DEFAULT NULL,
  `F01IEDLACN` double DEFAULT NULL,
  `F01IEDPVCN` double DEFAULT NULL,
  `F01IEDTCN` double DEFAULT NULL,
  `B01IECC` double DEFAULT NULL,
  `F01IECCRUO` double DEFAULT NULL,
  `F01IECCDUO` double DEFAULT NULL,
  `B01IECCDUP` int(11) DEFAULT NULL,
  `B01IECCUOP` int(11) DEFAULT NULL,
  `F03IERHCN` double DEFAULT NULL,
  `F03IERCCN` double DEFAULT NULL,
  `F03IERDCN` double DEFAULT NULL,
  `F03IERLACN` double DEFAULT NULL,
  `F03IERPVCN` double DEFAULT NULL,
  `F03IERTCN` double DEFAULT NULL,
  `F03IEDHCN` double DEFAULT NULL,
  `F03IEDCCN` double DEFAULT NULL,
  `F03IEDDCN` double DEFAULT NULL,
  `F03IEDLACN` double DEFAULT NULL,
  `F03IEDPVCN` double DEFAULT NULL,
  `F03IEDTCN` double DEFAULT NULL,
  `B03IECC` double DEFAULT NULL,
  `F03IECCRUO` double DEFAULT NULL,
  `F03IECCDUO` double DEFAULT NULL,
  `B03IECCDUP` int(11) DEFAULT NULL,
  `B03IECCUOP` int(11) DEFAULT NULL,
  `F04IERHCT` double DEFAULT NULL,
  `F04IERCCT` double DEFAULT NULL,
  `F04IERDCT` double DEFAULT NULL,
  `F04IERLACT` double DEFAULT NULL,
  `F04IERPVCT` double DEFAULT NULL,
  `F04IERSVCT` double DEFAULT NULL,
  `F04IERTCT` double DEFAULT NULL,
  `F04IEDHCT` double DEFAULT NULL,
  `F04IEDCCT` double DEFAULT NULL,
  `F04IEDDCT` double DEFAULT NULL,
  `F04IEDLACT` double DEFAULT NULL,
  `F04IEDPVCT` double DEFAULT NULL,
  `F04IEDSVCT` double DEFAULT NULL,
  `F04IEDTCT` double DEFAULT NULL,
  `B04IECC` double DEFAULT NULL,
  `F04IECCRUA` double DEFAULT NULL,
  `F04IECCDUA` double DEFAULT NULL,
  `B04IECCDUP` int(11) DEFAULT NULL,
  `B04IECCUAP` int(11) DEFAULT NULL,
  `bPass04IECC` int(11) DEFAULT 0,
  `F06IERHCT` double DEFAULT NULL,
  `F06IERCCT` double DEFAULT NULL,
  `F06IERDCT` double DEFAULT NULL,
  `F06IERLACT` double DEFAULT NULL,
  `F06IERPVCT` double DEFAULT NULL,
  `F06IERSVCT` double DEFAULT NULL,
  `F06IERTCT` double DEFAULT NULL,
  `F06IEDHCT` double DEFAULT NULL,
  `F06IEDCCT` double DEFAULT NULL,
  `F06IEDDCT` double DEFAULT NULL,
  `F06IEDLACT` double DEFAULT NULL,
  `F06IEDPVCT` double DEFAULT NULL,
  `F06IEDSVCT` double DEFAULT NULL,
  `F06IEDTCT` double DEFAULT NULL,
  `B06IECC` double DEFAULT NULL,
  `F06IECCRUA` double DEFAULT NULL,
  `F06IECCDUA` double DEFAULT NULL,
  `B06IECCDUP` int(11) DEFAULT NULL,
  `B06IECCUAP` int(11) DEFAULT NULL,
  `bPass06IECC` int(11) DEFAULT 0,
  `F09IERHCT` double DEFAULT NULL,
  `F09IERCCT` double DEFAULT NULL,
  `F09IERDCT` double DEFAULT NULL,
  `F09IERLACT` double DEFAULT NULL,
  `F09IERPVCT` double DEFAULT NULL,
  `F09IERSVCT` double DEFAULT NULL,
  `F09IERTCT` double DEFAULT NULL,
  `F09IEDHCT` double DEFAULT NULL,
  `F09IEDCCT` double DEFAULT NULL,
  `F09IEDDCT` double DEFAULT NULL,
  `F09IEDLACT` double DEFAULT NULL,
  `F09IEDPVCT` double DEFAULT NULL,
  `F09IEDSVCT` double DEFAULT NULL,
  `F09IEDTCT` double DEFAULT NULL,
  `B09IECC` double DEFAULT NULL,
  `F09IECCRUA` double DEFAULT NULL,
  `F09IECCDUA` double DEFAULT NULL,
  `B09IECCDUP` int(11) DEFAULT NULL,
  `B09IECCUAP` int(11) DEFAULT NULL,
  `bPass09IECC` int(11) DEFAULT 0,
  `F12IERHCT` double DEFAULT NULL,
  `F12IERCCT` double DEFAULT NULL,
  `F12IERDCT` double DEFAULT NULL,
  `F12IERLACT` double DEFAULT NULL,
  `F12IERPVCT` double DEFAULT NULL,
  `F12IERSVCT` double DEFAULT NULL,
  `F12IERTCT` double DEFAULT NULL,
  `F12IEDHCT` double DEFAULT NULL,
  `F12IEDCCT` double DEFAULT NULL,
  `F12IEDDCT` double DEFAULT NULL,
  `F12IEDLACT` double DEFAULT NULL,
  `F12IEDPVCT` double DEFAULT NULL,
  `F12IEDSVCT` double DEFAULT NULL,
  `F12IEDTCT` double DEFAULT NULL,
  `B12IECC` double DEFAULT NULL,
  `F12IECCRUA` double DEFAULT NULL,
  `F12IECCDUA` double DEFAULT NULL,
  `B12IECCDUP` int(11) DEFAULT NULL,
  `B12IECCUAP` int(11) DEFAULT NULL,
  `bPass12IECC` int(11) DEFAULT 0,
  `F15IERHCT` double DEFAULT NULL,
  `F15IERCCT` double DEFAULT NULL,
  `F15IERDCT` double DEFAULT NULL,
  `F15IERLACT` double DEFAULT NULL,
  `F15IERPVCT` double DEFAULT NULL,
  `F15IERSVCT` double DEFAULT NULL,
  `F15IERTCT` double DEFAULT NULL,
  `F15IEDHCT` double DEFAULT NULL,
  `F15IEDCCT` double DEFAULT NULL,
  `F15IEDDCT` double DEFAULT NULL,
  `F15IEDLACT` double DEFAULT NULL,
  `F15IEDPVCT` double DEFAULT NULL,
  `F15IEDSVCT` double DEFAULT NULL,
  `F15IEDTCT` double DEFAULT NULL,
  `B15IECC` int(11) DEFAULT NULL,
  `F15IECCRUA` double DEFAULT NULL,
  `F15IECCDUA` double DEFAULT NULL,
  `B15IECCDUP` int(11) DEFAULT NULL,
  `B15IECCUAP` int(11) DEFAULT NULL,
  `bPass15IECC` int(11) DEFAULT NULL,
  `f18IERHCT` float DEFAULT NULL,
  `f18IERCCT` float DEFAULT NULL,
  `f18IERDCT` float DEFAULT NULL,
  `f18IERLACT` float DEFAULT NULL,
  `f18IERPVCT` float DEFAULT NULL,
  `f18IERSVCT` float DEFAULT NULL,
  `f18IERTCT` float DEFAULT NULL,
  `f18IEDHCT` float DEFAULT NULL,
  `f18IEDCCT` float DEFAULT NULL,
  `f18IEDDCT` float DEFAULT NULL,
  `f18IEDLACT` float DEFAULT NULL,
  `f18IEDPVCT` float DEFAULT NULL,
  `f18IEDSVCT` float DEFAULT NULL,
  `f18IEDTCT` float DEFAULT NULL,
  `b18IECC` int(11) DEFAULT NULL,
  `f18IECCRUA` float DEFAULT NULL,
  `f18IECCDUA` float DEFAULT NULL,
  `b18IECCDuP` int(11) DEFAULT NULL,
  `b18IECCuAP` int(11) DEFAULT NULL,
  `bPass18IECC` float DEFAULT NULL,
  `f18IERMVCT` double DEFAULT NULL,
  `f18IEDMVCT` double DEFAULT NULL,
  `f21IERHCT` double DEFAULT NULL,
  `f21IERCCT` double DEFAULT NULL,
  `f21IERDCT` double DEFAULT NULL,
  `f21IERLACT` double DEFAULT NULL,
  `f21IERMVCT` double DEFAULT NULL,
  `f21IERPVCT` double DEFAULT NULL,
  `f21IERSVCT` double DEFAULT NULL,
  `f21IERTCT` double DEFAULT NULL,
  `f21IEDHCT` double DEFAULT NULL,
  `f21IEDCCT` double DEFAULT NULL,
  `f21IEDDCT` double DEFAULT NULL,
  `f21IEDLACT` double DEFAULT NULL,
  `f21IEDMVCT` double DEFAULT NULL,
  `f21IEDPVCT` double DEFAULT NULL,
  `f21IEDSVCT` double DEFAULT NULL,
  `f21IEDTCT` double DEFAULT NULL,
  `b21IECC` int(11) DEFAULT NULL,
  `f21IECCRUA` double DEFAULT NULL,
  `f21IECCDUA` double DEFAULT NULL,
  `b21IECCDuP` int(11) DEFAULT NULL,
  `b21IECCuAP` int(11) DEFAULT NULL,
  `bPass21IECC` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=43500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Infilt`
--

DROP TABLE IF EXISTS `Infilt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Infilt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `LININFILNO` int(11) DEFAULT NULL,
  `NINTYPE` double DEFAULT NULL,
  `FINHEATVAL` double DEFAULT NULL,
  `FINCOOLVAL` double DEFAULT NULL,
  `NINWHINFUN` double DEFAULT NULL,
  `LINMVTYPE` int(11) DEFAULT NULL,
  `FINMVRATE` double DEFAULT NULL,
  `FINSREFF` double DEFAULT NULL,
  `NINHRSDAY` double DEFAULT NULL,
  `FINMVFAN` double DEFAULT NULL,
  `SINRATENO` varchar(31) DEFAULT NULL,
  `FINTREFF` double DEFAULT NULL,
  `NINVERIFY` double DEFAULT NULL,
  `NINSHLTRCL` int(11) DEFAULT 0,
  `NINCLGVENT` int(11) DEFAULT NULL,
  `NINFANMOTOR` int(11) DEFAULT NULL,
  `FINANNUAL` float DEFAULT NULL,
  `FINTESTED` float DEFAULT NULL,
  `NINGDAIRXMF` int(11) DEFAULT NULL,
  `NINNOMVMSRD` int(255) DEFAULT NULL,
  `NINWATTDFLT` int(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=44500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Joist`
--

DROP TABLE IF EXISTS `Joist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Joist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZRJNAME` varchar(31) DEFAULT NULL,
  `FRJAREA` double DEFAULT NULL,
  `NRJLOC` double DEFAULT NULL,
  `FRJCOINSUL` double DEFAULT NULL,
  `FRJFRINSUL` double DEFAULT NULL,
  `FRJSPACING` double DEFAULT NULL,
  `FRJUO` double DEFAULT NULL,
  `FRJINSULTH` double DEFAULT NULL,
  `SRJRATENO` varchar(31) DEFAULT NULL,
  `NRJINSGRDE` int(11) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=45500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LAInst`
--

DROP TABLE IF EXISTS `LAInst`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LAInst` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SLAINAME` varchar(255) DEFAULT NULL,
  `NLAITYPE` double DEFAULT 0,
  `NLAILOC` double DEFAULT 0,
  `NLAIFUEL` double DEFAULT 0,
  `FLAIRATE` double DEFAULT NULL,
  `NLAIRATEU` double DEFAULT NULL,
  `FLAIUSE` double DEFAULT NULL,
  `NLAIUSEU` double DEFAULT NULL,
  `NLAIQTY` int(11) NOT NULL,
  `NLAIEFF` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=46500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LightApp`
--

DROP TABLE IF EXISTS `LightApp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LightApp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `FLAOVNFUEL` double DEFAULT NULL,
  `FLADRYFUEL` double DEFAULT NULL,
  `SLARATENO` varchar(31) DEFAULT NULL,
  `NLAUSEDEF` double DEFAULT NULL,
  `FLAREFKWH` double DEFAULT NULL,
  `FLADISHWEF` double DEFAULT 0,
  `FLAFLRCENT` double DEFAULT 0,
  `FLAFANCFM` double DEFAULT 0,
  `FLACFLCENT` double DEFAULT 0,
  `FLACFLEXT` double DEFAULT NULL,
  `FLACFLGAR` double DEFAULT NULL,
  `NLAREFLOC` int(11) NOT NULL,
  `FLADISHWCAP` double DEFAULT NULL,
  `FLADISHWYR` double DEFAULT NULL,
  `NLAOVNIND` int(11) NOT NULL,
  `NLAOVNCON` int(11) NOT NULL,
  `NLADRYLOC` int(11) NOT NULL,
  `NLADRYMOIST` int(11) NOT NULL,
  `FLADRYEF` double DEFAULT NULL,
  `FLADRYMEF` double DEFAULT NULL,
  `FLADRYGASEF` double DEFAULT NULL,
  `NLAWASHLOC` int(11) NOT NULL,
  `FLAWASHLER` double DEFAULT NULL,
  `FLAWASHCAP` double DEFAULT NULL,
  `FLAWASHELEC` double DEFAULT NULL,
  `FLAWASHGAS` double DEFAULT NULL,
  `FLAWASHGCST` double DEFAULT NULL,
  `FLAWASHEFF` double DEFAULT NULL,
  `FLALEDINT` double DEFAULT NULL,
  `FLALEDEXT` double DEFAULT NULL,
  `FLALEDGAR` double DEFAULT NULL,
  `nLAFanCnt` int(20) DEFAULT NULL,
  `nLAOvnLoc` int(20) DEFAULT NULL,
  `nLADryUnit` int(20) DEFAULT NULL,
  `nLAWashPre` int(20) DEFAULT NULL,
  `nLAWashUnit` int(20) DEFAULT NULL,
  `nLAWashDhw` int(20) DEFAULT NULL,
  `nLAWashLoad` int(20) DEFAULT NULL,
  `fLAWashIWF` double DEFAULT NULL,
  `nLADishLoc` int(20) DEFAULT NULL,
  `nLADishPre` int(20) DEFAULT NULL,
  `nLADishDhw` int(20) DEFAULT NULL,
  `fLADishElec` double DEFAULT NULL,
  `fLADishGas` double DEFAULT NULL,
  `fLADishGCst` double DEFAULT NULL,
  `nLADishLoad` int(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=47500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MandReq`
--

DROP TABLE IF EXISTS `MandReq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MandReq` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `NMRIECC04` smallint(6) DEFAULT NULL,
  `NMRIECC06` int(11) DEFAULT NULL,
  `NMRIECC09` int(11) DEFAULT NULL,
  `NMRESV2TBC` int(11) DEFAULT NULL,
  `NMRESV2PRD` int(11) DEFAULT 0,
  `NMRESV3TEC` int(11) DEFAULT NULL,
  `NMRESV3HC` int(11) DEFAULT NULL,
  `NMRESV3HR` int(11) DEFAULT NULL,
  `NMRESV3WM` int(11) DEFAULT NULL,
  `NMRESV3AP` int(11) DEFAULT 0,
  `NMRESV3RF` int(11) DEFAULT 0,
  `NMRESV3CF` int(11) DEFAULT 0,
  `NMRESV3EF` int(11) DEFAULT 0,
  `NMRESV3DW` int(11) DEFAULT 0,
  `NMRESV3NRF` int(11) DEFAULT 0,
  `NMRESV3NCF` int(11) DEFAULT 0,
  `NMRESV3NEF` int(11) DEFAULT 0,
  `NMRESV3NDW` int(11) DEFAULT 0,
  `SMRRATENO` varchar(31) DEFAULT NULL,
  `NMRIECCNY` smallint(6) DEFAULT 0,
  `nMRESV3SAF` int(11) DEFAULT 0,
  `fMRESV3BFA` double DEFAULT 0,
  `nMRESV3NBB` int(11) DEFAULT 0,
  `NMRIECC12` int(11) DEFAULT NULL,
  `NMRFLORIDA` int(11) DEFAULT NULL,
  `NMRESV3SLAB` int(11) DEFAULT NULL,
  `NMRIECC15` int(11) DEFAULT NULL,
  `SMRESQUAL4` varchar(31) DEFAULT NULL,
  `NMRIECC18` int(11) DEFAULT NULL,
  `NMRIECCMI` int(11) DEFAULT NULL,
  `NMRESMFWSHR` int(11) DEFAULT NULL,
  `NMRESMFDRYR` int(11) DEFAULT NULL,
  `NMRESMFWIN` int(11) DEFAULT NULL,
  `NMRIECCNC` int(11) DEFAULT NULL,
  `nMRNGBS15` int(11) DEFAULT NULL,
  `NMRIECC21` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=48500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MechVent`
--

DROP TABLE IF EXISTS `MechVent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MechVent` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `lBldgRunNo` int(11) DEFAULT NULL,
  `lBldgNo` int(11) DEFAULT NULL,
  `sMVRateNo` varchar(31) DEFAULT NULL,
  `sMVName` varchar(31) DEFAULT NULL,
  `nMVType` int(11) DEFAULT NULL,
  `fMVRate` double DEFAULT NULL,
  `nMVHrsDay` int(11) DEFAULT NULL,
  `fMVFanPwr` double DEFAULT NULL,
  `fMVASRE` double DEFAULT NULL,
  `fMVATRE` double DEFAULT NULL,
  `nMVNotMsrd` int(11) DEFAULT NULL,
  `nMVWattDflt` int(11) DEFAULT NULL,
  `nMVFanMotor` int(11) DEFAULT NULL,
  `nMVDuctNo` int(11) DEFAULT NULL,
  `nMVShrdMF` int(11) DEFAULT NULL,
  `nMVHtgNo` int(11) DEFAULT NULL,
  `nMVClgNo` int(11) DEFAULT NULL,
  `fMVShrdCFM` double DEFAULT NULL,
  `fMVOAPct` double DEFAULT NULL,
  `fMVRecirc` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=49500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `NevMeas`
--

DROP TABLE IF EXISTS `NevMeas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `NevMeas` (
  `LNMNMNO` int(11) NOT NULL,
  `SNMCITY` varchar(100) DEFAULT NULL,
  `SNMHOUSE` varchar(100) DEFAULT NULL,
  `SNMFND` varchar(100) DEFAULT NULL,
  `SNMHTG` varchar(100) DEFAULT NULL,
  `SNMCLG` varchar(100) DEFAULT NULL,
  `SNMDHWFT` varchar(100) DEFAULT NULL,
  `SNMMEATYP` varchar(100) DEFAULT NULL,
  `SNMMEADSC` varchar(255) DEFAULT NULL,
  `FNMKWH` double DEFAULT NULL,
  `FNMTHERM` double DEFAULT NULL,
  PRIMARY KEY (`LNMNMNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=50500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PhotoVol`
--

DROP TABLE IF EXISTS `PhotoVol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PhotoVol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `NPVCOLTYPE` double DEFAULT NULL,
  `FPVAREA` double DEFAULT NULL,
  `FPVPOWER` double DEFAULT NULL,
  `FPVTILT` double DEFAULT NULL,
  `NPVOR` double DEFAULT NULL,
  `FPVINVEFF` double DEFAULT NULL,
  `SPVRATENO` varchar(31) DEFAULT NULL,
  `SPVNAME` varchar(31) DEFAULT NULL,
  `nPVNumBeds` int(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=51500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ProjInfo`
--

DROP TABLE IF EXISTS `ProjInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ProjInfo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SPIPOWNER` varchar(31) DEFAULT NULL,
  `SPISTREET` varchar(31) DEFAULT NULL,
  `SPICITY` varchar(31) DEFAULT NULL,
  `SPISTATE` varchar(31) DEFAULT NULL,
  `SPIZIP` varchar(31) DEFAULT NULL,
  `SPIPHONE` varchar(31) DEFAULT NULL,
  `SPIBUILDER` varchar(31) DEFAULT NULL,
  `SPIMODEL` varchar(51) DEFAULT NULL,
  `SPIBLDRDEV` varchar(31) DEFAULT NULL,
  `SPIBLDRPHO` varchar(31) DEFAULT NULL,
  `SPIRATORG` varchar(31) DEFAULT NULL,
  `SPIRATPHON` varchar(31) DEFAULT NULL,
  `SPIRATNAME` varchar(31) DEFAULT NULL,
  `SPIRATERNO` varchar(31) DEFAULT NULL,
  `SPIRATDATE` varchar(31) DEFAULT NULL,
  `SPIRATNGNO` varchar(31) DEFAULT NULL,
  `SPIRATTYPE` varchar(31) DEFAULT NULL,
  `SPIRATREAS` varchar(31) DEFAULT NULL,
  `SPIBLDRSTR` varchar(31) DEFAULT NULL,
  `SPIBLDRCTY` varchar(31) DEFAULT NULL,
  `SPIBLGNAME` varchar(51) DEFAULT NULL,
  `SPIRATEMAL` varchar(101) DEFAULT NULL,
  `SPIRATSTR` varchar(31) DEFAULT NULL,
  `SPIRATCITY` varchar(31) DEFAULT NULL,
  `SPIRATST` varchar(31) DEFAULT NULL,
  `SPIRATZIP` varchar(31) DEFAULT NULL,
  `SPIRATWEB` varchar(101) DEFAULT NULL,
  `SPIBLDREML` varchar(101) DEFAULT NULL,
  `SPIPRVDRID` varchar(31) DEFAULT NULL,
  `SPIREGID` varchar(51) DEFAULT NULL,
  `SPISAMSETID` varchar(31) DEFAULT NULL,
  `SPIBLDRPRMT` varchar(31) DEFAULT NULL,
  `SPIVER1NAME` varchar(31) DEFAULT NULL,
  `SPIVER1ID` varchar(31) DEFAULT NULL,
  `SPIVER2NAME` varchar(31) DEFAULT NULL,
  `SPIVER2ID` varchar(31) DEFAULT NULL,
  `SPIVER3NAME` varchar(31) DEFAULT NULL,
  `SPIVER3ID` varchar(31) DEFAULT NULL,
  `SPIVER4NAME` varchar(31) DEFAULT NULL,
  `SPIVER4ID` varchar(31) DEFAULT NULL,
  `SPIREGDATE` varchar(31) DEFAULT NULL,
  `SPIPRMTDATE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=52500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RegionalCode`
--

DROP TABLE IF EXISTS `RegionalCode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RegionalCode` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `FNVREBATE` double DEFAULT NULL,
  `FNYECRHCN` double DEFAULT NULL,
  `FNYECRCCN` double DEFAULT NULL,
  `FNYECRDCN` double DEFAULT NULL,
  `FNYECRLACN` double DEFAULT NULL,
  `FNYECRPVCN` double DEFAULT NULL,
  `FNYECRTCN` double DEFAULT NULL,
  `FNYECDHCN` double DEFAULT NULL,
  `FNYECDCCN` double DEFAULT NULL,
  `FNYECDDCN` double DEFAULT NULL,
  `FNYECDLACN` double DEFAULT NULL,
  `FNYECDPVCN` double DEFAULT NULL,
  `FNYECDTCN` double DEFAULT NULL,
  `BNYECC` double DEFAULT NULL,
  `FNVECRHCN` double DEFAULT NULL,
  `FNVECRCCN` double DEFAULT NULL,
  `FNVECRDCN` double DEFAULT NULL,
  `FNVECRLACN` double DEFAULT NULL,
  `FNVECRPVCN` double DEFAULT NULL,
  `FNVECRTCN` double DEFAULT NULL,
  `FNVECDHCN` double DEFAULT NULL,
  `FNVECDCCN` double DEFAULT NULL,
  `FNVECDDCN` double DEFAULT NULL,
  `FNVECDLACN` double DEFAULT NULL,
  `FNVECDPVCN` double DEFAULT NULL,
  `FNVECDTCN` double DEFAULT NULL,
  `BNVECC` double DEFAULT NULL,
  `FNCRHCT` double DEFAULT NULL,
  `FNCRCCT` double DEFAULT NULL,
  `FNCRDCT` double DEFAULT NULL,
  `FNCRLACT` double DEFAULT NULL,
  `FNCRPVCT` double DEFAULT NULL,
  `FNCRSVCT` double DEFAULT NULL,
  `FNCRTCT` double DEFAULT NULL,
  `FNCDHCT` double DEFAULT NULL,
  `FNCDCCT` double DEFAULT NULL,
  `FNCDDCT` double DEFAULT NULL,
  `FNCDLACT` double DEFAULT NULL,
  `FNCDPVCT` double DEFAULT NULL,
  `FNCDSVCT` double DEFAULT NULL,
  `FNCDTCT` double DEFAULT NULL,
  `BNCMEETCT` int(11) DEFAULT NULL,
  `FNCRUA` double DEFAULT NULL,
  `FNCDUA` double DEFAULT NULL,
  `BNCDCTPASS` int(11) DEFAULT NULL,
  `BNCUAPASS` int(11) DEFAULT NULL,
  `BNCPASS` int(11) DEFAULT NULL,
  `FNCHRHCT` double DEFAULT NULL,
  `FNCHRCCT` double DEFAULT NULL,
  `FNCHRDCT` double DEFAULT NULL,
  `FNCHRLACT` double DEFAULT NULL,
  `FNCHRPVCT` double DEFAULT NULL,
  `FNCHRSVCT` double DEFAULT NULL,
  `FNCHRTCT` double DEFAULT NULL,
  `FNCHDHCT` double DEFAULT NULL,
  `FNCHDCCT` double DEFAULT NULL,
  `FNCHDDCT` double DEFAULT NULL,
  `FNCHDLACT` double DEFAULT NULL,
  `FNCHDPVCT` double DEFAULT NULL,
  `FNCHDSVCT` double DEFAULT NULL,
  `FNCHDTCT` double DEFAULT NULL,
  `BNCHMEETCT` int(11) DEFAULT NULL,
  `FNCHRUA` double DEFAULT NULL,
  `FNCHDUA` double DEFAULT NULL,
  `BNCHDCTPASS` int(11) DEFAULT NULL,
  `BNCHUAPASS` int(11) DEFAULT NULL,
  `BNCHPASS` int(11) DEFAULT NULL,
  `FNYRHCT` double DEFAULT NULL,
  `FNYRCCT` double DEFAULT NULL,
  `FNYRDCT` double DEFAULT NULL,
  `FNYRLACT` double DEFAULT NULL,
  `FNYRPVCT` double DEFAULT NULL,
  `FNYRSVCT` double DEFAULT NULL,
  `FNYRTCT` double DEFAULT NULL,
  `FNYDHCT` double DEFAULT NULL,
  `FNYDCCT` double DEFAULT NULL,
  `FNYDDCT` double DEFAULT NULL,
  `FNYDLACT` double DEFAULT NULL,
  `FNYDPVCT` double DEFAULT NULL,
  `FNYDSVCT` double DEFAULT NULL,
  `FNYDTCT` double DEFAULT NULL,
  `BNYMEETCT` double DEFAULT NULL,
  `FNYRUA` double DEFAULT NULL,
  `FNYDUA` double DEFAULT NULL,
  `BNYDCTPASS` double DEFAULT NULL,
  `BNYUAPASS` double DEFAULT NULL,
  `BNYPASS` double DEFAULT NULL,
  `FNYRMVCT` double DEFAULT NULL,
  `FNYDMVCT` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=53500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RejMeas`
--

DROP TABLE IF EXISTS `RejMeas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RejMeas` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LRMRMNO` int(11) NOT NULL,
  `LRMCRNO` int(11) NOT NULL,
  `LRMPARNO` double DEFAULT NULL,
  `NRMMULT` double DEFAULT NULL,
  `SRMCOMP` varchar(51) DEFAULT NULL,
  `SRMEXIST` varchar(51) DEFAULT NULL,
  `SRMPROP` varchar(51) DEFAULT NULL,
  `SRMTREAT` varchar(121) DEFAULT NULL,
  `SRMTREATD` varchar(121) DEFAULT NULL,
  `FRMLIFE` double DEFAULT NULL,
  `FRMCOST` double DEFAULT NULL,
  `NRMREJREAS` double DEFAULT NULL,
  `SRMREJREAS` varchar(51) DEFAULT NULL,
  PRIMARY KEY (`LRMRMNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=54500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ResnetDisc`
--

DROP TABLE IF EXISTS `ResnetDisc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ResnetDisc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `NRDQ1` smallint(6) DEFAULT 0,
  `NRDQ2A` smallint(6) DEFAULT 0,
  `NRDQ2B` smallint(6) DEFAULT 0,
  `NRDQ2C` smallint(6) DEFAULT 0,
  `NRDQ2D` smallint(6) DEFAULT 0,
  `NRDQ2E` smallint(6) DEFAULT 0,
  `SRDQ2EOTHR` varchar(255) DEFAULT NULL,
  `NRDQ3A` smallint(6) DEFAULT 0,
  `NRDQ3B` smallint(6) DEFAULT 0,
  `NRDQ3C` smallint(6) DEFAULT 0,
  `NRDQ4HVACI` smallint(6) DEFAULT 3,
  `NRDQ4HVACB` smallint(6) DEFAULT 3,
  `NRDQ4THMLI` smallint(6) DEFAULT 3,
  `NRDQ4THMLB` smallint(6) DEFAULT 3,
  `NRDQ4AIRSI` smallint(6) DEFAULT 3,
  `NRDQ4AIRSB` smallint(6) DEFAULT 3,
  `NRDQ4WINI` smallint(6) DEFAULT 3,
  `NRDQ4WINB` smallint(6) DEFAULT 3,
  `NRDQ4APPLI` smallint(6) DEFAULT 3,
  `NRDQ4APPLB` smallint(6) DEFAULT 3,
  `NRDQ4CNSTI` smallint(6) DEFAULT 3,
  `NRDQ4CNSTB` smallint(6) DEFAULT 3,
  `NRDQ4OTHRI` smallint(6) DEFAULT 3,
  `NRDQ4OTHRB` smallint(6) DEFAULT 3,
  `SRDQ4OTHR` varchar(255) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `NRDQ5` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=55500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Results`
--

DROP TABLE IF EXISTS `Results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `FHTEFF` double DEFAULT NULL,
  `FCLGEFF` double DEFAULT NULL,
  `FHWEFF` double DEFAULT NULL,
  `FLHROOF` double DEFAULT NULL,
  `FLCROOF` double DEFAULT NULL,
  `FLHJOIST` double DEFAULT NULL,
  `FLCJOIST` double DEFAULT NULL,
  `FLHAGWALL` double DEFAULT NULL,
  `FLCAGWALL` double DEFAULT NULL,
  `FLHFNDWALL` double DEFAULT NULL,
  `FLCFNDWALL` double DEFAULT NULL,
  `FLHWNDOSK` double DEFAULT NULL,
  `FLCWNDOSK` double DEFAULT NULL,
  `FLHFFLR` double DEFAULT NULL,
  `FLCFFLR` double DEFAULT NULL,
  `FLHCRAWL` double DEFAULT NULL,
  `FLCCRAWL` double DEFAULT NULL,
  `FLHSLAB` double DEFAULT NULL,
  `FLCSLAB` double DEFAULT NULL,
  `FLHINF` double DEFAULT NULL,
  `FLCINF` double DEFAULT NULL,
  `FLHMECHVNT` double DEFAULT NULL,
  `FLCMECHVNT` double DEFAULT NULL,
  `FLHDUCT` double DEFAULT NULL,
  `FLCDUCT` double DEFAULT NULL,
  `FLHASOL` double DEFAULT NULL,
  `FLCASOL` double DEFAULT NULL,
  `FLHSS` double DEFAULT NULL,
  `FLCSS` double DEFAULT NULL,
  `FLHIGAIN` double DEFAULT NULL,
  `FLCIGAIN` double DEFAULT NULL,
  `FLHWHF` double DEFAULT NULL,
  `FLCWHF` double DEFAULT NULL,
  `FLHDOOR` double DEFAULT NULL,
  `FLCDOOR` double DEFAULT NULL,
  `FLHTOTAL` double DEFAULT NULL,
  `FLCTOTAL` double DEFAULT NULL,
  `FTOTDHW` double DEFAULT NULL,
  `FSOLSAVE` double DEFAULT NULL,
  `FHTPEAK` double DEFAULT NULL,
  `FACSPEAK` double DEFAULT NULL,
  `FACLPEAK` double DEFAULT NULL,
  `FACTPEAK` double DEFAULT NULL,
  `FHBUCK` double DEFAULT NULL,
  `FACBUCK` double DEFAULT NULL,
  `FWBUCK` double DEFAULT NULL,
  `FHCONS` double DEFAULT NULL,
  `FCCONS` double DEFAULT NULL,
  `FHCOST` double DEFAULT NULL,
  `FCCOST` double DEFAULT NULL,
  `FWCONS` double DEFAULT NULL,
  `FWCOST` double DEFAULT NULL,
  `FSERVCOST` double DEFAULT NULL,
  `FTOTCOST` double DEFAULT NULL,
  `FREFRCONS` double DEFAULT NULL,
  `FFRZCONS` double DEFAULT NULL,
  `FDRYCONS` double DEFAULT NULL,
  `FOVENCONS` double DEFAULT NULL,
  `FLAOTHCONS` double DEFAULT NULL,
  `FLIHSCONS` double DEFAULT NULL,
  `FLICSCONS` double DEFAULT NULL,
  `FREFRCOST` double DEFAULT NULL,
  `FFRZCOST` double DEFAULT NULL,
  `FDRYCOST` double DEFAULT NULL,
  `FOVENCOST` double DEFAULT NULL,
  `FLAOTHCOST` double DEFAULT NULL,
  `FLIGHTCOST` double DEFAULT NULL,
  `FLATOTCONS` double DEFAULT NULL,
  `FLATOTCOST` double DEFAULT NULL,
  `FPVTOTCONS` double DEFAULT NULL,
  `FPVTOTCOST` double DEFAULT NULL,
  `FSHELLAREA` double DEFAULT NULL,
  `FHTGLDPHDD` double DEFAULT NULL,
  `FCLGLDPHDD` double DEFAULT NULL,
  `FHTGDDPHDD` double DEFAULT NULL,
  `FCLGDDPHDD` double DEFAULT NULL,
  `FHTGACH` double DEFAULT NULL,
  `FCLGACH` double DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `FEMCO2TOT` double DEFAULT NULL,
  `FEMSO2TOT` double DEFAULT NULL,
  `FEMNOXTOT` double DEFAULT NULL,
  `FEMCO2HTG` double DEFAULT NULL,
  `FEMCO2CLG` double DEFAULT NULL,
  `FEMCO2DHW` double DEFAULT NULL,
  `FEMCO2LA` double DEFAULT NULL,
  `FEMCO2PV` double DEFAULT NULL,
  `FEMSO2HTG` double DEFAULT NULL,
  `FEMSO2CLG` double DEFAULT NULL,
  `FEMSO2DHW` double DEFAULT NULL,
  `FEMSO2LA` double DEFAULT NULL,
  `FEMSO2PV` double DEFAULT NULL,
  `FEMNOXHTG` double DEFAULT NULL,
  `FEMNOXCLG` double DEFAULT NULL,
  `FEMNOXDHW` double DEFAULT NULL,
  `FEMNOXLA` double DEFAULT NULL,
  `FEMNOXPV` double DEFAULT NULL,
  `FEMHERSCO2` double DEFAULT NULL,
  `FEMHERSSO2` double DEFAULT NULL,
  `FEMHERSNOX` double DEFAULT NULL,
  `FSRCEGYHTG` double DEFAULT NULL,
  `FSRCEGYCLG` double DEFAULT NULL,
  `FSRCEGYDHW` double DEFAULT NULL,
  `FSRCEGYLA` double DEFAULT NULL,
  `FSRCEGYPV` double DEFAULT NULL,
  `fDHWNoLoss` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=56500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Roof`
--

DROP TABLE IF EXISTS `Roof`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Roof` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) DEFAULT NULL,
  `SZRONAME` varchar(31) DEFAULT NULL,
  `FROAREA` double DEFAULT NULL,
  `NROTYPE` double DEFAULT NULL,
  `NRORADBAR` double DEFAULT NULL,
  `NROCOL` double DEFAULT NULL,
  `LROCEILTNO` int(11) NOT NULL,
  `FROUO` double DEFAULT NULL,
  `SRORATENO` varchar(31) DEFAULT NULL,
  `NROCLAY` int(11) DEFAULT NULL,
  `NROVENT` int(11) DEFAULT NULL,
  `FROROOFAREA` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=57500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SSCmnWal`
--

DROP TABLE IF EXISTS `SSCmnWal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SSCmnWal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZSSCNAME` varchar(31) DEFAULT NULL,
  `FSSCAREA` double DEFAULT NULL,
  `NSSCMTYP` double DEFAULT NULL,
  `FSSCMTHK` double DEFAULT NULL,
  `FSSCINS` double DEFAULT NULL,
  `NSSCFAN` double DEFAULT NULL,
  `FSSCFLRATE` double DEFAULT NULL,
  `SSSCRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=58500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SSMass`
--

DROP TABLE IF EXISTS `SSMass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SSMass` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZSSMNAME` varchar(31) DEFAULT NULL,
  `FSSMAREA` double DEFAULT NULL,
  `NSSMTYPE` double DEFAULT NULL,
  `FSSMTHK` double DEFAULT NULL,
  `FSSMWVOL` double DEFAULT NULL,
  `SSSMRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=59500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SSSkLght`
--

DROP TABLE IF EXISTS `SSSkLght`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SSSkLght` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZSSSNAME` varchar(31) DEFAULT NULL,
  `FSSSAREA` double DEFAULT NULL,
  `NSSSOR` double DEFAULT NULL,
  `FSSSPITCH` double DEFAULT NULL,
  `FSSSSUM` double DEFAULT NULL,
  `FSSSWTR` double DEFAULT NULL,
  `LSSSWDWTNO` int(11) NOT NULL,
  `SSSSRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=60500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SSWindow`
--

DROP TABLE IF EXISTS `SSWindow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SSWindow` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZSSWNAME` varchar(31) DEFAULT NULL,
  `FSSWAREA` double DEFAULT NULL,
  `NSSWOR` double DEFAULT NULL,
  `FSSWSUM` double DEFAULT NULL,
  `FSSWWTR` double DEFAULT NULL,
  `LSSWWDWTNO` int(11) NOT NULL,
  `SSSWRATENO` varchar(31) DEFAULT NULL,
  `FSSOHDEPTH` double DEFAULT NULL,
  `FSSOHTOTOP` double DEFAULT NULL,
  `FSSOHTOBTM` double DEFAULT NULL,
  `FSSADJSUM` double DEFAULT NULL,
  `FSSADJWTR` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=61500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SeasnRat`
--

DROP TABLE IF EXISTS `SeasnRat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SeasnRat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LSRSRNO` int(11) NOT NULL,
  `LSRURNO` int(11) NOT NULL,
  `NSRSTRTMTH` double DEFAULT NULL,
  `NSRSTOPMTH` double DEFAULT NULL,
  `FSRSVCCHRG` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=62500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SharedType`
--

DROP TABLE IF EXISTS `SharedType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SharedType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `lBldgRunNo` int(11) DEFAULT NULL,
  `lSharedEqKey` int(11) DEFAULT NULL,
  `sName` varchar(31) DEFAULT NULL,
  `nSystem` int(11) DEFAULT NULL,
  `nFuel` int(11) DEFAULT NULL,
  `fRatedEff` double DEFAULT NULL,
  `nRatedEffUnit` int(11) DEFAULT NULL,
  `fBoilerCap` double DEFAULT NULL,
  `fChillerCap` double DEFAULT NULL,
  `fGndLoopCap` double DEFAULT NULL,
  `fGndLoopPump` double DEFAULT NULL,
  `nBlgLoopUnits` int(11) DEFAULT NULL,
  `fBlgLoopPumpPwr` double DEFAULT NULL,
  `nTerminalType` int(11) DEFAULT NULL,
  `fFanCoil` double DEFAULT NULL,
  `sNote` varchar(255) DEFAULT NULL,
  `lHtgEqKey` int(11) DEFAULT NULL,
  `lClgEqKey` int(11) DEFAULT NULL,
  `lGshpEqKey` int(11) DEFAULT NULL,
  `lWlhpEqKey` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=63500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SimpInp`
--

DROP TABLE IF EXISTS `SimpInp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SimpInp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `NSIHSETYPE` double DEFAULT NULL,
  `NSIFNDTYPE` double DEFAULT NULL,
  `FSIFNDPESL` double DEFAULT NULL,
  `FSIFNDPEOC` double DEFAULT NULL,
  `FSIFNDPEEC` double DEFAULT NULL,
  `FSIFNDPEHC` double DEFAULT NULL,
  `FSIFNDPEUF` double DEFAULT NULL,
  `FSIFNDPEHF` double DEFAULT NULL,
  `FSIFNDPEUW` double DEFAULT NULL,
  `FSIFNDPEHW` double DEFAULT NULL,
  `FSICFLAREA` double DEFAULT NULL,
  `NSIBEDRMS` double DEFAULT NULL,
  `FSIPFLARHB` double DEFAULT NULL,
  `FSIPFLARFL` double DEFAULT NULL,
  `FSIPFLARML` double DEFAULT NULL,
  `FSIPFLARSL` double DEFAULT NULL,
  `FSIPFLARTL` double DEFAULT NULL,
  `NSINOCRNHB` double DEFAULT NULL,
  `NSINOCRNFL` double DEFAULT NULL,
  `NSINOCRNML` double DEFAULT NULL,
  `NSINOCRNSL` double DEFAULT NULL,
  `NSINOCRNTL` double DEFAULT NULL,
  `FSIPOABOHB` double DEFAULT NULL,
  `FSIPOABOFL` double DEFAULT NULL,
  `FSIPOABOML` double DEFAULT NULL,
  `FSIPOABOSL` double DEFAULT NULL,
  `FSIPOABOTL` double DEFAULT NULL,
  `FSICEILHHB` double DEFAULT NULL,
  `FSICEILHFL` double DEFAULT NULL,
  `FSICEILHML` double DEFAULT NULL,
  `FSICEILHSL` double DEFAULT NULL,
  `FSICEILHTL` double DEFAULT NULL,
  `FSIPOGRGE` double DEFAULT NULL,
  `FSIPCATHHB` double DEFAULT NULL,
  `FSIPCATHFL` double DEFAULT NULL,
  `FSIPCATHML` double DEFAULT NULL,
  `FSIPCATHSL` double DEFAULT NULL,
  `FSIPCATHTL` double DEFAULT NULL,
  `FSIINFRATE` double DEFAULT NULL,
  `NSIINFMTYP` double DEFAULT NULL,
  `NSIINFUNIT` double DEFAULT NULL,
  `NSINODOORS` double DEFAULT NULL,
  `FSISLBDBMT` double DEFAULT NULL,
  `FSLBD1L` double DEFAULT NULL,
  `LSICLGT1NO` double DEFAULT NULL,
  `LSICLGT2NO` double DEFAULT NULL,
  `LSIWALT1NO` double DEFAULT NULL,
  `LSIWALT2NO` double DEFAULT NULL,
  `LSIFNDWTNO` double DEFAULT NULL,
  `LSIFLRTYNO` double DEFAULT NULL,
  `LSIDORTYNO` double DEFAULT NULL,
  `LSISLBTYNO` double DEFAULT NULL,
  `SSIRATENO` varchar(31) DEFAULT NULL,
  `FSIBOXLEN` double DEFAULT 0,
  `FSIBOXWID` double DEFAULT 0,
  `FSIBOXHGT` double DEFAULT 0,
  `NSILVABGAR` double DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=64500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Site`
--

DROP TABLE IF EXISTS `Site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `SZSELABEL` varchar(31) DEFAULT NULL,
  `ISECITY` double DEFAULT NULL,
  `FSEELEV` double DEFAULT NULL,
  `NSEHS` double DEFAULT NULL,
  `NSECS` double DEFAULT NULL,
  `NSECSJSDAY` double DEFAULT NULL,
  `NSEDEGDAYH` double DEFAULT NULL,
  `NSEDEGDAYC` double DEFAULT NULL,
  `FSETAMBHS` double DEFAULT NULL,
  `FSETAMBCS` double DEFAULT NULL,
  `FSEHDD65` double DEFAULT NULL,
  `FSECDH74` double DEFAULT NULL,
  `SCLIMZONE` varchar(50) DEFAULT NULL,
  `SRATENO` varchar(31) DEFAULT NULL,
  `fASHRAEWSF` double DEFAULT NULL,
  `fAveWindSpd` double DEFAULT NULL,
  `fAveAmbAirT` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=65500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Skylight`
--

DROP TABLE IF EXISTS `Skylight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Skylight` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZSKNAME` varchar(31) DEFAULT NULL,
  `FSKGLZAREA` double DEFAULT NULL,
  `NSKOR` double DEFAULT NULL,
  `FSKPITCH` double DEFAULT NULL,
  `FSKSUMSHAD` double DEFAULT NULL,
  `FSKWTRSHAD` double DEFAULT NULL,
  `NSKSURFNUM` double DEFAULT NULL,
  `LSKWINTNO` int(11) NOT NULL,
  `SSKRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=66500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Slab`
--

DROP TABLE IF EXISTS `Slab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Slab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `SZSFNAME` varchar(31) DEFAULT NULL,
  `FSFAREA` double DEFAULT NULL,
  `FSFDEP` double DEFAULT NULL,
  `FSFPER` double DEFAULT NULL,
  `FSFEXPER` double DEFAULT NULL,
  `FSFONPER` double DEFAULT NULL,
  `LSFSLABTNO` int(11) NOT NULL,
  `SSFRATENO` varchar(31) DEFAULT NULL,
  `nSFLoc` int(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=67500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SlabType`
--

DROP TABLE IF EXISTS `SlabType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SlabType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LSTSTNO` int(11) NOT NULL,
  `SSTTYPE` varchar(31) DEFAULT NULL,
  `FSTPINS` double DEFAULT NULL,
  `FSTUINS` double DEFAULT NULL,
  `FSTFUWID` double DEFAULT NULL,
  `NSTRADIANT` double DEFAULT NULL,
  `FSTPINSDEP` double DEFAULT NULL,
  `SSTNOTE` varchar(255) DEFAULT NULL,
  `NSTINSGRDE` int(11) DEFAULT 0,
  `NSTFLRCVR` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=68500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SunSpace`
--

DROP TABLE IF EXISTS `SunSpace`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SunSpace` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL,
  `FSSRFAREA` double DEFAULT NULL,
  `FSSRFINS` double DEFAULT NULL,
  `FSSAGWAREA` double DEFAULT NULL,
  `FSSAGWINS` double DEFAULT NULL,
  `FSSBGWAREA` double DEFAULT NULL,
  `FSSBGWINS` double DEFAULT NULL,
  `FSSAREA` double DEFAULT NULL,
  `FSSFRMINS` double DEFAULT NULL,
  `FSSSLBPER` double DEFAULT NULL,
  `FSSSLBDEP` double DEFAULT NULL,
  `FSSSLBTHK` double DEFAULT NULL,
  `FSSSLBPINS` double DEFAULT NULL,
  `FSSSLBUINS` double DEFAULT NULL,
  `SSSRATENO` varchar(31) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=69500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UtilRate`
--

DROP TABLE IF EXISTS `UtilRate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UtilRate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LURURNO` int(11) NOT NULL,
  `SURNAME` varchar(31) DEFAULT NULL,
  `NURFUELTYP` double DEFAULT NULL,
  `NURUNITS` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=70500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Version`
--

DROP TABLE IF EXISTS `Version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Version` (
  `lID` int(11) NOT NULL AUTO_INCREMENT,
  `lVersion` int(11) DEFAULT 0,
  `lMinor` int(11) DEFAULT 0,
  PRIMARY KEY (`lID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=71500;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Support for 16.3.3
INSERT INTO `Version` (`lID`, `lVersion`, `lMinor`) VALUES (1, 31, 21);

--
-- Table structure for table `WallType`
--

DROP TABLE IF EXISTS `WallType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `WallType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LWTWTNO` int(11) NOT NULL,
  `FWTSTUDWDT` double DEFAULT NULL,
  `FWTSTUDDPT` double DEFAULT NULL,
  `FWTSTUDSPG` double DEFAULT NULL,
  `FWTGYPTHK` double DEFAULT NULL,
  `FWTCONTINS` double DEFAULT NULL,
  `FWTCVTYINS` double DEFAULT NULL,
  `FWTCINSTHK` double DEFAULT NULL,
  `FWTBLCKINS` double DEFAULT NULL,
  `NWTCNTNTYP` double DEFAULT NULL,
  `LWTCOMPNO` double DEFAULT NULL,
  `BWTQFVALID` double DEFAULT NULL,
  `FWTFF` double DEFAULT NULL,
  `BWTDFLTFF` int(11) DEFAULT NULL,
  `SWTNOTE` varchar(255) DEFAULT NULL,
  `NWTINSGRDE` int(11) DEFAULT NULL,
  PRIMARY KEY (`LWTWTNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=72500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Window`
--

DROP TABLE IF EXISTS `Window`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Window` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LBLDGNO` int(11) NOT NULL DEFAULT 0,
  `SZWDNAME` varchar(31) DEFAULT NULL,
  `FWDAREA` double DEFAULT NULL,
  `NWDOR` double DEFAULT NULL,
  `FWDSUMSHAD` double DEFAULT NULL,
  `FWDWTRSHAD` double DEFAULT NULL,
  `NWDSURFNUM` double DEFAULT NULL,
  `NWDSURFTYP` double DEFAULT NULL,
  `LWDWINTNO` int(11) DEFAULT NULL,
  `SWDRATENO` varchar(31) DEFAULT NULL,
  `FWDOHDEPTH` double DEFAULT NULL,
  `FWDOHTOTOP` double DEFAULT NULL,
  `FWDOHTOBTM` double DEFAULT NULL,
  `FWDADJSUM` double DEFAULT NULL,
  `FWDADJWTR` double DEFAULT NULL,
  `nWDOperate` int(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=73500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WlhpType`
--

DROP TABLE IF EXISTS `WlhpType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `WlhpType` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `lBldgRunNo` int(11) DEFAULT NULL,
  `lWlhpEqKey` int(11) DEFAULT NULL,
  `sName` varchar(31) DEFAULT NULL,
  `fHtgEff` double DEFAULT NULL,
  `fHtgCap` double DEFAULT NULL,
  `fClgEff` double DEFAULT NULL,
  `fClgCap` double DEFAULT NULL,
  `fClgSHF` int(11) DEFAULT NULL,
  `sNote` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=74500;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WndwType`
--

DROP TABLE IF EXISTS `WndwType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `WndwType` (
  `LBLDGRUNNO` int(11) DEFAULT NULL,
  `LWDTWINNO` int(11) NOT NULL,
  `SWDTTYPE` varchar(31) DEFAULT NULL,
  `FWDTSHGC` double DEFAULT NULL,
  `FWDTUVALUE` double DEFAULT NULL,
  `SWDTNOTE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`LWDTWINNO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=75500;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-04-08  9:44:50
