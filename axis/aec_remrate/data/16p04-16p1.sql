USE remrate;

ALTER TABLE `Equip`
    ADD COLUMN `nEIDHUCAPWT` int(11) NULL DEFAULT NULL,
    ADD COLUMN `fEIWHFFlow` DOUBLE DEFAULT NULL,
    ADD COLUMN `fEIWHFWatts` DOUBLE DEFAULT NULL;

ALTER TABLE `EqInst`
    ADD COLUMN `fCWLoadSrvd` DOUBLE DEFAULT NULL,
    ADD COLUMN `fDWLoadSrvd` DOUBLE DEFAULT NULL,
    ADD COLUMN `fDhuLoadSrvd` DOUBLE DEFAULT NULL,
    ADD COLUMN `fMVHtgLoadSrvd` DOUBLE DEFAULT NULL,
    ADD COLUMN `fMVClgLoadSrvd` DOUBLE DEFAULT NULL,
    ADD COLUMN `nDwellUnitsDhw` int(11) DEFAULT NULL,
    ADD COLUMN `lDhuEqKey` int(11) DEFAULT NULL,
    ADD COLUMN `lSharedEqKey` int(11) DEFAULT NULL,
    ADD COLUMN `nPrecondSharedMV` int(11) DEFAULT NULL;

ALTER TABLE `DhwDistrib` ADD COLUMN `nHomesServed` int(11) DEFAULT NULL;
ALTER TABLE `MandReq` ADD COLUMN `nMRNGBS15` int(11) DEFAULT NULL;
ALTER TABLE `Slab` ADD COLUMN `nSFLoc` int(20) DEFAULT NULL;
ALTER TABLE `PhotoVol` ADD COLUMN `nPVNumBeds` int(20) DEFAULT NULL;
ALTER TABLE `Window` ADD COLUMN `nWDOperate` int(20) DEFAULT NULL;

ALTER TABLE `LightApp`
    ADD COLUMN `nLAFanCnt` int(20) DEFAULT NULL,
    ADD COLUMN `nLAOvnLoc` int(20) DEFAULT NULL,
    ADD COLUMN `nLADryUnit` int(20) DEFAULT NULL,
    ADD COLUMN `nLAWashPre` int(20) DEFAULT NULL,
    ADD COLUMN `nLAWashUnit` int(20) DEFAULT NULL,
    ADD COLUMN `nLAWashDhw` int(20) DEFAULT NULL,
    ADD COLUMN `nLAWashLoad` int(20) DEFAULT NULL,
    ADD COLUMN `fLAWashIWF` DOUBLE DEFAULT NULL,
    ADD COLUMN `nLADishLoc` int(20) DEFAULT NULL,
    ADD COLUMN `nLADishPre` int(20) DEFAULT NULL,
    ADD COLUMN `nLADishDhw` int(20) DEFAULT NULL,
    ADD COLUMN `fLADishElec` DOUBLE DEFAULT NULL,
    ADD COLUMN `fLADishGas` DOUBLE DEFAULT NULL,
    ADD COLUMN `fLADishGCst` DOUBLE DEFAULT NULL,
    ADD COLUMN `nLADishLoad` int(20) DEFAULT NULL;

CREATE TABLE `DehumidType`
(
    `id`          bigint(20) NOT NULL AUTO_INCREMENT,
    `lBldgRunNo`  int(11)      DEFAULT NULL,
    `lDhuEqKey`   int(11)      DEFAULT NULL,
    `sName`       varchar(31)  DEFAULT NULL,
    `nSystem`     int(11)      DEFAULT NULL,
    `nFuel`       int(11)      DEFAULT NULL,
    `fCapacity`   double       DEFAULT NULL,
    `fEfficiency` double       DEFAULT NULL,
    `sNote`       varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `MechVent`
(
    `id`          bigint(20) NOT NULL AUTO_INCREMENT,
    `lBldgRunNo`  int(11)     DEFAULT NULL,
    `lBldgNo`     int(11)     DEFAULT NULL,
    `sMVRateNo`   varchar(31) DEFAULT NULL,
    `sMVName`     varchar(31) DEFAULT NULL,
    `nMVType`     int(11)     DEFAULT NULL,
    `fMVRate`     double      DEFAULT NULL,
    `nMVHrsDay`   int(11)     DEFAULT NULL,
    `fMVFanPwr`   double      DEFAULT NULL,
    `fMVASRE`     double      DEFAULT NULL,
    `fMVATRE`     double      DEFAULT NULL,
    `nMVNotMsrd`  int(11)     DEFAULT NULL,
    `nMVWattDflt` int(11)     DEFAULT NULL,
    `nMVFanMotor` int(11)     DEFAULT NULL,
    `nMVDuctNo`   int(11)     DEFAULT NULL,
    `nMVShrdMF`   int(11)     DEFAULT NULL,
    `nMVHtgNo`    int(11)     DEFAULT NULL,
    `nMVClgNo`    int(11)     DEFAULT NULL,
    `fMVShrdCFM`  double      DEFAULT NULL,
    `fMVOAPct`    double      DEFAULT NULL,
    `fMVRecirc`   double      DEFAULT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `SharedType`
(
    `id`              bigint(20) NOT NULL AUTO_INCREMENT,
    `lBldgRunNo`      int(11)      DEFAULT NULL,
    `lSharedEqKey`    int(11)      DEFAULT NULL,
    `sName`           varchar(31)  DEFAULT NULL,
    `nSystem`         int(11)      DEFAULT NULL,
    `nFuel`           int(11)      DEFAULT NULL,
    `fRatedEff`       double       DEFAULT NULL,
    `nRatedEffUnit`   int(11)      DEFAULT NULL,
    `fBoilerCap`      double       DEFAULT NULL,
    `fChillerCap`     double       DEFAULT NULL,
    `fGndLoopCap`     double       DEFAULT NULL,
    `fGndLoopPump`    double       DEFAULT NULL,
    `nBlgLoopUnits`   int(11)      DEFAULT NULL,
    `fBlgLoopPumpPwr` double       DEFAULT NULL,
    `nTerminalType`   int(11)      DEFAULT NULL,
    `fFanCoil`        double       DEFAULT NULL,
    `sNote`           varchar(255) DEFAULT NULL,
    `lHtgEqKey`       int(11)      DEFAULT NULL,
    `lClgEqKey`       int(11)      DEFAULT NULL,
    `lGshpEqKey`      int(11)      DEFAULT NULL,
    `lWlhpEqKey`      int(11)      DEFAULT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `WlhpType`
(
    `id`         bigint(20) NOT NULL AUTO_INCREMENT,
    `lBldgRunNo` int(11)      DEFAULT NULL,
    `lWlhpEqKey` int(11)      DEFAULT NULL,
    `sName`      varchar(31)  DEFAULT NULL,
    `fHtgEff`    double       DEFAULT NULL,
    `fHtgCap`    double       DEFAULT NULL,
    `fClgEff`    double       DEFAULT NULL,
    `fClgCap`    double       DEFAULT NULL,
    `fClgSHF`    int(11)      DEFAULT NULL,
    `sNote`      varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`)
);

UPDATE `Version` SET `lMinor` = 17 WHERE `lID` = 1;
