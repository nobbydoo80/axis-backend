
DELIMITER $$
DROP TRIGGER IF EXISTS `after_simulation_copy_trigger` $$
CREATE TRIGGER after_simulation_copy_trigger
    AFTER INSERT on BuildRun FOR EACH ROW
    BEGIN

    -- Trigger #: 1 of 75 Source: BuildRun Target: remrate_data_simulation --

    DECLARE user_name varchar(32);
    DECLARE org_id INT;
    DECLARE user_id INT;
    DECLARE major_id INT;
    DECLARE minor_id INT;
    DECLARE lbldgrunno_id INT;
    DECLARE correct_date varchar(96);

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET correct_date=STR_TO_DATE(NEW.SBRDATE, '%m/%d/%Y %H:%i:%s');

    -- Grab the username and let's use it!
    SELECT SUBSTRING_INDEX(USER(),'@',1) INTO user_name;

    -- Figure out the org_id which holds that user..
    SELECT company_id INTO org_id FROM axis.remrate_remrateuser WHERE username=user_name;

    -- Update the user or insert him/her into our usertable.
    INSERT INTO axis.remrate_remrateuser
      (`username`, `company_id`, `is_active`, `created_on`, `last_used`)
      VALUES( user_name, org_id, '1', NOW(), NOW())
      ON DUPLICATE KEY UPDATE last_used=NOW();

    SELECT id INTO user_id FROM axis.remrate_remrateuser WHERE username=user_name;

    SELECT lVersion, lMinor INTO major_id, minor_id FROM remrate.Version WHERE lID=1;

    -- Do not push the flavor on old versions
    IF NEW.SBRPROGVER IN ('12.5', '12.99A', '13.0', '14.0', '14.1', '14.2', '14.3', '14.4', '14.4.1') THEN
      INSERT INTO axis.remrate_data_simulation
          (`company_id`, `remrate_user_id`, `lBldgRunNo`, `sBRDate`, `sBRProgVer`, `SBRProgFlvr`, `sBRRateNo`, `sBRFlag`, `lBRExpTpe`, `nInstance`) VALUES
          ( org_id, user_id, NEW.LBLDGRUNNO, correct_date, NEW.SBRPROGVER, "", NEW.SBRRATENO, NEW.SBRFLAG, NEW.LBREXPTPE, NEW.NINSTANCE );
    ELSE
       INSERT INTO axis.remrate_data_simulation
         (`company_id`, `remrate_user_id`, `sBRDate`, `lBldgRunNo`, `sBRProgVer`, `SBRProgFlvr`, `sBRRateNo`, `sBRFlag`, `lBRExpTpe`, `nInstance`, `sBRUdrName`, `sBRUdrChk`) VALUES
         ( org_id, user_id, correct_date, NEW.LBLDGRUNNO, NEW.SBRPROGVER, NEW.SBRPROGFLVR, NEW.SBRRATENO, NEW.SBRFLAG, NEW.LBREXPTPE, NEW.NINSTANCE, NEW.SBRUDRNAME, NEW.SBRUDRCHK );
    END IF;


    INSERT INTO axis.remrate_data_datatracker
      (`lBldgRunNo`, `version`, `db_major_version`, `db_minor_version`, `simulation_id`, `company_id`, `remrate_user_id`, `user_host`, `created_on`, `last_update`, `status`) VALUES
      ( NEW.LBLDGRUNNO, NEW.SBRPROGVER, major_id, minor_id, LAST_INSERT_ID(), org_id, user_id, USER(), NOW(), NOW(), -1);


    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_utilityrates_copy_trigger` $$
CREATE TRIGGER after_utilityrates_copy_trigger
    AFTER INSERT on UtilRate FOR EACH ROW
    BEGIN

    -- Trigger #: 2 of 75 Source: UtilRate Target: remrate_data_utilityrate --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_utilityrate
      (`simulation_id`, `lBldgRunNo`, `sURName`, `nURFuelTyp`, `lURURNo`, `nURUnits`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.SURNAME, NEW.NURFUELTYP, NEW.LURURNO, NEW.NURUNITS );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_seasonalrate_copy_trigger` $$
CREATE TRIGGER after_seasonalrate_copy_trigger
    AFTER INSERT on SeasnRat FOR EACH ROW
    BEGIN

    -- Trigger #: 3 of 75 Source: SeasnRat Target: remrate_data_seasonalrate --

    DECLARE utility_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lURURNo
    SELECT axis.remrate_data_utilityrate.id INTO utility_id FROM axis.remrate_data_utilityrate
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_utilityrate.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_utilityrate.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_utilityrate.lURURNo = NEW.LSRURNO AND axis.remrate_data_datatracker.status = -1);

    INSERT INTO axis.remrate_data_seasonalrate
      (`rate_id`, `simulation_id`, `lBldgRunNo`, `lSRURNo`, `lSRSRNo`, `nSRStrtMth`, `nSRStopMth`, `fSRSvcChrg`) VALUES
      ( utility_id, sim_id, NEW.LBLDGRUNNO, NEW.LSRURNO, NEW.lSRSRNo, NEW.NSRSTRTMTH, NEW.NSRSTOPMTH, NEW.FSRSVCCHRG );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_block_copy_trigger` $$
CREATE TRIGGER after_block_copy_trigger
    AFTER INSERT on Block FOR EACH ROW
    BEGIN

    -- Trigger #: 4 of 75 Source: Block Target: remrate_data_block --

    DECLARE season_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lSRSRNo
    SELECT axis.remrate_data_seasonalrate.id INTO season_id FROM axis.remrate_data_seasonalrate
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_seasonalrate.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_seasonalrate.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_seasonalrate.lSRSRNo = NEW.LBLSRNO AND axis.remrate_data_datatracker.status = -1);

    INSERT INTO axis.remrate_data_block
      (`seasonal_rate_id`, `simulation_id`, `lBldgRunNo`, `lBLSRNo`, `fBLBlckMax`, `fBLRate`) VALUES
      ( season_id, sim_id, NEW.LBLDGRUNNO, NEW.LBLSRNO, NEW.FBLBLCKMAX, NEW.FBLRATE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_building_copy_trigger` $$
CREATE TRIGGER after_building_copy_trigger
    AFTER INSERT on Building FOR EACH ROW
    BEGIN

    -- Trigger #: 5 of 75 Source: Building Target: remrate_data_building --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgno_id INT;

    DECLARE user_name varchar(32);
    DECLARE org_id INT;
    DECLARE user_id INT;
    DECLARE major_id INT;
    DECLARE minor_id INT;
    DECLARE lbldgrunno_id INT;
    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    -- Grab the username and let's use it!
    SELECT SUBSTRING_INDEX(USER(),'@',1) INTO user_name;

    -- Figure out the org_id which holds that user..
    SELECT company_id INTO org_id FROM axis.remrate_remrateuser WHERE username=user_name;

    -- Update the user or insert him/her into our usertable.
    INSERT INTO axis.remrate_remrateuser
      (`username`, `company_id`, `is_active`, `created_on`, `last_used`)
      VALUES( user_name, org_id, '1', NOW(), NOW())
      ON DUPLICATE KEY UPDATE last_used=NOW();

    SELECT id INTO user_id FROM axis.remrate_remrateuser WHERE username=user_name;

    SELECT lVersion, lMinor INTO major_id, minor_id FROM remrate.Version WHERE lID=1;

    SET lbldgno_id=NEW.LBLDGNO;

    -- Figure out the lBldgRunNo
    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      lBldgRunNo=NEW.lBldgRunNo AND lBldgNo IS NULL AND STATUS=-1 ORDER BY -id LIMIT 1;
    SELECT id into user_id FROM axis.remrate_remrateuser WHERE username=user_name;

    -- Do not push the window and wall ratios < 14.3
    IF version_id IN ('12.5', '12.99A', '13.0', '14.0', '14.1', '14.2') THEN
       INSERT INTO axis.remrate_data_building
         (`company_id`, `remrate_user_id`, `simulation_id`, `created_on`, `last_update`, `sync_status`, `user_host`, `lBldgRunNo`, `lBldgNo`, `sBUBldgNam`, `sBURateNo`, `nBUBlgType`, `fCeilAtRo`, `fCeilAtAr`, `fCeilCaRo`, `fCeilCaAr`, `fAGWCORo`, `fAGWCOAr`, `fAGWBORo`, `fAGWBOAr`, `fJoiCORo`, `fJoiCOAr`, `fJoiBORo`, `fJoiBOAr`, `fFndCORo`, `fFndCOAr`, `fFndBORo`, `fFndBOAr`, `fFrFCARo`, `fFrFCAAr`, `fWinCORo`, `fWinCOAr`, `fSkyCORo`, `fSkyCOAr`, `fDorCORo`, `fDorCOAr`, `fAMThDry`, `fWinWall`, `fWinFloor`, `sNotes`) VALUES
         ( org_id, user_id, sim_id, NOW(), NOW(), -1, USER(), NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SBUBLDGNAM, NEW.SBURATENO, NEW.NBUBLGTYPE, NEW.FCEILATRO, NEW.FCEILATAR, NEW.FCEILCARO, NEW.FCEILCAAR, NEW.FAGWCORO, NEW.FAGWCOAR, NEW.FAGWBORO, NEW.FAGWBOAR, NEW.FJOICORO, NEW.FJOICOAR, NEW.FJOIBORO, NEW.FJOIBOAR, NEW.FFNDCORO, NEW.FFNDCOAR, NEW.FFNDBORO, NEW.FFNDBOAR, NEW.FFRFCARO, NEW.FFRFCAAR, NEW.FWINCORO, NEW.FWINCOAR, NEW.FSKYCORO, NEW.FSKYCOAR, NEW.FDORCORO, NEW.FDORCOAR, NEW.FAMTHDRY, NULL, NULL, NEW.sNotes );
    ELSE
       INSERT INTO axis.remrate_data_building
         (`company_id`, `remrate_user_id`, `simulation_id`, `created_on`, `last_update`, `sync_status`, `user_host`, `lBldgRunNo`, `lBldgNo`, `sBUBldgNam`, `sBURateNo`, `nBUBlgType`, `fCeilAtRo`, `fCeilAtAr`, `fCeilCaRo`, `fCeilCaAr`, `fAGWCORo`, `fAGWCOAr`, `fAGWBORo`, `fAGWBOAr`, `fJoiCORo`, `fJoiCOAr`, `fJoiBORo`, `fJoiBOAr`, `fFndCORo`, `fFndCOAr`, `fFndBORo`, `fFndBOAr`, `fFrFCARo`, `fFrFCAAr`, `fWinCORo`, `fWinCOAr`, `fSkyCORo`, `fSkyCOAr`, `fDorCORo`, `fDorCOAr`, `fAMThDry`, `fWinWall`, `fWinFloor`, `sNotes`, `SCEILATDOM`, `SCEILSADOM`, `SCEILCADOM`, `SAGWDOM`, `SFNDWDOM`, `SSLABDOM`, `SFRFDOM`, `SWINDOM`, `SDUCTDOM`, `SHTGDOM`, `SCLGDOM`, `SDHWDOM`) VALUES
         ( org_id, user_id, sim_id, NOW(), NOW(), -1, USER(), NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SBUBLDGNAM, NEW.SBURATENO, NEW.NBUBLGTYPE, NEW.FCEILATRO, NEW.FCEILATAR, NEW.FCEILCARO, NEW.FCEILCAAR, NEW.FAGWCORO, NEW.FAGWCOAR, NEW.FAGWBORO, NEW.FAGWBOAR, NEW.FJOICORO, NEW.FJOICOAR, NEW.FJOIBORO, NEW.FJOIBOAR, NEW.FFNDCORO, NEW.FFNDCOAR, NEW.FFNDBORO, NEW.FFNDBOAR, NEW.FFRFCARO, NEW.FFRFCAAR, NEW.FWINCORO, NEW.FWINCOAR, NEW.FSKYCORO, NEW.FSKYCOAR, NEW.FDORCORO, NEW.FDORCOAR, NEW.FAMTHDRY, NEW.FWINWALL, NEW.FWINFLOOR, NEW.sNotes, NEW.SCEILATDOM, NEW.SCEILSADOM, NEW.SCEILCADOM, NEW.SAGWDOM, NEW.SFNDWDOM, NEW.SSLABDOM, NEW.SFRFDOM, NEW.SWINDOM, NEW.SDUCTDOM, NEW.SHTGDOM, NEW.SCLGDOM, NEW.SDHWDOM );
    END IF;


    UPDATE axis.remrate_data_datatracker SET
      `lBldgNo`=NEW.LBLDGNO, `building_id`=LAST_INSERT_ID(),
      `last_update`=NOW(), `status`=0 WHERE
      `lBldgRunNo`=NEW.lBldgRunNo AND lBldgNo IS NULL AND `status`=-1 ORDER BY -id LIMIT 1;


    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_project_copy_trigger` $$
CREATE TRIGGER after_project_copy_trigger
    AFTER INSERT on ProjInfo FOR EACH ROW
    BEGIN

    -- Trigger #: 6 of 75 Source: ProjInfo Target: remrate_data_project --

    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgno_id INT;

    SET lbldgno_id=NEW.LBLDGNO;

    SELECT building_id, version INTO bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Do not push the builder permits < 13.0
    IF version_id IN ('12.5', '12.99A', '13.0') THEN
        INSERT INTO axis.remrate_data_project
          (`building_id`, `lBldgRunNo`, `lBldgNo`, `sPIBlgName`, `sPIPOwner`, `sPIStreet`, `sPICity`, `sPIState`, `sPIZip`, `sPIPhone`, `sPIBldrPrmt`, `SPIBuilder`, `sPIBldrStr`, `sPIBldrCty`, `sPIBldrEml`, `sPIBldrPho`, `sPIModel`, `sPIBldrDev`, `sPIRatOrg`, `sPIRatStr`, `sPIRatCity`, `sPIRatSt`, `sPIRatZip`, `sPIRatPhon`, `sPIRatWeb`, `sPIPRVDRID`, `sPIRatName`, `sPIRaterNo`, `sPIRatEMal`, `sPIRatDate`, `sPIRatngNo`, `sPIRatType`, `sPIRatReas`, `SPISAMSETID`, `sPIREGID`) VALUES
          ( bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SPIBLGNAME, NEW.SPIPOWNER, NEW.SPISTREET, NEW.SPICITY, NEW.SPISTATE, NEW.SPIZIP, NEW.SPIPHONE, "", NEW.SPIBUILDER, NEW.SPIBLDRSTR, NEW.SPIBLDRCTY, NEW.SPIBLDREML, NEW.SPIBLDRPHO, NEW.SPIMODEL, NEW.SPIBLDRDEV, NEW.SPIRATORG, NEW.SPIRATSTR, NEW.SPIRATCITY, NEW.SPIRATST, NEW.SPIRATZIP, NEW.SPIRATPHON, NEW.SPIRATWEB, NEW.SPIPRVDRID, NEW.SPIRATNAME, NEW.SPIRATERNO, NEW.SPIRATEMAL, NEW.SPIRATDATE, NEW.SPIRATNGNO, NEW.SPIRATTYPE, NEW.SPIRATREAS, NEW.SPISAMSETID, NEW.SPIREGID );
    ELSE
       INSERT INTO axis.remrate_data_project
         (`building_id`, `lBldgRunNo`, `lBldgNo`, `sPIBlgName`, `sPIPOwner`, `sPIStreet`, `sPICity`, `sPIState`, `sPIZip`, `sPIPhone`, `sPIBldrPrmt`, `SPIBuilder`, `sPIBldrStr`, `sPIBldrCty`, `sPIBldrEml`, `sPIBldrPho`, `sPIModel`, `sPIBldrDev`, `sPIRatOrg`, `sPIRatStr`, `sPIRatCity`, `sPIRatSt`, `sPIRatZip`, `sPIRatPhon`, `sPIRatWeb`, `sPIPRVDRID`, `sPIRatName`, `sPIRaterNo`, `sPIRatEMal`, `sPIRatDate`, `sPIRatngNo`, `sPIRatType`, `sPIRatReas`, `sPIVer1Name`, `sPIVer1ID`, `sPIVer2Name`, `sPIVer2ID`, `sPIVer3Name`, `sPIVer3ID`, `sPIVer4Name`, `sPIVer4ID`, `SPISAMSETID`, `sPIREGID`, `sPIRegDate`, `sPIPrmtDate`) VALUES
         ( bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SPIBLGNAME, NEW.SPIPOWNER, NEW.SPISTREET, NEW.SPICITY, NEW.SPISTATE, NEW.SPIZIP, NEW.SPIPHONE, NEW.SPIBLDRPRMT, NEW.SPIBUILDER, NEW.SPIBLDRSTR, NEW.SPIBLDRCTY, NEW.SPIBLDREML, NEW.SPIBLDRPHO, NEW.SPIMODEL, NEW.SPIBLDRDEV, NEW.SPIRATORG, NEW.SPIRATSTR, NEW.SPIRATCITY, NEW.SPIRATST, NEW.SPIRATZIP, NEW.SPIRATPHON, NEW.SPIRATWEB, NEW.SPIPRVDRID, NEW.SPIRATNAME, NEW.SPIRATERNO, NEW.SPIRATEMAL, NEW.SPIRATDATE, NEW.SPIRATNGNO, NEW.SPIRATTYPE, NEW.SPIRATREAS, NEW.SPIVER1NAME, NEW.SPIVER1ID, NEW.SPIVER2NAME, NEW.SPIVER2ID, NEW.SPIVER3NAME, NEW.SPIVER3ID, NEW.SPIVER4NAME, NEW.SPIVER4ID, NEW.SPISAMSETID, NEW.SPIREGID, NEW.SPIREGDATE, NEW.SPIPRMTDATE );
    END IF;

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_bldginfo_copy_trigger` $$
CREATE TRIGGER after_bldginfo_copy_trigger
    AFTER INSERT on BldgInfo FOR EACH ROW
    BEGIN

    -- Trigger #: 7 of 75 Source: BldgInfo Target: remrate_data_buildinginfo --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_buildinginfo
      (`simulation_id`, `lBldgRunNo`, `lBldgNo`, `fBIVolume`, `fBIACond`, `nBIHType`, `nBILType`, `nBIStories`, `nBIFType`, `nBIBeds`, `nBIUnits`, `sBIRateNo`, `nBICType`, `nBIYearBlt`, `nBIThBndry`, `nBIStoryWCB`, `NBIINFLTVOL`, `nBITotalStories`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.FBIVOLUME, NEW.FBIACOND, NEW.NBIHTYPE, NEW.NBILTYPE, NEW.NBISTORIES, NEW.NBIFTYPE, NEW.NBIBEDS, NEW.NBIUNITS, NEW.SBIRATENO, NEW.NBICTYPE, NEW.NBIYEARBLT, NEW.NBITHBNDRY, NEW.NBISTORYWCB, NEW.NBIINFLTVOL, NEW.nBITotalStories );


    UPDATE axis.remrate_data_building SET
      `building_info_id`=LAST_INSERT_ID() WHERE
      `lBldgRunNo`=NEW.lBldgRunNo AND `lBldgNo`=NEW.lBldgNo AND `simulation_id`=sim_id;


    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_foundationwalltype_copy_trigger` $$
CREATE TRIGGER after_foundationwalltype_copy_trigger
    AFTER INSERT on FndwType FOR EACH ROW
    BEGIN

    -- Trigger #: 8 of 75 Source: FndwType Target: remrate_data_foundationwalltype --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_foundationwalltype
      (`simulation_id`, `lBldgRunNo`, `lFWTWTNo`, `sFWTType`, `nFWTType`, `nFWTStdTyp`, `nFWTInsGrd`, `fFWTMasThk`, `fFWTExtIns`, `fFWTExInsT`, `fFWTExInsB`, `nFWTEInTTp`, `nFWTEInBTp`, `fFWTInInCt`, `fFWTInInFC`, `fFWTInInsT`, `fFWTInInsB`, `nFWTIInTTp`, `nFWTIInBTp`, `sFWTNote`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LFWTWTNO, NEW.SFWTTYPE, NEW.NFWTTYPE, NEW.NFWTSTDTYP, NEW.NFWTINSGRD, NEW.FFWTMASTHK, NEW.FFWTEXTINS, NEW.FFWTEXINST, NEW.FFWTEXINSB, NEW.NFWTEINTTP, NEW.NFWTEINBTP, NEW.FFWTININCT, NEW.FFWTININFC, NEW.FFWTININST, NEW.FFWTININSB, NEW.NFWTIINTTP, NEW.NFWTIINBTP, NEW.SFWTNOTE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_foundationwall_copy_trigger` $$
CREATE TRIGGER after_foundationwall_copy_trigger
    AFTER INSERT on FndWall FOR EACH ROW
    BEGIN

    -- Trigger #: 9 of 75 Source: FndWall Target: remrate_data_foundationwall --

    DECLARE foundation_wall_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lFWTWTNo
    SELECT axis.remrate_data_foundationwalltype.id INTO foundation_wall_id FROM axis.remrate_data_foundationwalltype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_foundationwalltype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_foundationwalltype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_foundationwalltype.lFWTWTNo = NEW.LFWFWTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_foundationwall
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szFWName`, `fFWLength`, `fFWHeight`, `fFWDBGrade`, `fFWHAGrade`, `nFWLoc`, `lFWFWTNo`, `sFWRateNo`) VALUES
      ( foundation_wall_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZFWNAME, NEW.FFWLENGTH, NEW.FFWHEIGHT, NEW.FFWDBGRADE, NEW.FFWHAGRADE, NEW.NFWLOC, NEW.LFWFWTNO, NEW.SFWRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_slabtype_copy_trigger` $$
CREATE TRIGGER after_slabtype_copy_trigger
    AFTER INSERT on SlabType FOR EACH ROW
    BEGIN

    -- Trigger #: 10 of 75 Source: SlabType Target: remrate_data_slabtype --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_slabtype
      (`simulation_id`, `lBldgRunNo`, `lSTSTNo`, `sSTType`, `fSTPIns`, `nSTRadiant`, `fSTUIns`, `fSTFUWid`, `fSTPInsDep`, `sSTNote`, `nSTInsGrde`, `nSTFlrCvr`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LSTSTNO, NEW.SSTTYPE, NEW.FSTPINS, NEW.NSTRADIANT, NEW.FSTUINS, NEW.FSTFUWID, NEW.FSTPINSDEP, NEW.SSTNOTE, NEW.NSTINSGRDE, NEW.NSTFLRCVR );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_slab_copy_trigger` $$
CREATE TRIGGER after_slab_copy_trigger
    AFTER INSERT on Slab FOR EACH ROW
    BEGIN

    -- Trigger #: 11 of 75 Source: Slab Target: remrate_data_slab --

    DECLARE slab_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lSTSTNo
    SELECT axis.remrate_data_slabtype.id INTO slab_id FROM axis.remrate_data_slabtype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_slabtype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_slabtype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_slabtype.lSTSTNo = NEW.LSFSLABTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_slab
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szSFName`, `lSFSlabTNo`, `fSFArea`, `fSFDep`, `fSFPer`, `fSFExPer`, `fSFOnPer`, `sSFRateNo`, `nSFLoc`) VALUES
      ( slab_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZSFNAME, NEW.LSFSLABTNO, NEW.FSFAREA, NEW.FSFDEP, NEW.FSFPER, NEW.FSFEXPER, NEW.FSFONPER, NEW.SSFRATENO, NEW.nSFLoc );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_compositeinsulation_copy_trigger` $$
CREATE TRIGGER after_compositeinsulation_copy_trigger
    AFTER INSERT on CompType FOR EACH ROW
    BEGIN

    -- Trigger #: 12 of 75 Source: CompType Target: remrate_data_compositetype --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_compositetype
      (`simulation_id`, `lBldgRunNo`, `lTCTTCTTNo`, `sTCTType`, `fTCTUo`, `nTCTQFVal`, `sTCTLNm1`, `sTCTLNm2`, `sTCTLNm3`, `sTCTLNm4`, `sTCTLNm5`, `sTCTLNm6`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LTCTTCTTNO, NEW.STCTTYPE, NEW.FTCTUO, NEW.NTCTQFVAL, NEW.STCTLNM1, NEW.STCTLNM2, NEW.STCTLNM3, NEW.STCTLNM4, NEW.STCTLNM5, NEW.STCTLNM6 );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_heatpath_copy_trigger` $$
CREATE TRIGGER after_heatpath_copy_trigger
    AFTER INSERT on HeatPath FOR EACH ROW
    BEGIN

    -- Trigger #: 13 of 75 Source: HeatPath Target: remrate_data_heatpath --

    DECLARE comp_type_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lTCTTCTTNo
    SELECT axis.remrate_data_compositetype.id INTO comp_type_id FROM axis.remrate_data_compositetype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_compositetype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_compositetype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_compositetype.lTCTTCTTNo = NEW.LHPTCTTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_heatpath
      (`composite_type_id`, `simulation_id`, `lBldgRunNo`, `lHPTCTTNo`, `sHPPthName`, `fHPPthArea`, `fHPPthRVal`, `fHPLRval1`, `fHPLRval2`, `fHPLRval3`, `fHPLRval4`, `fHPLRval5`, `fHPLRval6`, `fHPLRval7`, `fHPLRval8`) VALUES
      ( comp_type_id, sim_id, NEW.LBLDGRUNNO, NEW.LHPTCTTNO, NEW.SHPPTHNAME, NEW.FHPPTHAREA, NEW.FHPPTHRVAL, NEW.FHPLRVAL1, NEW.FHPLRVAL2, NEW.FHPLRVAL3, NEW.FHPLRVAL4, NEW.FHPLRVAL5, NEW.FHPLRVAL6, NEW.FHPLRVAL7, NEW.FHPLRVAL8 );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_ceilingtype_copy_trigger` $$
CREATE TRIGGER after_ceilingtype_copy_trigger
    AFTER INSERT on CeilType FOR EACH ROW
    BEGIN

    -- Trigger #: 14 of 75 Source: CeilType Target: remrate_data_ceilingtype --

    DECLARE comp_type_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lTCTTCTTNo
    SELECT axis.remrate_data_compositetype.id INTO comp_type_id FROM axis.remrate_data_compositetype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_compositetype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_compositetype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_compositetype.lTCTTCTTNo = NEW.LCTCOMPNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_ceilingtype
      (`composite_type_id`, `simulation_id`, `lBldgRunNo`, `lCTCTNo`, `lCTCompNo`, `sCTNote`, `nCTCeilTyp`, `fCTContIns`, `fCTCvtyIns`, `fCTGypThk`, `fCTRftrWdt`, `fCTRftrHgt`, `fCTRftrSpc`, `fCTCInsThk`, `bCTQFValid`, `NCTINSTYP`, `FCTUNRDEP`, `FCTUNRRVL`, `FCTCLGWID`, `FCTCLGRSE`, `FCTTRSHGT`, `FCTHELHGT`, `FCTVNTSPC`, `NCTQFTYP`, `FCTFF`, `BCTDFLTFF`, `NCTINSGRDE`) VALUES
      ( comp_type_id, sim_id, NEW.LBLDGRUNNO, NEW.LCTCTNO, NEW.LCTCOMPNO, NEW.SCTNOTE, NEW.NCTCEILTYP, NEW.FCTCONTINS, NEW.FCTCVTYINS, NEW.FCTGYPTHK, NEW.FCTRFTRWDT, NEW.FCTRFTRHGT, NEW.FCTRFTRSPC, NEW.FCTCINSTHK, NEW.BCTQFVALID, NEW.NCTINSTYP, NEW.FCTUNRDEP, NEW.FCTUNRRVL, NEW.FCTCLGWID, NEW.FCTCLGRSE, NEW.FCTTRSHGT, NEW.FCTHELHGT, NEW.FCTVNTSPC, NEW.NCTQFTYP, NEW.FCTFF, NEW.BCTDFLTFF, NEW.NCTINSGRDE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_roof_copy_trigger` $$
CREATE TRIGGER after_roof_copy_trigger
    AFTER INSERT on Roof FOR EACH ROW
    BEGIN

    -- Trigger #: 15 of 75 Source: Roof Target: remrate_data_roof --

    DECLARE ctype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lCTCTNo
    SELECT axis.remrate_data_ceilingtype.id INTO ctype_id FROM axis.remrate_data_ceilingtype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_ceilingtype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_ceilingtype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_ceilingtype.lCTCTNo = NEW.LROCEILTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_roof
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `lROCeilTNo`, `szROName`, `nROCol`, `fROArea`, `nROClay`, `nROVent`, `nRORadBar`, `nROType`, `fROUo`, `sRORateNo`, `fRORoofArea`) VALUES
      ( ctype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.LROCEILTNO, NEW.SZRONAME, NEW.NROCOL, NEW.FROAREA, NEW.NROCLAY, NEW.NROVENT, NEW.NRORADBAR, NEW.NROTYPE, NEW.FROUO, NEW.SRORATENO, NEW.FROROOFAREA );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_walltype_copy_trigger` $$
CREATE TRIGGER after_walltype_copy_trigger
    AFTER INSERT on WallType FOR EACH ROW
    BEGIN

    -- Trigger #: 16 of 75 Source: WallType Target: remrate_data_walltype --

    DECLARE comp_type_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lTCTTCTTNo
    SELECT axis.remrate_data_compositetype.id INTO comp_type_id FROM axis.remrate_data_compositetype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_compositetype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_compositetype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_compositetype.lTCTTCTTNo = NEW.LWTCOMPNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_walltype
      (`composite_type_id`, `simulation_id`, `lWTWTNo`, `lBldgRunNo`, `lWTCompNo`, `fWTContIns`, `fWTCvtyIns`, `fWTStudWdt`, `fWTStudDpt`, `fWTStudSpg`, `fWTGypThk`, `fWTCInsThk`, `fWTBlckIns`, `nWTCntnTyp`, `bWTQFValid`, `fWTFF`, `bWTDFLTFF`, `sWTNote`, `nWTInsGrde`) VALUES
      ( comp_type_id, sim_id, NEW.LWTWTNO, NEW.LBLDGRUNNO, NEW.LWTCOMPNO, NEW.FWTCONTINS, NEW.FWTCVTYINS, NEW.FWTSTUDWDT, NEW.FWTSTUDDPT, NEW.FWTSTUDSPG, NEW.FWTGYPTHK, NEW.FWTCINSTHK, NEW.FWTBLCKINS, NEW.NWTCNTNTYP, NEW.BWTQFVALID, NEW.FWTFF, NEW.BWTDFLTFF, NEW.SWTNOTE, NEW.NWTINSGRDE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_abovegradewall_copy_trigger` $$
CREATE TRIGGER after_abovegradewall_copy_trigger
    AFTER INSERT on AGWall FOR EACH ROW
    BEGIN

    -- Trigger #: 17 of 75 Source: AGWall Target: remrate_data_abovegradewall --

    DECLARE wtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lWTWTNo
    SELECT axis.remrate_data_walltype.id INTO wtype_id FROM axis.remrate_data_walltype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_walltype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_walltype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_walltype.lWTWTNo = NEW.LAGWALLTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_abovegradewall
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szAGName`, `fAGArea`, `nAGLoc`, `nAGCol`, `fAGUo`, `lAGWallTNo`, `sAGRateNo`) VALUES
      ( wtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZAGNAME, NEW.FAGAREA, NEW.NAGLOC, NEW.NAGCOL, NEW.FAGUO, NEW.LAGWALLTNO, NEW.SAGRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_framefloortype_copy_trigger` $$
CREATE TRIGGER after_framefloortype_copy_trigger
    AFTER INSERT on FlrType FOR EACH ROW
    BEGIN

    -- Trigger #: 18 of 75 Source: FlrType Target: remrate_data_floortype --

    DECLARE comp_type_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lTCTTCTTNo
    SELECT axis.remrate_data_compositetype.id INTO comp_type_id FROM axis.remrate_data_compositetype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_compositetype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_compositetype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_compositetype.lTCTTCTTNo = NEW.NFTTCTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_floortype
      (`composite_type_id`, `simulation_id`, `lBldgRunNo`, `lFTFTNo`, `nFTTCTNo`, `fFTContIns`, `fFTCvtyIns`, `fFTJstWdt`, `fFTJstHgt`, `fFTJstSpg`, `fFTCInsThk`, `nFTCovType`, `bFTQFValid`, `NFTQFTYPE`, `FFTFLRWID`, `FFTOUTWID`, `FFTBATTHK`, `FFTBATRVL`, `FFTBLKTHK`, `FFTBLKRVL`, `NFTCNTINS`, `NFTOUTINS`, `FFTFF`, `BFTDFLTFF`, `SFTNOTE`, `nFTInsGrde`) VALUES
      ( comp_type_id, sim_id, NEW.LBLDGRUNNO, NEW.LFTFTNO, NEW.NFTTCTNO, NEW.FFTCONTINS, NEW.FFTCVTYINS, NEW.FFTJSTWDT, NEW.FFTJSTHGT, NEW.FFTJSTSPG, NEW.FFTCINSTHK, NEW.NFTCOVTYPE, NEW.BFTQFVALID, NEW.NFTQFTYPE, NEW.FFTFLRWID, NEW.FFTOUTWID, NEW.FFTBATTHK, NEW.FFTBATRVL, NEW.FFTBLKTHK, NEW.FFTBLKRVL, NEW.NFTCNTINS, NEW.NFTOUTINS, NEW.FFTFF, NEW.BFTDFLTFF, NEW.SFTNOTE, NEW.NFTINSGRDE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_framefloor_copy_trigger` $$
CREATE TRIGGER after_framefloor_copy_trigger
    AFTER INSERT on FrameFlr FOR EACH ROW
    BEGIN

    -- Trigger #: 19 of 75 Source: FrameFlr Target: remrate_data_framefloor --

    DECLARE ftype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lFTFTNo
    SELECT axis.remrate_data_floortype.id INTO ftype_id FROM axis.remrate_data_floortype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_floortype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_floortype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_floortype.lFTFTNo = NEW.LFFFLORTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_framefloor
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szFFName`, `fFFArea`, `nFFLoc`, `fFFUo`, `lFFFlorTNo`, `sFFRateNo`) VALUES
      ( ftype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZFFNAME, NEW.FFFAREA, NEW.NFFLOC, NEW.FFFUO, NEW.LFFFLORTNO, NEW.SFFRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_joist_copy_trigger` $$
CREATE TRIGGER after_joist_copy_trigger
    AFTER INSERT on Joist FOR EACH ROW
    BEGIN

    -- Trigger #: 20 of 75 Source: Joist Target: remrate_data_joist --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_joist
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szRJName`, `fRJArea`, `nRJLoc`, `fRJCoInsul`, `fRJFrInsul`, `fRJSpacing`, `fRJUo`, `fRJInsulTh`, `sRJRateNo`, `nRJInsGrde`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZRJNAME, NEW.FRJAREA, NEW.NRJLOC, NEW.FRJCOINSUL, NEW.FRJFRINSUL, NEW.FRJSPACING, NEW.FRJUO, NEW.FRJINSULTH, NEW.SRJRATENO, NEW.NRJINSGRDE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_doortype_copy_trigger` $$
CREATE TRIGGER after_doortype_copy_trigger
    AFTER INSERT on DoorType FOR EACH ROW
    BEGIN

    -- Trigger #: 21 of 75 Source: DoorType Target: remrate_data_doortype --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_doortype
      (`simulation_id`, `lBldgRunNo`, `lDTDTNo`, `sDTType`, `nDTType`, `fDTRValue`, `sDTNote`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LDTDTNO, NEW.SDTTYPE, NEW.NDTTYPE, NEW.FDTRVALUE, NEW.SDTNOTE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_door_copy_trigger` $$
CREATE TRIGGER after_door_copy_trigger
    AFTER INSERT on Door FOR EACH ROW
    BEGIN

    -- Trigger #: 22 of 75 Source: Door Target: remrate_data_door --

    DECLARE dtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lDTDTNo
    SELECT axis.remrate_data_doortype.id INTO dtype_id FROM axis.remrate_data_doortype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_doortype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_doortype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_doortype.lDTDTNo = NEW.lDODoorTNo AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_door
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szDOName`, `fNOArea`, `nDOWallNum`, `lDODoorTNo`, `fDOUo`, `sDORateNo`) VALUES
      ( dtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZDONAME, NEW.FNOAREA, NEW.NDOWALLNUM, NEW.LDODOORTNO, NEW.FDOUO, NEW.SDORATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_windowtype_copy_trigger` $$
CREATE TRIGGER after_windowtype_copy_trigger
    AFTER INSERT on WndwType FOR EACH ROW
    BEGIN

    -- Trigger #: 23 of 75 Source: WndwType Target: remrate_data_windowtype --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_windowtype
      (`simulation_id`, `lBldgRunNo`, `lWDTWinNo`, `sWDTType`, `fWDTSHGC`, `fWDTUValue`, `sWDTNote`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LWDTWINNO, NEW.SWDTTYPE, NEW.FWDTSHGC, NEW.FWDTUVALUE, NEW.SWDTNOTE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_window_copy_trigger` $$
CREATE TRIGGER after_window_copy_trigger
    AFTER INSERT on Window FOR EACH ROW
    BEGIN

    -- Trigger #: 24 of 75 Source: Window Target: remrate_data_window --

    DECLARE wtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lWDTWinNo
    SELECT axis.remrate_data_windowtype.id INTO wtype_id FROM axis.remrate_data_windowtype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_windowtype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_windowtype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_windowtype.lWDTWinNo = NEW.lWDWinTNo AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_window
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szWDName`, `fWDArea`, `nWDOr`, `fWDSumShad`, `fWDWtrShad`, `nWDSurfNum`, `nWDSurfTyp`, `lWDWinTNo`, `sWDRateNo`, `fWDOHDepth`, `fWDOHToTop`, `fWDOHToBtm`, `fWDAdjSum`, `fWDAdjWtr`, `nWDOperate`) VALUES
      ( wtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZWDNAME, NEW.FWDAREA, NEW.NWDOR, NEW.FWDSUMSHAD, NEW.FWDWTRSHAD, NEW.NWDSURFNUM, NEW.NWDSURFTYP, NEW.LWDWINTNO, NEW.SWDRATENO, NEW.FWDOHDEPTH, NEW.FWDOHTOTOP, NEW.FWDOHTOBTM, NEW.FWDADJSUM, NEW.FWDADJWTR, NEW.nWDOperate );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_skylight_copy_trigger` $$
CREATE TRIGGER after_skylight_copy_trigger
    AFTER INSERT on Skylight FOR EACH ROW
    BEGIN

    -- Trigger #: 25 of 75 Source: Skylight Target: remrate_data_skylight --

    DECLARE wtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lWDTWinNo
    SELECT axis.remrate_data_windowtype.id INTO wtype_id FROM axis.remrate_data_windowtype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_windowtype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_windowtype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_windowtype.lWDTWinNo = NEW.lSKWinTNo AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_skylight
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szSKName`, `fSKGlzArea`, `nSKOr`, `fSKPitch`, `fSKSumShad`, `fSKWtrShad`, `nSKSurfNum`, `lSKWinTNo`, `sSKRateNo`) VALUES
      ( wtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZSKNAME, NEW.FSKGLZAREA, NEW.NSKOR, NEW.FSKPITCH, NEW.FSKSUMSHAD, NEW.FSKWTRSHAD, NEW.NSKSURFNUM, NEW.LSKWINTNO, NEW.SSKRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_generalmechanicalequipment_copy_trigger` $$
CREATE TRIGGER after_generalmechanicalequipment_copy_trigger
    AFTER INSERT on Equip FOR EACH ROW
    BEGIN

    -- Trigger #: 26 of 75 Source: Equip Target: remrate_data_generalmechanicalequipment --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_generalmechanicalequipment
      (`simulation_id`, `lEIEINo`, `lBldgRunNo`, `lBldgNo`, `fEIHSetPnt`, `fEICSetPnt`, `nEISBThrm`, `nEISUThrm`, `nEIVentTyp`, `nEISBSch`, `fEISBTemp`, `nEIDuctLoc`, `nEIDuctLo2`, `nEIDuctLo3`, `fEIDuctIns`, `fEIDuctIn2`, `fEIDuctIn3`, `fEIDuctSup`, `fEIDuctSu2`, `fEIDuctSu3`, `fEIDuctRet`, `fEIDuctRe2`, `fEIDuctRe3`, `nEIDuctLk`, `nEIDTUNITS`, `fEIDTLKAGE`, `nEIDTQUAL`, `sEIRateNo`, `nEIHTGCAPWT`, `nEICLGCAPWT`, `nEIDHWCAPWT`, `nEIDHUCAPWT`, `fEIWHFFlow`, `FEIWHFWatts`) VALUES
      ( sim_id, NEW.LEIEINO, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.FEIHSETPNT, NEW.FEICSETPNT, NEW.NEISBTHRM, NEW.NEISUTHRM, NEW.NEIVENTTYP, NEW.NEISBSCH, NEW.FEISBTEMP, NEW.NEIDUCTLOC, NEW.NEIDUCTLO2, NEW.NEIDUCTLO3, NEW.FEIDUCTINS, NEW.FEIDUCTIN2, NEW.FEIDUCTIN3, NEW.FEIDUCTSUP, NEW.FEIDUCTSU2, NEW.FEIDUCTSU3, NEW.FEIDUCTRET, NEW.FEIDUCTRE2, NEW.FEIDUCTRE3, NEW.NEIDUCTLK, NEW.NEIDTUNITS, NEW.FEIDTLKAGE, NEW.NEIDTQUAL, NEW.SEIRATENO, NEW.nEIHTGCAPWT, NEW.nEICLGCAPWT, NEW.nEIDHWCAPWT, NEW.nEIDHUCAPWT, NEW.fEIWHFFlow, NEW.FEIWHFWatts );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_heater_copy_trigger` $$
CREATE TRIGGER after_heater_copy_trigger
    AFTER INSERT on HtgType FOR EACH ROW
    BEGIN

    -- Trigger #: 27 of 75 Source: HtgType Target: remrate_data_heater --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_heater
      (`simulation_id`, `lBldgRunNo`, `lHETHETNo`, `sHETType`, `nHETSystTp`, `nHETFuelTp`, `fHETRatCap`, `fHETEff`, `nHETEffUTp`, `fHETFanPwr`, `nHETPmpTyp`, `sHETNote`, `nHETDSHtr`, `nHETFnCtrl`, `nHETFnDef`, `fHETFnHSpd`, `fHETFnLSpd`, `fHETAuxElc`, `nHETAuxETp`, `nHETAuxDef`, `fHETPmpEng`, `fHETRCap17`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LHETHETNO, NEW.SHETTYPE, NEW.NHETSYSTTP, NEW.NHETFUELTP, NEW.FHETRATCAP, NEW.FHETEFF, NEW.NHETEFFUTP, NEW.FHETFANPWR, NEW.NHETPMPTYP, NEW.SHETNOTE, NEW.NHETDSHTR, NEW.NHETFNCTRL, NEW.NHETFNDEF, NEW.FHETFNHSPD, NEW.FHETFNLSPD, NEW.FHETAUXELC, NEW.NHETAUXETP, NEW.NHETAUXDEF, NEW.FHETPMPENG, NEW.FHETRCAP17 );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_airconditioner_copy_trigger` $$
CREATE TRIGGER after_airconditioner_copy_trigger
    AFTER INSERT on ClgType FOR EACH ROW
    BEGIN

    -- Trigger #: 28 of 75 Source: ClgType Target: remrate_data_airconditioner --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_airconditioner
      (`simulation_id`, `lBldgRunNo`, `lCETCETNo`, `sCETType`, `nCETSystTp`, `nCETFuelTp`, `fCETRatCap`, `fCETEff`, `fCETSHF`, `nCETEffUTp`, `sCETNote`, `fCETFanPwr`, `nCETPmpTyp`, `nCETDSHtr`, `nCETFnCtrl`, `nCETFnDef`, `fCETFnHSpd`, `fCETFnLSpd`, `fCETPmpEng`, `nCETFanDef`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LCETCETNO, NEW.SCETTYPE, NEW.NCETSYSTTP, NEW.NCETFUELTP, NEW.FCETRATCAP, NEW.FCETEFF, NEW.FCETSHF, NEW.NCETEFFUTP, NEW.SCETNOTE, NEW.FCETFANPWR, NEW.NCETPMPTYP, NEW.NCETDSHTR, NEW.NCETFNCTRL, NEW.NCETFNDEF, NEW.FCETFNHSPD, NEW.FCETFNLSPD, NEW.FCETPMPENG, NEW.NCETFANDEF );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_hotwaterheater_copy_trigger` $$
CREATE TRIGGER after_hotwaterheater_copy_trigger
    AFTER INSERT on DhwType FOR EACH ROW
    BEGIN

    -- Trigger #: 29 of 75 Source: DhwType Target: remrate_data_hotwaterheater --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_hotwaterheater
      (`simulation_id`, `lBldgRunNo`, `lDETDETNo`, `sDETType`, `nDETSystTp`, `nDETFuelTp`, `fDETTnkVol`, `fDETTnkIns`, `fDETEnergy`, `fDETRecEff`, `sDETNote`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LDETDETNO, NEW.SDETTYPE, NEW.NDETSYSTTP, NEW.NDETFUELTP, NEW.FDETTNKVOL, NEW.FDETTNKINS, NEW.FDETENERGY, NEW.FDETRECEFF, NEW.SDETNOTE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_groundsourceheatpump_copy_trigger` $$
CREATE TRIGGER after_groundsourceheatpump_copy_trigger
    AFTER INSERT on GshpType FOR EACH ROW
    BEGIN

    -- Trigger #: 30 of 75 Source: GshpType Target: remrate_data_groundsourceheatpump --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_groundsourceheatpump
      (`simulation_id`, `lBldgRunNo`, `lGSTGSTNo`, `sGSTType`, `nGSTType`, `nGSTFuel`, `fGSTHCap50`, `fGSTCCap50`, `fGSTHCOP70`, `fGSTCEER70`, `fGSTHCap70`, `fGSTCCap70`, `fGSTHCOP50`, `fGSTCEER50`, `fGSTHCOP32`, `fGSTHCap32`, `fGSTCEER77`, `fGSTCCap77`, `fGSTSHF`, `nGSTFanDef`, `nGSTDSHtr`, `sGSTNote`, `fGSTBKUPCP`, `fGSTFanPwr`, `fGSTPmpEng`, `nGSTPmpEnT`, `nGSTDbType`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LGSTGSTNO, NEW.SGSTTYPE, NEW.NGSTTYPE, NEW.NGSTFUEL, NEW.FGSTHCAP50, NEW.FGSTCCAP50, NEW.FGSTHCOP70, NEW.FGSTCEER70, NEW.FGSTHCAP70, NEW.FGSTCCAP70, NEW.FGSTHCOP50, NEW.FGSTCEER50, NEW.FGSTHCOP32, NEW.FGSTHCAP32, NEW.FGSTCEER77, NEW.FGSTCCAP77, NEW.FGSTSHF, NEW.NGSTFANDEF, NEW.NGSTDSHTR, NEW.SGSTNOTE, NEW.FGSTBKUPCP, NEW.fGSTFANPWR, NEW.fGSTPmpEng, NEW.nGSTPmpEnT, NEW.nGSTDbType );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_airsourceheatpump_copy_trigger` $$
CREATE TRIGGER after_airsourceheatpump_copy_trigger
    AFTER INSERT on AshpType FOR EACH ROW
    BEGIN

    -- Trigger #: 31 of 75 Source: AshpType Target: remrate_data_airsourceheatpump --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_airsourceheatpump
      (`simulation_id`, `lBldgRunNo`, `lASTASTNo`, `sASTType`, `nASTFuel`, `fASTHCap47`, `FASTHEFF`, `NASTHEFFU`, `fASTCCAP`, `FASTCEFF`, `NASTCEFFU`, `fASTSHF`, `nASTDSHtr`, `sASTNote`, `fASTBKUPCP`, `nASTFnCtrl`, `nASTFnDef`, `fASTFnHSpd`, `fASTFnLSpd`, `fASTHCap17`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LASTASTNO, NEW.SASTTYPE, NEW.NASTFUEL, NEW.FASTHCAP47, NEW.FASTHEFF, NEW.NASTHEFFU, NEW.FASTCCAP, NEW.FASTCEFF, NEW.NASTCEFFU, NEW.FASTSHF, NEW.NASTDSHTR, NEW.SASTNOTE, NEW.FASTBKUPCP, NEW.NASTFNCTRL, NEW.NASTFNDEF, NEW.FASTFNHSPD, NEW.FASTFNLSPD, NEW.FASTHCAP17 );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_dualfuelheatpump_copy_trigger` $$
CREATE TRIGGER after_dualfuelheatpump_copy_trigger
    AFTER INSERT on DfhpType FOR EACH ROW
    BEGIN

    -- Trigger #: 32 of 75 Source: DfhpType Target: remrate_data_dualfuelheatpump --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_dualfuelheatpump
      (`simulation_id`, `lBldgRunNo`, `lDFTDFTNo`, `sDFTType`, `nDFTFuel`, `nDFTBFuel`, `fDFTHCap47`, `fDFTCCap`, `fDFTHHSPF`, `nDFTBEffU`, `fDFTBSEff`, `fDFTBCap`, `fDFTCSEER`, `fDFTCSHF`, `nDFTDSHtr`, `fDFTSwitch`, `nDFTFnCtrl`, `nDFTFnDef`, `fDFTFnHSpd`, `fDFTFnLSpd`, `sDFTNote`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LDFTDFTNO, NEW.SDFTTYPE, NEW.NDFTFUEL, NEW.NDFTBFUEL, NEW.FDFTHCAP47, NEW.FDFTCCAP, NEW.FDFTHHSPF, NEW.NDFTBEFFU, NEW.FDFTBSEFF, NEW.FDFTBCAP, NEW.FDFTCSEER, NEW.FDFTCSHF, NEW.NDFTDSHTR, NEW.FDFTSWITCH, NEW.NDFTFNCTRL, NEW.NDFTFNDEF, NEW.FDFTFNHSPD, NEW.FDFTFNLSPD, NEW.SDFTNOTE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_integratedspacewaterheater_copy_trigger` $$
CREATE TRIGGER after_integratedspacewaterheater_copy_trigger
    AFTER INSERT on HtDhType FOR EACH ROW
    BEGIN

    -- Trigger #: 33 of 75 Source: HtDhType Target: remrate_data_integratedspacewaterheater --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_integratedspacewaterheater
      (`simulation_id`, `lBldgRunNo`, `lHTDHTDNo`, `sHTDType`, `NHTDSYSTTP`, `nHTDFuel`, `FHTDRATCAP`, `NHTDDISTTP`, `FHTDSPHTE`, `FHTDWHEF`, `FHTDWHRE`, `FHTDTNKSZ`, `FHTDTNKIN`, `nHTDFnCtrl`, `nHTDFnDef`, `fHTDFnHSpd`, `fHTDFnLSpd`, `sHTDNote`, `fHTDAuxElc`, `nHTDAuxETp`, `nHTDAuxDef`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LHTDHTDNO, NEW.SHTDTYPE, NEW.NHTDSYSTTP, NEW.NHTDFUEL, NEW.FHTDRATCAP, NEW.NHTDDISTTP, NEW.FHTDSPHTE, NEW.FHTDWHEF, NEW.FHTDWHRE, NEW.FHTDTNKSZ, NEW.FHTDTNKIN, NEW.NHTDFNCTRL, NEW.NHTDFNDEF, NEW.FHTDFNHSPD, NEW.FHTDFNLSPD, NEW.SHTDNOTE, NEW.FHTDAUXELC, NEW.NHTDAUXETP, NEW.NHTDAUXDEF );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_dehumidifier_copy_trigger` $$
CREATE TRIGGER after_dehumidifier_copy_trigger
    AFTER INSERT on DehumidType FOR EACH ROW
    BEGIN

    -- Trigger #: 34 of 75 Source: DehumidType Target: remrate_data_dehumidifier --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_dehumidifier
      (`simulation_id`, `lBldgRunNo`, `lDhuEqKey`, `sName`, `nSystem`, `nFuel`, `fCapacity`, `fEfficiency`, `sNote`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.lDhuEqKey, NEW.sName, NEW.nSystem, NEW.nFuel, NEW.fCapacity, NEW.fEfficiency, NEW.sNote );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_sharedequipment_copy_trigger` $$
CREATE TRIGGER after_sharedequipment_copy_trigger
    AFTER INSERT on SharedType FOR EACH ROW
    BEGIN

    -- Trigger #: 35 of 75 Source: SharedType Target: remrate_data_sharedequipment --

    DECLARE gshp_id INT;
    DECLARE wlhp_id INT;
    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Figure out the lGSTGSTNo
    SELECT axis.remrate_data_groundsourceheatpump.id INTO gshp_id FROM axis.remrate_data_groundsourceheatpump
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_groundsourceheatpump.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_groundsourceheatpump.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_groundsourceheatpump.lGSTGSTNo = NEW.lGshpEqKey AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lWlhpEqKey
    SELECT axis.remrate_data_waterloopheatpump.id INTO wlhp_id FROM axis.remrate_data_waterloopheatpump
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_waterloopheatpump.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_waterloopheatpump.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_waterloopheatpump.lWlhpEqKey = NEW.lWlhpEqKey AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_sharedequipment
      (`ground_source_heat_pump_id`, `water_loop_heat_pump_id`, `simulation_id`, `lBldgRunNo`, `lSharedEqKey`, `sName`, `nSystem`, `nFuel`, `fRatedEff`, `nRatedEffUnit`, `fBoilerCap`, `fChillerCap`, `fGndLoopCap`, `fGndLoopPump`, `nBlgLoopUnits`, `fBlgLoopPumpPwr`, `nTerminalType`, `fFanCoil`, `sNote`, `lHtgEqKey`, `lClgEqKey`, `lGshpEqKey`, `lWlhpEqKey`) VALUES
      ( gshp_id, wlhp_id, sim_id, NEW.lBldgRunNo, NEW.lSharedEqKey, NEW.sName, NEW.nSystem, NEW.nFuel, NEW.fRatedEff, NEW.nRatedEffUnit, NEW.fBoilerCap, NEW.fChillerCap, NEW.fGndLoopCap, NEW.fGndLoopPump, NEW.nBlgLoopUnits, NEW.fBlgLoopPumpPwr, NEW.nTerminalType, NEW.fFanCoil, NEW.sNote, NEW.lHtgEqKey, NEW.lClgEqKey, NEW.lGshpEqKey, NEW.lWlhpEqKey );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_waterloopheatpump_copy_trigger` $$
CREATE TRIGGER after_waterloopheatpump_copy_trigger
    AFTER INSERT on WlhpType FOR EACH ROW
    BEGIN

    -- Trigger #: 36 of 75 Source: WlhpType Target: remrate_data_waterloopheatpump --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_waterloopheatpump
      (`simulation_id`, `lBldgRunNo`, `lWlhpEqKey`, `sName`, `fHtgEff`, `fHtgCap`, `fClgEff`, `fClgCap`, `fClgSHF`, `sNote`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.lWlhpEqKey, NEW.sName, NEW.fHtgEff, NEW.fHtgCap, NEW.fClgEff, NEW.fClgCap, NEW.fClgSHF, NEW.sNote );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_installedequipment_copy_trigger` $$
CREATE TRIGGER after_installedequipment_copy_trigger
    AFTER INSERT on EqInst FOR EACH ROW
    BEGIN

    -- Trigger #: 37 of 75 Source: EqInst Target: remrate_data_installedequipment --

    DECLARE htg_id INT;
    DECLARE gshp_id INT;
    DECLARE dfhp_id INT;
    DECLARE clg_id INT;
    DECLARE dhw_id INT;
    DECLARE ashp_id INT;
    DECLARE iswh_id INT;
    DECLARE dehumid_id INT;
    DECLARE shared_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lHETHETNo
    SELECT axis.remrate_data_heater.id INTO htg_id FROM axis.remrate_data_heater
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_heater.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_heater.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_heater.lHETHETNo = NEW.LEIHETNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lGSTGSTNo
    SELECT axis.remrate_data_groundsourceheatpump.id INTO gshp_id FROM axis.remrate_data_groundsourceheatpump
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_groundsourceheatpump.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_groundsourceheatpump.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_groundsourceheatpump.lGSTGSTNo = NEW.LEIGSTNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lDFTDFTNo
    SELECT axis.remrate_data_dualfuelheatpump.id INTO dfhp_id FROM axis.remrate_data_dualfuelheatpump
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_dualfuelheatpump.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_dualfuelheatpump.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_dualfuelheatpump.lDFTDFTNo = NEW.LEIDFTNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lCETCETNo
    SELECT axis.remrate_data_airconditioner.id INTO clg_id FROM axis.remrate_data_airconditioner
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_airconditioner.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_airconditioner.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_airconditioner.lCETCETNo = NEW.LEICLTNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lDETDETNo
    SELECT axis.remrate_data_hotwaterheater.id INTO dhw_id FROM axis.remrate_data_hotwaterheater
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_hotwaterheater.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_hotwaterheater.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_hotwaterheater.lDETDETNo = NEW.LEIDHTNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lASTASTNo
    SELECT axis.remrate_data_airsourceheatpump.id INTO ashp_id FROM axis.remrate_data_airsourceheatpump
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_airsourceheatpump.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_airsourceheatpump.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_airsourceheatpump.lASTASTNo = NEW.LEIASTNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lHTDHTDNo
    SELECT axis.remrate_data_integratedspacewaterheater.id INTO iswh_id FROM axis.remrate_data_integratedspacewaterheater
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_integratedspacewaterheater.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_integratedspacewaterheater.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_integratedspacewaterheater.lHTDHTDNo = NEW.LEIHDTNO AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lDhuEqKey
    SELECT axis.remrate_data_dehumidifier.id INTO dehumid_id FROM axis.remrate_data_dehumidifier
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_dehumidifier.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_dehumidifier.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_dehumidifier.lDhuEqKey = NEW.lDhuEqKey AND axis.remrate_data_datatracker.status = 0);

    -- Figure out the lSharedEqKey
    SELECT axis.remrate_data_sharedequipment.id INTO shared_id FROM axis.remrate_data_sharedequipment
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_sharedequipment.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_sharedequipment.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_sharedequipment.lSharedEqKey = NEW.lSharedEqKey AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_installedequipment
      (`heater_id`, `ground_source_heat_pump_id`, `dual_fuel_heat_pump_id`, `air_conditioner_id`, `hot_water_heater_id`, `air_source_heat_pump_id`, `integrated_space_water_heater_id`, `dehumidifier_id`, `shared_equipment_id`, `simulation_id`, `building_id`, `lEIEINo`, `lBldgRunNo`, `lBldgNo`, `lEIHETNo`, `lEIGSTNo`, `lEIDFTNo`, `lEICLTNo`, `lEIDHTNo`, `lEIASTNO`, `lEIHDTNO`, `lDhuEqKey`, `lSharedEqKey`, `nEISysType`, `fEIPerAdj`, `nEILoc`, `fEIHLdSrv`, `fEICLdSrv`, `fEIDLdSrv`, `nEINoUnits`, `fEIDSE`, `fCWLoadSrvd`, `fDWLoadSrvd`, `fDhuLoadSrvd`, `fMVHtgLoadSrvd`, `fMVClgLoadSrvd`, `nDwellUnitsDhw`, `nPrecondSharedMV`) VALUES
      ( htg_id, gshp_id, dfhp_id, clg_id, dhw_id, ashp_id, iswh_id, dehumid_id, shared_id, sim_id, bldg_id, NEW.LEIEINO, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.LEIHETNO, NEW.LEIGSTNO, NEW.LEIDFTNO, NEW.LEICLTNO, NEW.LEIDHTNO, NEW.LEIASTNO, NEW.LEIHDTNO, NEW.lDhuEqKey, NEW.lSharedEqKey, NEW.NEISYSTYPE, NEW.FEIPERADJ, NEW.NEILOC, NEW.FEIHLDSRV, NEW.FEICLDSRV, NEW.FEIDLDSRV, NEW.NEINOUNITS, NEW.fEIDSE, NEW.fCWLoadSrvd, NEW.fDWLoadSrvd, NEW.fDhuLoadSrvd, NEW.fMVHtgLoadSrvd, NEW.fMVClgLoadSrvd, NEW.nDwellUnitsDhw, NEW.nPrecondSharedMV );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_gshpwell_copy_trigger` $$
CREATE TRIGGER after_gshpwell_copy_trigger
    AFTER INSERT on GshpWell FOR EACH ROW
    BEGIN

    -- Trigger #: 38 of 75 Source: GshpWell Target: remrate_data_groundsourceheatpumpwell --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_groundsourceheatpumpwell
      (`simulation_id`, `lBldgRunNo`, `lGWellNo`, `nGWType`, `fGWNoWells`, `fGWDepth`, `fGWLpFlow`, `sRateNo`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.lGWellNo, NEW.nGWType, NEW.fGWNoWells, NEW.fGWDepth, NEW.fGWLpFlow, NEW.sRateNo );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_hotwaterdistribution_copy_trigger` $$
CREATE TRIGGER after_hotwaterdistribution_copy_trigger
    AFTER INSERT on DhwDistrib FOR EACH ROW
    BEGIN

    -- Trigger #: 39 of 75 Source: DhwDistrib Target: remrate_data_hotwaterdistribution --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_hotwaterdistribution
      (`simulation_id`, `lBldgRunNo`, `lDhwDistNo`, `sRateNo`, `bFixLowFlow`, `bDhwPipeIns`, `nRecircType`, `fMaxFixDist`, `fSupRetDist`, `fPipeLenDhw`, `fPipeLenRec`, `fRecPumpPwr`, `bHasDwhr`, `fDwhrEff`, `bDwhrPrehtC`, `bDwhrPrehtH`, `nShwrheads`, `nShwrToDwhr`, `fHwCtrlEff`, `nHomesServed`, `fCompactFactor`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.lDhwDistNo, NEW.sRateNo, NEW.bFixLowFlow, NEW.bDhwPipeIns, NEW.nRecircType, NEW.fMaxFixDist, NEW.fSupRetDist, NEW.fPipeLenDhw, NEW.fPipeLenRec, NEW.fRecPumpPwr, NEW.bHasDwhr, NEW.fDwhrEff, NEW.bDwhrPrehtC, NEW.bDwhrPrehtH, NEW.nShwrheads, NEW.nShwrToDwhr, NEW.fHwCtrlEff, NEW.nHomesServed, NEW.fCompactFactor );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_hvaccommissioning_copy_trigger` $$
CREATE TRIGGER after_hvaccommissioning_copy_trigger
    AFTER INSERT on HvacCx FOR EACH ROW
    BEGIN

    -- Trigger #: 40 of 75 Source: HvacCx Target: remrate_data_hvaccommissioning --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_hvaccommissioning
      (`simulation_id`, `lBldgRunNo`, `sRateNo`, `lHvacCxNo`, `nDuctSysNo`, `nHtgEquipNo`, `nClgEquipNo`, `nTotDuctLeakGrade`, `bTotDuctLeakExcep`, `bTotDuctLeakGrdIMet`, `fTotDuctLeakage`, `nBFAirflowGrade`, `bBFAirflowException`, `nBFAirflowDesignSpec`, `nBFAirflowOpCond`, `nBFWattDrawGrade`, `nBFWattDraw`, `fBFEffic`, `bRCSinglePkgSystem`, `bRCOnboardDiagnostic`, `nRCTestMethod`, `nRCGrade`, `fDiffDTD`, `fDiffCTOA`, `fDeviation`, `fRptdRefrigWeight`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.sRateNo, NEW.lHvacCxNo, NEW.nDuctSysNo, NEW.nHtgEquipNo, NEW.nClgEquipNo, NEW.nTotDuctLeakGrade, NEW.bTotDuctLeakExcep, NEW.bTotDuctLeakGrdIMet, NEW.fTotDuctLeakage, NEW.nBFAirflowGrade, NEW.bBFAirflowException, NEW.nBFAirflowDesignSpec, NEW.nBFAirflowOpCond, NEW.nBFWattDrawGrade, NEW.nBFWattDraw, NEW.fBFEffic, NEW.bRCSinglePkgSystem, NEW.bRCOnboardDiagnostic, NEW.nRCTestMethod, NEW.nRCGrade, NEW.fDiffDTD, NEW.fDiffCTOA, NEW.fDeviation, NEW.fRptdRefrigWeight );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_ductsystem_copy_trigger` $$
CREATE TRIGGER after_ductsystem_copy_trigger
    AFTER INSERT on DuctSystem FOR EACH ROW
    BEGIN

    -- Trigger #: 41 of 75 Source: DuctSystem Target: remrate_data_ductsystem --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_ductsystem
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `lDSDSNo`, `szDSName`, `nDSDLeakTy`, `nDSDLeakUn`, `fDSDLeakTo`, `fDSDLeakSu`, `fDSDLeakRe`, `lDSHtgNo`, `lDSClgNo`, `fDSSupArea`, `fDSRetArea`, `lDSRegis`, `lDSDLeakET`, `sDSRateNo`, `nDSDLeakTT`, `fDSCFArea`, `fDSDLeakRTo`, `nDSDLeakRUN`, `nDSDLeakTEx`, `nDSInpType`, `nDSLtOType`, `nDSIECCEx`, `nDSRESNETEx`, `nDSESTAREx`, `fDSTestLtO`, `fDSTestDL`, `nDSIsDucted`, `nDSTestType`, `fDSDSE`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.LDSDSNO, NEW.SZDSNAME, NEW.NDSDLEAKTY, NEW.NDSDLEAKUN, NEW.FDSDLEAKTO, NEW.FDSDLEAKSU, NEW.FDSDLEAKRE, NEW.LDSHTGNO, NEW.LDSCLGNO, NEW.FDSSUPAREA, NEW.FDSRETAREA, NEW.LDSREGIS, NEW.LDSDLEAKET, NEW.SDSRATENO, NEW.NDSDLEAKTT, NEW.FDSCFAREA, NEW.fDSDLEAKRTO, NEW.nDSDLeakRUN, NEW.NDSDLEAKTEX, NEW.nDSInpType, NEW.nDSLtOType, NEW.nDSIECCEx, NEW.nDSRESNETEx, NEW.nDSESTAREx, NEW.fDSTestLtO, NEW.fDSTestDL, NEW.nDSIsDucted, NEW.nDSTestType, NEW.fDSDSE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_duct_copy_trigger` $$
CREATE TRIGGER after_duct_copy_trigger
    AFTER INSERT on Duct FOR EACH ROW
    BEGIN

    -- Trigger #: 42 of 75 Source: Duct Target: remrate_data_duct --

    DECLARE dtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lDSDSNo
    SELECT axis.remrate_data_ductsystem.id INTO dtype_id FROM axis.remrate_data_ductsystem
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_ductsystem.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_ductsystem.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_ductsystem.lDSDSNo = NEW.LDUDSNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_duct
      (`duct_system_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `lDUDSNo`, `fDUArea`, `nDULoc`, `fDUIns`, `nDUDctType`, `sDURateNo`) VALUES
      ( dtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.LDUDSNO, NEW.FDUAREA, NEW.NDULOC, NEW.FDUINS, NEW.NDUDCTTYPE, NEW.SDURATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_infiltration_copy_trigger` $$
CREATE TRIGGER after_infiltration_copy_trigger
    AFTER INSERT on Infilt FOR EACH ROW
    BEGIN

    -- Trigger #: 43 of 75 Source: Infilt Target: remrate_data_infiltration --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_infiltration
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `lINInfilNo`, `fINHeatVal`, `fINCoolVal`, `nINWHInfUn`, `lINMVType`, `fINMVRate`, `fINMVFan`, `nINHrsDay`, `nINType`, `fINSREff`, `sINRateNo`, `fINTREff`, `nINVerify`, `nINShltrCl`, `nINClgVent`, `nINFanMotor`, `FINANNUAL`, `FINTESTED`, `NINGDAIRXMF`, `NINNOMVMSRD`, `NINWATTDFLT`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.LININFILNO, NEW.FINHEATVAL, NEW.FINCOOLVAL, NEW.NINWHINFUN, NEW.LINMVTYPE, NEW.FINMVRATE, NEW.FINMVFAN, NEW.NINHRSDAY, NEW.NINTYPE, NEW.FINSREFF, NEW.SINRATENO, NEW.FINTREFF, NEW.NINVERIFY, NEW.NINSHLTRCL, NEW.NINCLGVENT, NEW.NINFANMOTOR, NEW.FINANNUAL, NEW.FINTESTED, NEW.NINGDAIRXMF, NEW.NINNOMVMSRD, NEW.NINWATTDFLT );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_ventilation_copy_trigger` $$
CREATE TRIGGER after_ventilation_copy_trigger
    AFTER INSERT on MechVent FOR EACH ROW
    BEGIN

    -- Trigger #: 44 of 75 Source: MechVent Target: remrate_data_ventilation --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_ventilation
      (`simulation_id`, `lBldgRunNo`, `lBldgNo`, `sMVRateNo`, `sMVName`, `nMVType`, `fMVRate`, `nMVHrsDay`, `fMVFanPwr`, `fMVASRE`, `fMVATRE`, `nMVNotMsrd`, `nMVWattDflt`, `nMVFanMotor`, `nMVDuctNo`, `nMVShrdMF`, `nMVHtgNo`, `nMVClgNo`, `fMVShrdCFM`, `fMVOAPct`, `fMVReCirc`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.lBldgNo, NEW.sMVRateNo, NEW.sMVName, NEW.nMVType, NEW.fMVRate, NEW.nMVHrsDay, NEW.fMVFanPwr, NEW.fMVASRE, NEW.fMVATRE, NEW.nMVNotMsrd, NEW.nMVWattDflt, NEW.nMVFanMotor, NEW.nMVDuctNo, NEW.nMVShrdMF, NEW.nMVHtgNo, NEW.nMVClgNo, NEW.fMVShrdCFM, NEW.fMVOAPct, NEW.fMVRecirc );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_lightsandappliance_copy_trigger` $$
CREATE TRIGGER after_lightsandappliance_copy_trigger
    AFTER INSERT on LightApp FOR EACH ROW
    BEGIN

    -- Trigger #: 45 of 75 Source: LightApp Target: remrate_data_lightsandappliance --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_lightsandappliance
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `FLAOVNFUEL`, `FLADRYFUEL`, `FLAREFKWH`, `FLADISHWEF`, `FLAFANCFM`, `FLAFLRCENT`, `FLACFLCENT`, `FLACFLEXT`, `FLACFLGAR`, `FLADRYEF`, `FLAWASHLER`, `FLAWASHCAP`, `FLAWASHEFF`, `FLALEDINT`, `FLALEDEXT`, `FLALEDGAR`, `SLARATENO`, `NLAUSEDEF`, `NLAREFLOC`, `FLADISHWCAP`, `FLADISHWYR`, `NLAOVNIND`, `NLAOVNCON`, `NLADRYLOC`, `NLADRYMOIST`, `FLADRYMEF`, `FLADRYGASEF`, `NLAWASHLOC`, `FLAWASHELEC`, `FLAWASHGAS`, `FLAWASHGCST`, `nLAFanCnt`, `nLAOvnLoc`, `nLAWashPre`, `nLAWashUnit`, `nLAWashDhw`, `fLAWashIWF`, `nLAWashLoad`, `nLADishLoc`, `nLADishPre`, `nLADishDhw`, `fLADishElec`, `fLADishGas`, `fLADishGCst`, `nLADishLoad`, `nLADryUnit`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.FLAOVNFUEL, NEW.FLADRYFUEL, NEW.FLAREFKWH, NEW.FLADISHWEF, NEW.FLAFANCFM, NEW.FLAFLRCENT, NEW.FLACFLCENT, NEW.FLACFLEXT, NEW.FLACFLGAR, NEW.FLADRYEF, NEW.FLAWASHLER, NEW.FLAWASHCAP, NEW.FLAWASHEFF, NEW.FLALEDINT, NEW.FLALEDEXT, NEW.FLALEDGAR, NEW.SLARATENO, NEW.NLAUSEDEF, NEW.NLAREFLOC, NEW.FLADISHWCAP, NEW.FLADISHWYR, NEW.NLAOVNIND, NEW.NLAOVNCON, NEW.NLADRYLOC, NEW.NLADRYMOIST, NEW.FLADRYMEF, NEW.FLADRYGASEF, NEW.NLAWASHLOC, NEW.FLAWASHELEC, NEW.FLAWASHGAS, NEW.FLAWASHGCST, NEW.nLAFanCnt, NEW.nLAOvnLoc, NEW.nLAWashPre, NEW.nLAWashUnit, NEW.nLAWashDhw, NEW.fLAWashIWF, NEW.nLAWashLoad, NEW.nLADishLoc, NEW.nLADishPre, NEW.nLADishDhw, NEW.fLADishElec, NEW.fLADishGas, NEW.fLADishGCst, NEW.nLADishLoad, NEW.nLADryUnit );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_lainst_copy_trigger` $$
CREATE TRIGGER after_lainst_copy_trigger
    AFTER INSERT on LAInst FOR EACH ROW
    BEGIN

    -- Trigger #: 46 of 75 Source: LAInst Target: remrate_data_installedlightsandappliances --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_installedlightsandappliances
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `SLAINAME`, `NLAITYPE`, `NLAILOC`, `NLAIFUEL`, `FLAIRATE`, `NLAIRATEU`, `FLAIUSE`, `NLAIUSEU`, `NLAIQTY`, `NLAIEFF`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SLAINAME, NEW.NLAITYPE, NEW.NLAILOC, NEW.NLAIFUEL, NEW.FLAIRATE, NEW.NLAIRATEU, NEW.FLAIUSE, NEW.NLAIUSEU, NEW.NLAIQTY, NEW.NLAIEFF );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_mandreq_copy_trigger` $$
CREATE TRIGGER after_mandreq_copy_trigger
    AFTER INSERT on MandReq FOR EACH ROW
    BEGIN

    -- Trigger #: 47 of 75 Source: MandReq Target: remrate_data_mandatoryrequirements --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Do not push the Slab and Florida < 14.4
    IF version_id IN ('12.5', '12.99A', '13.0', '14.0', '14.1', '14.2', '14.3') THEN
       INSERT INTO axis.remrate_data_mandatoryrequirements
         (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nMRIECC04`, `nMRIECC06`, `nMRIECC09`, `nMRESV2TBC`, `nMRESV2PRD`, `nMRESV3TEC`, `nMRESV3HC`, `nMRESV3HR`, `nMRESV3WM`, `nMRESV3AP`, `nMRESV3RF`, `nMRESV3CF`, `nMRESV3EF`, `nMRESV3DW`, `nMRESV3NRF`, `nMRESV3NCF`, `nMRESV3NEF`, `nMRESV3NDW`, `sMRRateNo`, `nMRIECCNY`, `nMRESV3SAF`, `fMRESV3BFA`, `nMRESV3NBB`, `nMRIECC12`, `NMRFLORIDA`, `NMRESV3SLAB`) VALUES
         ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NMRIECC04, NEW.NMRIECC06, NEW.NMRIECC09, NEW.NMRESV2TBC, NEW.NMRESV2PRD, NEW.NMRESV3TEC, NEW.NMRESV3HC, NEW.NMRESV3HR, NEW.NMRESV3WM, NEW.NMRESV3AP, NEW.NMRESV3RF, NEW.NMRESV3CF, NEW.NMRESV3EF, NEW.NMRESV3DW, NEW.NMRESV3NRF, NEW.NMRESV3NCF, NEW.NMRESV3NEF, NEW.NMRESV3NDW, NEW.SMRRATENO, NEW.NMRIECCNY, NEW.nMRESV3SAF, NEW.fMRESV3BFA, NEW.nMRESV3NBB, NEW.NMRIECC12, 0, 0 );
    ELSE
       INSERT INTO axis.remrate_data_mandatoryrequirements
         (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nMRIECC04`, `nMRIECC06`, `nMRIECC09`, `nMRESV2TBC`, `nMRESV2PRD`, `nMRESV3TEC`, `nMRESV3HC`, `nMRESV3HR`, `nMRESV3WM`, `nMRESV3AP`, `nMRESV3RF`, `nMRESV3CF`, `nMRESV3EF`, `nMRESV3DW`, `nMRESV3NRF`, `nMRESV3NCF`, `nMRESV3NEF`, `nMRESV3NDW`, `sMRRateNo`, `nMRIECCNY`, `nMRESV3SAF`, `fMRESV3BFA`, `nMRESV3NBB`, `nMRIECC12`, `NMRFLORIDA`, `NMRESV3SLAB`, `NMRIECC15`, `sMResQual4`, `NMRIECC18`, `NMRIECCMI`, `NMRESMFWSHR`, `NMRESMFDRYR`, `NMRESMFWIN`, `NMRIECCNC`, `nMRNGBS15`, `NMRIECC21`) VALUES
         ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NMRIECC04, NEW.NMRIECC06, NEW.NMRIECC09, NEW.NMRESV2TBC, NEW.NMRESV2PRD, NEW.NMRESV3TEC, NEW.NMRESV3HC, NEW.NMRESV3HR, NEW.NMRESV3WM, NEW.NMRESV3AP, NEW.NMRESV3RF, NEW.NMRESV3CF, NEW.NMRESV3EF, NEW.NMRESV3DW, NEW.NMRESV3NRF, NEW.NMRESV3NCF, NEW.NMRESV3NEF, NEW.NMRESV3NDW, NEW.SMRRATENO, NEW.NMRIECCNY, NEW.nMRESV3SAF, NEW.fMRESV3BFA, NEW.nMRESV3NBB, NEW.NMRIECC12, NEW.NMRFLORIDA, NEW.NMRESV3SLAB, NEW.NMRIECC15, NEW.SMRESQUAL4, NEW.NMRIECC18, NEW.NMRIECCMI, NEW.NMRESMFWSHR, NEW.NMRESMFDRYR, NEW.NMRESMFWIN, NEW.NMRIECCNC, NEW.nMRNGBS15, NEW.NMRIECC21 );
    END IF;

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_doechallenge_copy_trigger` $$
CREATE TRIGGER after_doechallenge_copy_trigger
    AFTER INSERT on DOEChallenge FOR EACH ROW
    BEGIN

    -- Trigger #: 48 of 75 Source: DOEChallenge Target: remrate_data_doechallenge --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_doechallenge
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `sDCBldrID`, `nDCFenstrtn`, `nDCInsul`, `nDCDuctLoc`, `nDCAppl`, `nDCLighting`, `nDCFanEff`, `nDCAirQual`, `nDCSolarE`, `nDCSolarHW`, `nDCAirPlus`, `nDCWtrSense`, `nDCIBHS`, `nDCMGMT`, `nDCWaiver`, `sDCRateNo`, `nDCWaterEff`, `nDCPassiveHome`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SDCBLDRID, NEW.NDCFENSTRTN, NEW.NDCINSUL, NEW.NDCDUCTLOC, NEW.NDCAPPL, NEW.NDCLIGHTING, NEW.NDCFANEFF, NEW.NDCAIRQUAL, NEW.NDCSOLARE, NEW.NDCSOLARHW, NEW.NDCAIRPLUS, NEW.NDCWTRSENSE, NEW.NDCIBHS, NEW.NDCMGMT, NEW.NDCWAIVER, NEW.SDCRATENO, NEW.NDCWATEREFF, NEW.nDCPassiveHome );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_addmass_copy_trigger` $$
CREATE TRIGGER after_addmass_copy_trigger
    AFTER INSERT on AddMass FOR EACH ROW
    BEGIN

    -- Trigger #: 49 of 75 Source: AddMass Target: remrate_data_additionalmass --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_additionalmass
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szAMName`, `fAMArea`, `nAMLoc`, `nAMType`, `fAMThk`, `sAMRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZAMNAME, NEW.FAMAREA, NEW.NAMLOC, NEW.NAMTYPE, NEW.FAMTHK, NEW.SAMRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_solarsystem_copy_trigger` $$
CREATE TRIGGER after_solarsystem_copy_trigger
    AFTER INSERT on ActSolar FOR EACH ROW
    BEGIN

    -- Trigger #: 50 of 75 Source: ActSolar Target: remrate_data_solarsystem --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_solarsystem
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nASSystem`, `nASLoop`, `fASColArea`, `nASOr`, `nASTilt`, `nASSpecs`, `fASStgVol`, `sASRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NASSYSTEM, NEW.NASLOOP, NEW.FASCOLAREA, NEW.NASOR, NEW.NASTILT, NEW.NASSPECS, NEW.FASSTGVOL, NEW.SASRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_photovoltaic_copy_trigger` $$
CREATE TRIGGER after_photovoltaic_copy_trigger
    AFTER INSERT on PhotoVol FOR EACH ROW
    BEGIN

    -- Trigger #: 51 of 75 Source: PhotoVol Target: remrate_data_photovoltaic --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_photovoltaic
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nPVColType`, `fPVArea`, `fPVPower`, `fPVTilt`, `nPVOr`, `fPVInvEff`, `sPVRateNo`, `sPVName`, `nPVNumBeds`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NPVCOLTYPE, NEW.FPVAREA, NEW.FPVPOWER, NEW.FPVTILT, NEW.NPVOR, NEW.FPVINVEFF, NEW.sPVRateNo, NEW.SPVNAME, NEW.nPVNumBeds );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_sunspace_copy_trigger` $$
CREATE TRIGGER after_sunspace_copy_trigger
    AFTER INSERT on SunSpace FOR EACH ROW
    BEGIN

    -- Trigger #: 52 of 75 Source: SunSpace Target: remrate_data_sunspace --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_sunspace
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `fSSRfArea`, `fSSRFIns`, `fSSAGWArea`, `fSSAGWIns`, `fSSBGWArea`, `fSSBGWIns`, `fSSArea`, `fSSFrmIns`, `fSSSlbPer`, `fSSSlbDep`, `fSSSlbThk`, `fSSSlbPIns`, `fSSSlbUIns`, `sSSRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.FSSRFAREA, NEW.FSSRFINS, NEW.FSSAGWAREA, NEW.FSSAGWINS, NEW.FSSBGWAREA, NEW.FSSBGWINS, NEW.FSSAREA, NEW.FSSFRMINS, NEW.FSSSLBPER, NEW.FSSSLBDEP, NEW.FSSSLBTHK, NEW.FSSSLBPINS, NEW.FSSSLBUINS, NEW.SSSRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_ssmass_copy_trigger` $$
CREATE TRIGGER after_ssmass_copy_trigger
    AFTER INSERT on SSMass FOR EACH ROW
    BEGIN

    -- Trigger #: 53 of 75 Source: SSMass Target: remrate_data_sunspacemass --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_sunspacemass
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szSSMName`, `fSSMArea`, `nSSMType`, `fSSMThk`, `fSSMWVol`, `sSSMRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZSSMNAME, NEW.FSSMAREA, NEW.NSSMTYPE, NEW.FSSMTHK, NEW.FSSMWVOL, NEW.SSSMRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_sscmnwal_copy_trigger` $$
CREATE TRIGGER after_sscmnwal_copy_trigger
    AFTER INSERT on SSCmnWal FOR EACH ROW
    BEGIN

    -- Trigger #: 54 of 75 Source: SSCmnWal Target: remrate_data_sunspacecommonwall --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_sunspacecommonwall
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szSSCName`, `fSSCArea`, `nSSCMTyp`, `fSSCMThk`, `fSSCIns`, `nSSCFan`, `fSSCFlRate`, `sSSCRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZSSCNAME, NEW.FSSCAREA, NEW.NSSCMTYP, NEW.FSSCMTHK, NEW.FSSCINS, NEW.NSSCFAN, NEW.FSSCFLRATE, NEW.SSSCRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_sswindow_copy_trigger` $$
CREATE TRIGGER after_sswindow_copy_trigger
    AFTER INSERT on SSWindow FOR EACH ROW
    BEGIN

    -- Trigger #: 55 of 75 Source: SSWindow Target: remrate_data_sunspacewindow --

    DECLARE wtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lWDTWinNo
    SELECT axis.remrate_data_windowtype.id INTO wtype_id FROM axis.remrate_data_windowtype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_windowtype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_windowtype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_windowtype.lWDTWinNo = NEW.LSSWWDWTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_sunspacewindow
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szSSWName`, `fSSWArea`, `nSSWOr`, `fSSWSum`, `fSSWWtr`, `lSSWWdwTNo`, `sSSWRateNo`, `fSSOHDepth`, `fSSOHToTop`, `fSSOHToBtm`, `fSSAdjSum`, `fSSAdjWtr`) VALUES
      ( wtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZSSWNAME, NEW.FSSWAREA, NEW.NSSWOR, NEW.FSSWSUM, NEW.FSSWWTR, NEW.LSSWWDWTNO, NEW.SSSWRATENO, NEW.FSSOHDEPTH, NEW.FSSOHTOTOP, NEW.FSSOHTOBTM, NEW.FSSADJSUM, NEW.FSSADJWTR );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_sssklght_copy_trigger` $$
CREATE TRIGGER after_sssklght_copy_trigger
    AFTER INSERT on SSSkLght FOR EACH ROW
    BEGIN

    -- Trigger #: 56 of 75 Source: SSSkLght Target: remrate_data_sunspaceskylight --

    DECLARE wtype_id INT;
    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    -- Figure out the lWDTWinNo
    SELECT axis.remrate_data_windowtype.id INTO wtype_id FROM axis.remrate_data_windowtype
      INNER JOIN axis.remrate_data_simulation ON (axis.remrate_data_windowtype.simulation_id = axis.remrate_data_simulation.id)
      INNER JOIN axis.remrate_data_datatracker ON (axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)
      WHERE (axis.remrate_data_windowtype.lBldgRunNo = NEW.LBLDGRUNNO AND axis.remrate_data_windowtype.lWDTWinNo = NEW.LSSSWDWTNO AND axis.remrate_data_datatracker.status = 0);

    INSERT INTO axis.remrate_data_sunspaceskylight
      (`type_id`, `simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `szSSSName`, `fSSSArea`, `nSSSOr`, `fSSSPitch`, `fSSSSum`, `fSSSWtr`, `lSSSWdwTNo`, `sSSSRateNo`) VALUES
      ( wtype_id, sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SZSSSNAME, NEW.FSSSAREA, NEW.NSSSOR, NEW.FSSSPITCH, NEW.FSSSSUM, NEW.FSSSWTR, NEW.LSSSWDWTNO, NEW.SSSSRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_resnetdisc_copy_trigger` $$
CREATE TRIGGER after_resnetdisc_copy_trigger
    AFTER INSERT on ResnetDisc FOR EACH ROW
    BEGIN

    -- Trigger #: 57 of 75 Source: ResnetDisc Target: remrate_data_resnetdisc --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_resnetdisc
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nRDQ1`, `nRDQ2A`, `nRDQ2B`, `nRDQ2C`, `nRDQ2D`, `nRDQ2E`, `SRDQ2EOTHR`, `nRDQ3A`, `nRDQ3B`, `nRDQ3C`, `NRDQ4HVACI`, `NRDQ4HVACB`, `NRDQ4THMLI`, `NRDQ4THMLB`, `NRDQ4AIRSI`, `NRDQ4AIRSB`, `NRDQ4WINI`, `NRDQ4WINB`, `NRDQ4APPLI`, `NRDQ4APPLB`, `NRDQ4CNSTI`, `NRDQ4CNSTB`, `NRDQ4OTHRI`, `NRDQ4OTHRB`, `SRDQ4OTHR`, `NRDQ5`, `sRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NRDQ1, NEW.NRDQ2A, NEW.NRDQ2B, NEW.NRDQ2C, NEW.NRDQ2D, NEW.NRDQ2E, NEW.SRDQ2EOTHR, NEW.NRDQ3A, NEW.NRDQ3B, NEW.NRDQ3C, NEW.NRDQ4HVACI, NEW.NRDQ4HVACB, NEW.NRDQ4THMLI, NEW.NRDQ4THMLB, NEW.NRDQ4AIRSI, NEW.NRDQ4AIRSB, NEW.NRDQ4WINI, NEW.NRDQ4WINB, NEW.NRDQ4APPLI, NEW.NRDQ4APPLB, NEW.NRDQ4CNSTI, NEW.NRDQ4CNSTB, NEW.NRDQ4OTHRI, NEW.NRDQ4OTHRB, NEW.SRDQ4OTHR, NEW.NRDQ5, NEW.SRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_esrequire_copy_trigger` $$
CREATE TRIGGER after_esrequire_copy_trigger
    AFTER INSERT on ESRequire FOR EACH ROW
    BEGIN

    -- Trigger #: 58 of 75 Source: ESRequire Target: remrate_data_energystarrequirements --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_energystarrequirements
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nESEQUIP`, `nESWINDOW`, `nESFIXTURE`, `nESAPPLI`, `nESCEILFAN`, `nESVENTFAN`, `nABOVERALL`, `nABGRBDJST`, `nABEVBFFLS`, `nABSLABEDG`, `nABBANDJST`, `nABTHMLBRG`, `nWLSHWRTUB`, `nWLFIREPLC`, `nWLATCSLPE`, `nWLATCKNEE`, `nWLSKYSHFT`, `nWLPORCHRF`, `nWLSTRCASE`, `nWLDOUBLE`, `nFLRABVGRG`, `nFLRCANTIL`, `nSHAFTDUCT`, `nSHAFTPIPE`, `nSHAFTFLUE`, `nATCACCPNL`, `nATDDSTAIR`, `nRFDRPSOFT`, `nRFRECSLGT`, `nRFHOMEFAN`, `nCWLBTWNUT`, `SRATENO`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NESEQUIP, NEW.NESWINDOW, NEW.NESFIXTURE, NEW.NESAPPLI, NEW.NESCEILFAN, NEW.NESVENTFAN, NEW.nABOVERALL, NEW.nABGRBDJST, NEW.nABEVBFFLS, NEW.nABSLABEDG, NEW.nABBANDJST, NEW.nABTHMLBRG, NEW.nWLSHWRTUB, NEW.nWLFIREPLC, NEW.nWLATCSLPE, NEW.nWLATCKNEE, NEW.nWLSKYSHFT, NEW.nWLPORCHRF, NEW.nWLSTRCASE, NEW.nWLDOUBLE, NEW.nFLRABVGRG, NEW.nFLRCANTIL, NEW.nSHAFTDUCT, NEW.nSHAFTPIPE, NEW.nSHAFTFLUE, NEW.nATCACCPNL, NEW.nATDDSTAIR, NEW.nRFDRPSOFT, NEW.nRFRECSLGT, NEW.nRFHOMEFAN, NEW.nCWLBTWNUT, NEW.SRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_fuelsummary_copy_trigger` $$
CREATE TRIGGER after_fuelsummary_copy_trigger
    AFTER INSERT on FuelSum FOR EACH ROW
    BEGIN

    -- Trigger #: 59 of 75 Source: FuelSum Target: remrate_data_fuelsummary --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Do not push the fFSTotCons versions < 14.0
    IF version_id IN ('12.5', '12.99A', '13.0') THEN
       INSERT INTO axis.remrate_data_fuelsummary
         (`simulation_id`, `lBldgRunNo`, `nFSFuel`, `nFSUnits`, `fFSHCons`, `fFSCCons`, `fFSWCons`, `fFSLACons`, `fFSTotCost`, `fFSPVCons`, `sRateNo`, `fFSTotCons` ) VALUES
         ( sim_id, NEW.LBLDGRUNNO, NEW.NFSFUEL, NEW.NFSUNITS, NEW.FFSHCONS, NEW.FFSCCONS, NEW.FFSWCONS, NEW.FFSLACONS, NEW.FFSTOTCOST, NEW.FFSPVCONS, NEW.SRATENO, NULL );
    ELSE
       INSERT INTO axis.remrate_data_fuelsummary
         (`simulation_id`, `lBldgRunNo`, `nFSFuel`, `nFSUnits`, `fFSHCons`, `fFSCCons`, `fFSWCons`, `fFSLACons`, `fFSTotCost`, `fFSPVCons`, `sRateNo`) VALUES
         ( sim_id, NEW.LBLDGRUNNO, NEW.NFSFUEL, NEW.NFSUNITS, NEW.FFSHCONS, NEW.FFSCCONS, NEW.FFSWCONS, NEW.FFSLACONS, NEW.FFSTOTCOST, NEW.FFSPVCONS, NEW.SRATENO );
    END IF;

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_economicparam_copy_trigger` $$
CREATE TRIGGER after_economicparam_copy_trigger
    AFTER INSERT on EconParam FOR EACH ROW
    BEGIN

    -- Trigger #: 60 of 75 Source: EconParam Target: remrate_data_economicparameters --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_economicparameters
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `sRateNo`, `nFSBaseline`, `sFSBldgName`, `fEPImpCost`, `fEPImpLife`, `fEPMortRat`, `fEPMortPer`, `fEPDownPay`, `fEPAppVal`, `fEPInf`, `fEPDisRate`, `fEPEnInf`, `fEPAnalPer`, `nEPImpLifeD`, `nEPMortRatD`, `nEPMortPerD`, `nEPDownPayD`, `nEPInfD`, `nEPDisRateD`, `nEPEnInfD`, `nEPAnalPerD`, `NEPDOECalc`, `NEPCalcMthd`) VALUES
      ( sim_id, bldg_id, NEW.LBldgRunNo, NEW.LBldgNo, NEW.SRateNo, NEW.NFSBaseline, NEW.SFSBldgName, NEW.fEPImpCost, NEW.FEPImpLife, NEW.FEPMortRat, NEW.FEPMortPer, NEW.FEPDownPay, NEW.FEPAppVal, NEW.FEPInf, NEW.FEPDisRate, NEW.FEPEnInf, NEW.FEPAnalPer, NEW.NEPImpLifeD, NEW.NEPMortRatD, NEW.NEPMortPerD, NEW.NEPDownPayD, NEW.NEPInfD, NEW.NEPDisRateD, NEW.NEPEnInfD, NEW.NEPAnalPerD, NEW.NEPDOECalc, NEW.NEPCalcMthd );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_result_copy_trigger` $$
CREATE TRIGGER after_result_copy_trigger
    AFTER INSERT on Results FOR EACH ROW
    BEGIN

    -- Trigger #: 61 of 75 Source: Results Target: remrate_data_results --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_results
      (`simulation_id`, `lBldgRunNo`, `FHCOST`, `FCCOST`, `FWCOST`, `FLATOTCOST`, `FPVTOTCOST`, `FSERVCOST`, `FTOTCOST`, `FHCONS`, `FCCONS`, `FWCONS`, `FLATOTCONS`, `FPVTOTCONS`, `FSHELLAREA`, `FHTEFF`, `FCLGEFF`, `FHWEFF`, `FLHROOF`, `FLCROOF`, `FLHJOIST`, `FLCJOIST`, `FLHAGWALL`, `FLCAGWALL`, `FLHFNDWALL`, `FLCFNDWALL`, `FLHWNDOSK`, `FLCWNDOSK`, `FLHFFLR`, `FLCFFLR`, `FLHCRAWL`, `FLCCRAWL`, `FLHSLAB`, `FLCSLAB`, `FLHINF`, `FLCINF`, `FLHMECHVNT`, `FLCMECHVNT`, `FLHDUCT`, `FLCDUCT`, `FLHASOL`, `FLCASOL`, `FLHSS`, `FLCSS`, `FLHIGAIN`, `FLCIGAIN`, `FLHWHF`, `FLCWHF`, `FLHDOOR`, `FLCDOOR`, `FLHTOTAL`, `FLCTOTAL`, `FTOTDHW`, `FSOLSAVE`, `FHTPEAK`, `FACSPEAK`, `FACLPEAK`, `FACTPEAK`, `FHBUCK`, `FACBUCK`, `FWBUCK`, `FREFRCONS`, `FFRZCONS`, `FDRYCONS`, `FOVENCONS`, `FLAOTHCONS`, `FLIHSCONS`, `FLICSCONS`, `FREFRCOST`, `FFRZCOST`, `FDRYCOST`, `FOVENCOST`, `FLAOTHCOST`, `FLIGHTCOST`, `FHTGLDPHDD`, `FCLGLDPHDD`, `FHTGDDPHDD`, `FCLGDDPHDD`, `FHTGACH`, `FCLGACH`, `SRATENO`, `FEMCO2TOT`, `FEMSO2TOT`, `FEMNOXTOT`, `FEMCO2HTG`, `FEMCO2CLG`, `FEMCO2DHW`, `FEMCO2LA`, `FEMCO2PV`, `FEMSO2HTG`, `FEMSO2CLG`, `FEMSO2DHW`, `FEMSO2LA`, `FEMSO2PV`, `FEMNOXHTG`, `FEMNOXCLG`, `FEMNOXDHW`, `FEMNOXLA`, `FEMNOXPV`, `FEMHERSCO2`, `FEMHERSSO2`, `FEMHERSNOX`, `FSRCEGYHTG`, `FSRCEGYCLG`, `FSRCEGYDHW`, `FSRCEGYLA`, `FSRCEGYPV`, `fDHWNoLoss`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.FHCOST, NEW.FCCOST, NEW.FWCOST, NEW.FLATOTCOST, NEW.FPVTOTCOST, NEW.FSERVCOST, NEW.FTOTCOST, NEW.FHCONS, NEW.FCCONS, NEW.FWCONS, NEW.FLATOTCONS, NEW.FPVTOTCONS, NEW.FSHELLAREA, NEW.FHTEFF, NEW.FCLGEFF, NEW.FHWEFF, NEW.FLHROOF, NEW.FLCROOF, NEW.FLHJOIST, NEW.FLCJOIST, NEW.FLHAGWALL, NEW.FLCAGWALL, NEW.FLHFNDWALL, NEW.FLCFNDWALL, NEW.FLHWNDOSK, NEW.FLCWNDOSK, NEW.FLHFFLR, NEW.FLCFFLR, NEW.FLHCRAWL, NEW.FLCCRAWL, NEW.FLHSLAB, NEW.FLCSLAB, NEW.FLHINF, NEW.FLCINF, NEW.FLHMECHVNT, NEW.FLCMECHVNT, NEW.FLHDUCT, NEW.FLCDUCT, NEW.FLHASOL, NEW.FLCASOL, NEW.FLHSS, NEW.FLCSS, NEW.FLHIGAIN, NEW.FLCIGAIN, NEW.FLHWHF, NEW.FLCWHF, NEW.FLHDOOR, NEW.FLCDOOR, NEW.FLHTOTAL, NEW.FLCTOTAL, NEW.FTOTDHW, NEW.FSOLSAVE, NEW.FHTPEAK, NEW.FACSPEAK, NEW.FACLPEAK, NEW.FACTPEAK, NEW.FHBUCK, NEW.FACBUCK, NEW.FWBUCK, NEW.FREFRCONS, NEW.FFRZCONS, NEW.FDRYCONS, NEW.FOVENCONS, NEW.FLAOTHCONS, NEW.FLIHSCONS, NEW.FLICSCONS, NEW.FREFRCOST, NEW.FFRZCOST, NEW.FDRYCOST, NEW.FOVENCOST, NEW.FLAOTHCOST, NEW.FLIGHTCOST, NEW.FHTGLDPHDD, NEW.FCLGLDPHDD, NEW.FHTGDDPHDD, NEW.FCLGDDPHDD, NEW.FHTGACH, NEW.FCLGACH, NEW.SRATENO, NEW.FEMCO2TOT, NEW.FEMSO2TOT, NEW.FEMNOXTOT, NEW.FEMCO2HTG, NEW.FEMCO2CLG, NEW.FEMCO2DHW, NEW.FEMCO2LA, NEW.FEMCO2PV, NEW.FEMSO2HTG, NEW.FEMSO2CLG, NEW.FEMSO2DHW, NEW.FEMSO2LA, NEW.FEMSO2PV, NEW.FEMNOXHTG, NEW.FEMNOXCLG, NEW.FEMNOXDHW, NEW.FEMNOXLA, NEW.FEMNOXPV, NEW.FEMHERSCO2, NEW.FEMHERSSO2, NEW.FEMHERSNOX, NEW.FSRCEGYHTG, NEW.FSRCEGYCLG, NEW.FSRCEGYDHW, NEW.FSRCEGYLA, NEW.FSRCEGYPV, NEW.fDHWNoLoss );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_compliance_copy_trigger` $$
CREATE TRIGGER after_compliance_copy_trigger
    AFTER INSERT on Compliance FOR EACH ROW
    BEGIN

    -- Trigger #: 62 of 75 Source: Compliance Target: remrate_data_compliance --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    -- Do not push the flavor on some new compliance pieces
    IF version_id IN ('12.5', '12.99A', '13.0') THEN
       INSERT INTO axis.remrate_data_compliance
         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, `fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, `fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, `fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, `b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, `bEStarv3`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, `f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, `f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, `f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, `f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, `f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, `f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, `f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, `f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, `f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, `f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, `f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, `f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, `f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, `f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, `b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, `f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, `b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, `f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, `b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, `f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, `f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, `f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, `f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, `f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, `f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, `b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, `sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, `f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, `f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, `b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, `bPass12IECC`, `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES
         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS, NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, NEW.BTAXCREDIT, NEW.B90_2ASCCP, NULL, NEW.F98IERHCN, NEW.F98IERCCN, NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, NEW.F03IEDTCN, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, NEW.FNYECDTCN, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, NEW.B92MECDUP, NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, NEW.B93MECUOP, NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, NEW.B03IECCUOP, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, NEW.F92MECRCCN, NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, NEW.F92MECDHCN, NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, NEW.F92MECDTCN, NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, NEW.F93MECRLCN, NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, NEW.F93MECDDCN, NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, NEW.F95MECRHCN, NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, NEW.F95MECRTCN, NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, NEW.F95MECDPCN, NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, NEW.F90_2ASRCN, NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, NEW.SRATENO, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, NEW.BPASS04IECC, NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NULL, NULL, NULL, NULL );
    ELSEIF version_id IN ('14.0', '14.1', '14.2') THEN
       INSERT INTO axis.remrate_data_compliance
         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, `fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, `fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, `fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, `b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, `bEStarv3`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, `f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, `f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, `f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, `f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, `f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, `f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, `f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, `f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, `f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, `f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, `f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, `f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, `f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, `f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, `b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, `f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, `b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, `f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, `b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, `f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, `f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, `f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, `f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, `f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, `f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, `b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, `sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, `f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, `f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, `b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, `bPass12IECC`, `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES
         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS, NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, NEW.BTAXCREDIT, NEW.B90_2ASCCP, NEW.FES_SZADJF, NEW.F98IERHCN, NEW.F98IERCCN, NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, NEW.F03IEDTCN, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, NEW.FNYECDTCN, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, NEW.B92MECDUP, NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, NEW.B93MECUOP, NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, NEW.B03IECCUOP, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, NEW.F92MECRCCN, NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, NEW.F92MECDHCN, NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, NEW.F92MECDTCN, NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, NEW.F93MECRLCN, NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, NEW.F93MECDDCN, NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, NEW.F95MECRHCN, NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, NEW.F95MECRTCN, NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, NEW.F95MECDPCN, NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, NEW.F90_2ASRCN, NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, NEW.SRATENO, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, NEW.BPASS04IECC, NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NULL, NEW.FHERS130, NULL, NULL );
    ELSEIF version_id IN ('14.3') THEN
       INSERT INTO axis.remrate_data_compliance
         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, `fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, `fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, `fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, `b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, `bEStarv3`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, `f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, `f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, `f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, `f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, `f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, `f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, `f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, `f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, `f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, `f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, `f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, `f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, `f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, `f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, `b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, `f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, `b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, `f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, `b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, `f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, `f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, `f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, `f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, `f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, `f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, `b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, `sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, `f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, `f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, `b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, `bPass12IECC`, `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES
         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS, NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, NEW.BTAXCREDIT, NEW.B90_2ASCCP, NEW.FES_SZADJF, NEW.F98IERHCN, NEW.F98IERCCN, NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, NEW.F03IEDTCN, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, NEW.FNYECDTCN, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, NEW.B92MECDUP, NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, NEW.B93MECUOP, NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, NEW.B03IECCUOP, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, NEW.F92MECRCCN, NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, NEW.F92MECDHCN, NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, NEW.F92MECDTCN, NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, NEW.F93MECRLCN, NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, NEW.F93MECDDCN, NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, NEW.F95MECRHCN, NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, NEW.F95MECRTCN, NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, NEW.F95MECDPCN, NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, NEW.F90_2ASRCN, NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, NEW.SRATENO, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, NEW.BPASS04IECC, NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NEW.BDOECHALL, NEW.FHERS130, NULL, NULL );
    ELSE
       INSERT INTO axis.remrate_data_compliance
         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, `fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, `fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, `fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, `b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, `bEStarv3`, `bESTARV31`, `bESTARV3HI`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, `f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, `f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, `f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, `f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, `f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, `f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, `f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, `f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, `f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, `f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, `f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, `f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, `f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, `f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, `b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, `f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, `b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, `f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, `b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, `f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, `f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, `f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, `f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, `f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, `f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, `b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, `sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, `f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, `f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, `b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, `bPass12IECC`, `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES
         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS, NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, NEW.bESTARV31, NEW.bESTARV3HI, NEW.BTAXCREDIT, NEW.B90_2ASCCP, NEW.FES_SZADJF, NEW.F98IERHCN, NEW.F98IERCCN, NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, NEW.F03IEDTCN, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, NEW.FNYECDTCN, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, NEW.B92MECDUP, NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, NEW.B93MECUOP, NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, NEW.B03IECCUOP, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, NEW.F92MECRCCN, NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, NEW.F92MECDHCN, NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, NEW.F92MECDTCN, NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, NEW.F93MECRLCN, NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, NEW.F93MECDDCN, NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, NEW.F95MECRHCN, NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, NEW.F95MECRTCN, NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, NEW.F95MECDPCN, NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, NEW.F90_2ASRCN, NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, NEW.SRATENO, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, NEW.BPASS04IECC, NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NEW.bDOECHALL, NEW.FHERS130, NEW.FDOE_Hers, NEW.FDOE_HersSA );
    END IF;
    INSERT INTO axis.remrate_data_regionalcode
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `fNVRebate`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `bNYECC`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, `bNVECC`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.SRATENO, NEW.FNVREBATE, NEW.FNYECRHCN, NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, NEW.FNYECDTCN, NEW.BNYECC, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.BNVECC);
    INSERT INTO axis.remrate_data_energystar
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `BESTARV2`, `BESTARV25`, `BESTARV3`, `FV25HERSPV`, `FV25HERS`, `FV25HERSSA`, `FV25SZADJF`, `BESTARV3HI`, `BESTARV31`, `BDOEPROGRAM`, `FDOEHERS`, `FDOEHERSSA`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.SRATENO, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, NEW.FHERS_PV, NEW.FES_HERS, NEW.FES_HERSSA, NEW.FES_SZADJF, NEW.BESTARV3HI, NEW.BESTARV31, NEW.BDOECHALL, NEW.FDOE_HERS, NEW.FDOE_HersSA);
    INSERT INTO axis.remrate_data_hers
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `fHERSScor`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, `fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, `fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `FNYHERS`, `bTaxCredit`, `FHERS130`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.SRATENO, NEW.FHERSSCOR, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, NEW.FNYHERS, NEW.BTAXCREDIT, NEW.FHERS130);

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_regionalcode_copy_trigger` $$
CREATE TRIGGER after_regionalcode_copy_trigger
    AFTER INSERT on RegionalCode FOR EACH ROW
    BEGIN

    -- Trigger #: 63 of 75 Source: RegionalCode Target: remrate_data_regionalcode --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_regionalcode
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `fNVRebate`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `bNYECC`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, `bNVECC`, `fNCRHCT`, `fNCRCCT`, `fNCRDCT`, `fNCRLACT`, `fNCRPVCT`, `fNCRSVCT`, `fNCRTCT`, `fNCDHCT`, `fNCDCCT`, `fNCDDCT`, `fNCDLACT`, `fNCDPVCT`, `fNCDSVCT`, `fNCDTCT`, `bNCMeetCT`, `fNCRUA`, `fNCDUA`, `bNCDctPass`, `bNCUAPass`, `bNCPass`, `fNCHRHCT`, `fNCHRCCT`, `fNCHRDCT`, `fNCHRLACT`, `fNCHRPVCT`, `fNCHRSVCT`, `fNCHRTCT`, `fNCHDHCT`, `fNCHDCCT`, `fNCHDDCT`, `fNCHDLACT`, `fNCHDPVCT`, `fNCHDSVCT`, `fNCHDTCT`, `bNCHMeetCT`, `fNCHRUA`, `fNCHDUA`, `bNCHDctPass`, `bNCHUAPass`, `bNCHPass`, `FNYRHCT`, `FNYRCCT`, `FNYRDCT`, `FNYRLACT`, `FNYRPVCT`, `FNYRSVCT`, `FNYRTCT`, `FNYDHCT`, `FNYDCCT`, `FNYDDCT`, `FNYDLACT`, `FNYDPVCT`, `FNYDSVCT`, `FNYDTCT`, `BNYMEETCT`, `FNYRUA`, `FNYDUA`, `BNYDCTPASS`, `BNYUAPASS`, `BNYPASS`, `FNYDMVCT`, `FNYRMVCT`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.SRATENO, NEW.fNVRebate, NEW.fNYECRHCn, NEW.fNYECRCCn, NEW.fNYECRDCN, NEW.fNYECRLACn, NEW.fNYECRPVCn, NEW.fNYECRTCn, NEW.fNYECDHCn, NEW.fNYECDCCn, NEW.fNYECDDCN, NEW.fNYECDLACn, NEW.fNYECDPVCn, NEW.fNYECDTCn, NEW.bNYECC, NEW.fNVECRHCn, NEW.fNVECRCCn, NEW.fNVECRDCN, NEW.fNVECRLACn, NEW.fNVECRPVCn, NEW.fNVECRTCn, NEW.fNVECDHCn, NEW.fNVECDCCn, NEW.fNVECDDCN, NEW.fNVECDLACn, NEW.fNVECDPVCn, NEW.fNVECDTCn, NEW.bNVECC, NEW.fNCRHCT, NEW.fNCRCCT, NEW.fNCRDCT, NEW.fNCRLACT, NEW.fNCRPVCT, NEW.fNCRSVCT, NEW.fNCRTCT, NEW.fNCDHCT, NEW.fNCDCCT, NEW.fNCDDCT, NEW.fNCDLACT, NEW.fNCDPVCT, NEW.fNCDSVCT, NEW.fNCDTCT, NEW.bNCMeetCT, NEW.fNCRUA, NEW.fNCDUA, NEW.bNCDctPass, NEW.bNCUAPass, NEW.bNCPass, NEW.fNCHRHCT, NEW.fNCHRCCT, NEW.fNCHRDCT, NEW.fNCHRLACT, NEW.fNCHRPVCT, NEW.fNCHRSVCT, NEW.fNCHRTCT, NEW.fNCHDHCT, NEW.fNCHDCCT, NEW.fNCHDDCT, NEW.fNCHDLACT, NEW.fNCHDPVCT, NEW.fNCHDSVCT, NEW.fNCHDTCT, NEW.bNCHMeetCT, NEW.fNCHRUA, NEW.fNCHDUA, NEW.bNCHDctPass, NEW.bNCHUAPass, NEW.bNCHPass, NEW.FNYRHCT, NEW.FNYRCCT, NEW.FNYRDCT, NEW.FNYRLACT, NEW.FNYRPVCT, NEW.FNYRSVCT, NEW.FNYRTCT, NEW.FNYDHCT, NEW.FNYDCCT, NEW.FNYDDCT, NEW.FNYDLACT, NEW.FNYDPVCT, NEW.FNYDSVCT, NEW.FNYDTCT, NEW.BNYMEETCT, NEW.FNYRUA, NEW.FNYDUA, NEW.BNYDCTPASS, NEW.BNYUAPASS, NEW.BNYPASS, NEW.FNYDMVCT, NEW.FNYRMVCT );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_hers_copy_trigger` $$
CREATE TRIGGER after_hers_copy_trigger
    AFTER INSERT on HERSCode FOR EACH ROW
    BEGIN

    -- Trigger #: 64 of 75 Source: HERSCode Target: remrate_data_hers --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_hers
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `fHERSScor`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, `fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, `fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `FNYHERS`, `bTaxCredit`, `FHERS130`, `NBADORIENT`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.SRATENO, NEW.fHERSScor, NEW.fHERSCost, NEW.fHERSStars, NEW.fHERSRHCn, NEW.fHERSRCCn, NEW.fHERSRDCN, NEW.fHERSRLACn, NEW.fHERSRPVCn, NEW.fHERSRTCn, NEW.fHERSDHCn, NEW.fHERSDCCn, NEW.fHERSDDCN, NEW.fHERSDLACn, NEW.fHERSDPVCn, NEW.fHERSDTCn, NEW.FNYHERS, NEW.bTaxCredit, NEW.FHERS130, NEW.NBADORIENT );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_energystar_copy_trigger` $$
CREATE TRIGGER after_energystar_copy_trigger
    AFTER INSERT on ENERGYSTAR FOR EACH ROW
    BEGIN

    -- Trigger #: 65 of 75 Source: ENERGYSTAR Target: remrate_data_energystar --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_energystar
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `BESTARV2`, `BESTARV25`, `FV25HERSPV`, `FV25HERS`, `FV25HERSSA`, `FV25SZADJF`, `BESTARV3`, `FV3HERSPV`, `FV3HERS`, `FV3HERSSA`, `FV3SZADJF`, `BESTARV3HI`, `FV3HIHERSPV`, `FV3HIHERS`, `FV3HIHERSSA`, `FV3HISZADJF`, `BESTARV31`, `FV31HERSPV`, `FV31HERS`, `FV31HERSSA`, `FV31SZADJF`, `BESTARV32W`, `FV32WHERSPV`, `FV32WHERS`, `FV32WHERSSA`, `FV32WSZADJF`, `BDOEPROGRAM`, `FDOEHERS`, `FDOEHERSSA`, `bESTARV10MF`, `FV10MFHERSPV`, `FV10MFHERS`, `BESTARV11MF`, `FV11MFHERSPV`, `FV11MFHERS`, `BESTARV12MF`, `FV12MFHERSPV`, `FV12MFHERS`) VALUES
      ( sim_id, NEW.lBldgRunNo, NEW.SRATENO, NEW.BESTARV2, NEW.BESTARV25, NEW.FV25HERSPV, NEW.FV25HERS, NEW.FV25HERSSA, NEW.FV25SZADJF, NEW.BESTARV3, NEW.FV3HERSPV, NEW.FV3HERS, NEW.FV3HERSSA, NEW.FV3SZADJF, NEW.BESTARV3HI, NEW.FV3HIHERSPV, NEW.FV3HIHERS, NEW.FV3HIHERSSA, NEW.FV3HISZADJF, NEW.BESTARV31, NEW.FV31HERSPV, NEW.FV31HERS, NEW.FV31HERSSA, NEW.FV31SZADJF, NEW.BESTARV32W, NEW.FV32WHERSPV, NEW.FV32WHERS, NEW.FV32WHERSSA, NEW.FV32WSZADJF, NEW.BDOEPROGRAM, NEW.FDOEHERS, NEW.FDOEHERSSA, NEW.bESTARV10MF, NEW.FV10MFHERSPV, NEW.FV10MFHERS, NEW.BESTARV11MF, NEW.FV11MFHERSPV, NEW.FV11MFHERS, NEW.BESTARV12MF, NEW.FV12MFHERSPV, NEW.FV12MFHERS );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_iecc_copy_trigger` $$
CREATE TRIGGER after_iecc_copy_trigger
    AFTER INSERT on IECC FOR EACH ROW
    BEGIN

    -- Trigger #: 66 of 75 Source: IECC Target: remrate_data_iecc --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_iecc
      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `f98IERHCn`, `f98IERCCn`, `f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, `f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `b98IECC`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, `f00IERHCn`, `f00IERCCn`, `f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, `f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `b00IECC`, `f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IERHCn`, `f01IERCCn`, `f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, `f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `b01IECC`, `f01IECCRUo`, `f01IECCDUo`, `b01IECCDuP`, `b01IECCuoP`, `f03IERHCn`, `f03IERCCn`, `f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, `f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `b03IECC`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, `f04IERHCT`, `f04IERCCT`, `f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, `f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, `b04IECC`, `f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `bPass04IECC`, `f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, `f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, `f06IEDSVCT`, `f06IEDTCT`, `b06IECC`, `f06IECCRUA`, `f06IECCDUA`, `b06IECCDuP`, `b06IECCuAP`, `bPass06IECC`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, `f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, `f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `b09IECC`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, `b09IECCuAP`, `bPass09IECC`, `f12IERHCT`, `f12IERCCT`, `f12IERDCT`, `f12IERLACT`, `f12IERPVCT`, `f12IERSVCT`, `f12IERTCT`, `f12IEDHCT`, `f12IEDCCT`, `f12IEDDCT`, `f12IEDLACT`, `f12IEDPVCT`, `f12IEDSVCT`, `f12IEDTCT`, `b12IECC`, `f12IECCRUA`, `f12IECCDUA`, `b12IECCDuP`, `b12IECCuAP`, `bPass12IECC`, `f15IERHCT`, `f15IERCCT`, `f15IERDCT`, `f15IERLACT`, `f15IERPVCT`, `f15IERSVCT`, `f15IERTCT`, `f15IEDHCT`, `f15IEDCCT`, `f15IEDDCT`, `f15IEDLACT`, `f15IEDPVCT`, `f15IEDSVCT`, `f15IEDTCT`, `b15IECC`, `f15IECCRUA`, `f15IECCDUA`, `b15IECCDuP`, `b15IECCuAP`, `bPass15IECC`, `f18IERHCT`, `f18IERCCT`, `f18IERDCT`, `f18IERLACT`, `f18IERPVCT`, `f18IERSVCT`, `f18IERTCT`, `f18IEDHCT`, `f18IEDCCT`, `f18IEDDCT`, `f18IEDLACT`, `f18IEDPVCT`, `f18IEDSVCT`, `f18IEDTCT`, `b18IECC`, `f18IECCRUA`, `f18IECCDUA`, `b18IECCDuP`, `b18IECCuAP`, `bPass18IECC`, `f18IERMVCT`, `f18IEDMVCT`, `f21IERHCT`, `f21IERCCT`, `f21IERDCT`, `f21IERLACT`, `f21IERMVCT`, `f21IERPVCT`, `f21IERSVCT`, `f21IERTCT`, `f21IEDHCT`, `f21IEDCCT`, `f21IEDDCT`, `f21IEDLACT`, `f21IEDMVCT`, `f21IEDPVCT`, `f21IEDSVCT`, `f21IEDTCT`, `b21IECC`, `f21IECCRUA`, `f21IECCDUA`, `b21IECCDuP`, `b21IECCuAP`, `bPass21IECC`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.SRATENO, NEW.F98IERHCN, NEW.F98IERCCN, NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, NEW.B98IECC, NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.B00IECC, NEW.F00IECCRUO, NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.B01IECC, NEW.F01IECCRUO, NEW.F01IECCDUO, NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IERHCN, NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, NEW.F03IEDTCN, NEW.B03IECC, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, NEW.B03IECCUOP, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, NEW.B04IECC, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, NEW.bPass04IECC, NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.B06IECC, NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.bPass06IECC, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, NEW.B09IECC, NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.bPass09IECC, NEW.F12IERHCT, NEW.F12IERCCT, NEW.F12IERDCT, NEW.F12IERLACT, NEW.F12IERPVCT, NEW.F12IERSVCT, NEW.F12IERTCT, NEW.F12IEDHCT, NEW.F12IEDCCT, NEW.F12IEDDCT, NEW.F12IEDLACT, NEW.F12IEDPVCT, NEW.F12IEDSVCT, NEW.F12IEDTCT, NEW.B12IECC, NEW.F12IECCRUA, NEW.F12IECCDUA, NEW.B12IECCDUP, NEW.B12IECCUAP, NEW.bPass12IECC, NEW.F15IERHCT, NEW.F15IERCCT, NEW.F15IERDCT, NEW.F15IERLACT, NEW.F15IERPVCT, NEW.F15IERSVCT, NEW.F15IERTCT, NEW.F15IEDHCT, NEW.F15IEDCCT, NEW.F15IEDDCT, NEW.F15IEDLACT, NEW.F15IEDPVCT, NEW.F15IEDSVCT, NEW.F15IEDTCT, NEW.B15IECC, NEW.F15IECCRUA, NEW.F15IECCDUA, NEW.B15IECCDUP, NEW.B15IECCUAP, NEW.bPass15IECC, NEW.f18IERHCT, NEW.f18IERCCT, NEW.f18IERDCT, NEW.f18IERLACT, NEW.f18IERPVCT, NEW.f18IERSVCT, NEW.f18IERTCT, NEW.f18IEDHCT, NEW.f18IEDCCT, NEW.f18IEDDCT, NEW.f18IEDLACT, NEW.f18IEDPVCT, NEW.f18IEDSVCT, NEW.f18IEDTCT, NEW.b18IECC, NEW.f18IECCRUA, NEW.f18IECCDUA, NEW.b18IECCDuP, NEW.b18IECCuAP, NEW.bPass18IECC, NEW.f18IERMVCT, NEW.f18IEDMVCT, NEW.f21IERHCT, NEW.f21IERCCT, NEW.f21IERDCT, NEW.f21IERLACT, NEW.f21IERMVCT, NEW.f21IERPVCT, NEW.f21IERSVCT, NEW.f21IERTCT, NEW.f21IEDHCT, NEW.f21IEDCCT, NEW.f21IEDDCT, NEW.f21IEDLACT, NEW.f21IEDMVCT, NEW.f21IEDPVCT, NEW.f21IEDSVCT, NEW.f21IEDTCT, NEW.b21IECC, NEW.f21IECCRUA, NEW.f21IECCDUA, NEW.b21IECCDuP, NEW.b21IECCuAP, NEW.bPass21IECC );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_costrate_copy_trigger` $$
CREATE TRIGGER after_costrate_copy_trigger
    AFTER INSERT on CostRate FOR EACH ROW
    BEGIN

    -- Trigger #: 67 of 75 Source: CostRate Target: remrate_data_costrate --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_costrate
      (`simulation_id`, `lCRCRNo`, `lBldgRunNo`, `fCRHtg`, `fCRHtg2`, `fCRHtgSav`, `fCRClg`, `fCRClg2`, `fCRClgSav`, `fCRHW`, `fCRHW2`, `fCRHWSav`, `fCRLA`, `fCRLA2`, `fCRLASav`, `fCRSC`, `fCRSC2`, `fCRSCSav`, `fCRTot`, `fCRTot2`, `fCRTotSav`, `fCRRating`, `fCRRating2`, `fCR1YCF`) VALUES
      ( sim_id, NEW.LCRCRNO, NEW.LBLDGRUNNO, NEW.FCRHTG, NEW.FCRHTG2, NEW.FCRHTGSAV, NEW.FCRCLG, NEW.FCRCLG2, NEW.FCRCLGSAV, NEW.FCRHW, NEW.FCRHW2, NEW.FCRHWSAV, NEW.FCRLA, NEW.FCRLA2, NEW.FCRLASAV, NEW.FCRSC, NEW.FCRSC2, NEW.FCRSCSAV, NEW.FCRTOT, NEW.FCRTOT2, NEW.FCRTOTSAV, NEW.FCRRATING, NEW.FCRRATING2, NEW.FCR1YCF );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_accmeas_copy_trigger` $$
CREATE TRIGGER after_accmeas_copy_trigger
    AFTER INSERT on AccMeas FOR EACH ROW
    BEGIN

    -- Trigger #: 68 of 75 Source: AccMeas Target: remrate_data_acceptedmeasure --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_acceptedmeasure
      (`simulation_id`, `lBldgRunNo`, `lAMAMNo`, `lAMCRNo`, `lAMParNo`, `nAMMult`, `sAMComp`, `sAMExist`, `sAMProp`, `sAMTreat`, `sAMTreatD`, `fAMLife`, `fAMCost`, `fAMYrSav`, `fAMSIR`, `fAMPVSav`, `fAMSP`, `fAMRating`, `fAM1YCF`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LAMAMNO, NEW.LAMCRNO, NEW.LAMPARNO, NEW.NAMMULT, NEW.SAMCOMP, NEW.SAMEXIST, NEW.SAMPROP, NEW.SAMTREAT, NEW.SAMTREATD, NEW.FAMLIFE, NEW.FAMCOST, NEW.FAMYRSAV, NEW.FAMSIR, NEW.FAMPVSAV, NEW.FAMSP, NEW.FAMRATING, NEW.FAM1YCF );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_rejmeas_copy_trigger` $$
CREATE TRIGGER after_rejmeas_copy_trigger
    AFTER INSERT on RejMeas FOR EACH ROW
    BEGIN

    -- Trigger #: 69 of 75 Source: RejMeas Target: remrate_data_rejectedmeasure --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_rejectedmeasure
      (`simulation_id`, `lBldgRunNo`, `lRMRMNo`, `lRMCRNo`, `lRMParNo`, `nRMMult`, `sRMComp`, `sRMExist`, `sRMProp`, `sRMTreat`, `sRMTreatD`, `fRMLife`, `fRMCost`, `nRMRejReas`, `sRMRejReas`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LRMRMNO, NEW.LRMCRNO, NEW.LRMPARNO, NEW.NRMMULT, NEW.SRMCOMP, NEW.SRMEXIST, NEW.SRMPROP, NEW.SRMTREAT, NEW.SRMTREATD, NEW.FRMLIFE, NEW.FRMCOST, NEW.NRMREJREAS, NEW.SRMREJREAS );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_econ_copy_trigger` $$
CREATE TRIGGER after_econ_copy_trigger
    AFTER INSERT on Econ FOR EACH ROW
    BEGIN

    -- Trigger #: 70 of 75 Source: Econ Target: remrate_data_economic --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_economic
      (`simulation_id`, `lBldgRunNo`, `lECECNo`, `lECCRNo`, `fECImpCst`, `fECWtLife`, `nECMorTerm`, `fECMorRate`, `fECPVF`, `fECSavTot`, `fECMaint`, `fECNetSav`, `fECMorCst`, `fECPVSav`, `nECRankCr`, `fECCutoff`, `fECMaxLim`, `nECMeasInt`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.LECECNO, NEW.LECCRNO, NEW.FECIMPCST, NEW.FECWTLIFE, NEW.NECMORTERM, NEW.FECMORRATE, NEW.FECPVF, NEW.FECSAVTOT, NEW.FECMAINT, NEW.FECNETSAV, NEW.FECMORCST, NEW.FECPVSAV, NEW.NECRANKCR, NEW.FECCUTOFF, NEW.FECMAXLIM, NEW.NECMEASINT );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_simpinp_copy_trigger` $$
CREATE TRIGGER after_simpinp_copy_trigger
    AFTER INSERT on SimpInp FOR EACH ROW
    BEGIN

    -- Trigger #: 71 of 75 Source: SimpInp Target: remrate_data_simplifiedinput --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_simplifiedinput
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nSIHseType`, `nSIFndType`, `fSIFndPesl`, `fSIFndPeoc`, `fSIFndPeec`, `fSIFndPeHC`, `fSIFndPeUF`, `fSIFndPeHF`, `fSIFndPeUW`, `fSIFndPeHW`, `fSICFlArea`, `nSIBedRms`, `fSIPFlArHB`, `fSIPFlArFL`, `fSIPFlArML`, `fSIPFlArSL`, `fSIPFlArTL`, `nSINoCrnHB`, `nSINoCrnFL`, `nSINoCrnML`, `nSINoCrnSL`, `nSINoCrnTL`, `fSIPOAboHB`, `fSIPOAboFL`, `fSIPOAboML`, `fSIPOAboSL`, `fSIPOAboTL`, `fSICeilHHB`, `fSICeilHFL`, `fSICeilHML`, `fSICeilHSL`, `fSICeilHTL`, `fSIPOGrge`, `fSIPCathHB`, `fSIPCathFL`, `fSIPCathML`, `fSIPCathSL`, `fSIPCathTL`, `fSIInfRate`, `nSIInfMTyp`, `nSIInfUnit`, `nSINoDoors`, `fSISlbDBmt`, `fSlbD1L`, `lSIClgT1No`, `lSIClgT2No`, `lSIWalT1No`, `lSIWalT2No`, `lSIFndWTNo`, `lSIFlrTyNo`, `lSIDorTyNo`, `lSISlbTyNo`, `sSIRateNo`, `fSIBoxLen`, `fSIBoxWid`, `fSIBoxHgt`, `nSILvAbGar`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NSIHSETYPE, NEW.NSIFNDTYPE, NEW.FSIFNDPESL, NEW.FSIFNDPEOC, NEW.FSIFNDPEEC, NEW.FSIFNDPEHC, NEW.FSIFNDPEUF, NEW.FSIFNDPEHF, NEW.FSIFNDPEUW, NEW.FSIFNDPEHW, NEW.FSICFLAREA, NEW.NSIBEDRMS, NEW.FSIPFLARHB, NEW.FSIPFLARFL, NEW.FSIPFLARML, NEW.FSIPFLARSL, NEW.FSIPFLARTL, NEW.NSINOCRNHB, NEW.NSINOCRNFL, NEW.NSINOCRNML, NEW.NSINOCRNSL, NEW.NSINOCRNTL, NEW.FSIPOABOHB, NEW.FSIPOABOFL, NEW.FSIPOABOML, NEW.FSIPOABOSL, NEW.FSIPOABOTL, NEW.FSICEILHHB, NEW.FSICEILHFL, NEW.FSICEILHML, NEW.FSICEILHSL, NEW.FSICEILHTL, NEW.FSIPOGRGE, NEW.FSIPCATHHB, NEW.FSIPCATHFL, NEW.FSIPCATHML, NEW.FSIPCATHSL, NEW.FSIPCATHTL, NEW.FSIINFRATE, NEW.NSIINFMTYP, NEW.NSIINFUNIT, NEW.NSINODOORS, NEW.FSISLBDBMT, NEW.FSLBD1L, NEW.LSICLGT1NO, NEW.LSICLGT2NO, NEW.LSIWALT1NO, NEW.LSIWALT2NO, NEW.LSIFNDWTNO, NEW.LSIFLRTYNO, NEW.LSIDORTYNO, NEW.LSISLBTYNO, NEW.SSIRATENO, NEW.FSIBOXLEN, NEW.FSIBOXWID, NEW.FSIBOXHGT, NEW.NSILVABGAR );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_nevmeas_copy_trigger` $$
CREATE TRIGGER after_nevmeas_copy_trigger
    AFTER INSERT on NevMeas FOR EACH ROW
    BEGIN

    -- Trigger #: 72 of 75 Source: NevMeas Target: remrate_data_nevmeas --

    INSERT INTO axis.remrate_data_nevmeas
      (`lNMNMNo`, `sNMCity`, `sNMHouse`, `sNMFnd`, `sNMHTG`, `sNMCLG`, `sNMDHWFT`, `sNMMEATYP`, `sNMMEADSC`, `fNMKWH`, `fNMTherm`) VALUES
      ( NEW.LNMNMNO, NEW.SNMCITY, NEW.SNMHOUSE, NEW.SNMFND, NEW.SNMHTG, NEW.SNMCLG, NEW.SNMDHWFT, NEW.SNMMEATYP, NEW.SNMMEADSC, NEW.FNMKWH, NEW.FNMTHERM );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_florida_copy_trigger` $$
CREATE TRIGGER after_florida_copy_trigger
    AFTER INSERT on Florida FOR EACH ROW
    BEGIN

    -- Trigger #: 73 of 75 Source: Florida Target: remrate_data_florida --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_florida
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nType`, `nWorstCase`, `sPermitOff`, `sPermitNo`, `sJurisdctn`, `sRateNo`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NTYPE, NEW.NWORSTCASE, NEW.SPERMITOFF, NEW.SPERMITNO, NEW.SJURISDCTN, NEW.SRATENO );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_hercinfo_copy_trigger` $$
CREATE TRIGGER after_hercinfo_copy_trigger
    AFTER INSERT on HercInfo FOR EACH ROW
    BEGIN

    -- Trigger #: 74 of 75 Source: HercInfo Target: remrate_data_hercinfo --

    DECLARE sim_id INT;
    DECLARE bldg_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;
    DECLARE lbldgno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;
    SET lbldgno_id=NEW.LBLDGNO;

    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgNo`=NEW.LBLDGNO AND `lBldgRunNo`=NEW.LBLDGRUNNO AND `status`=0) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_hercinfo
      (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `sHIUsrItem`, `sHIITMTYPE`) VALUES
      ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SHIUSRITEM, NEW.SHIITMTYPE );

    -- Done doing stuff.. --

    END $$

DROP TRIGGER IF EXISTS `after_site_copy_trigger` $$
CREATE TRIGGER after_site_copy_trigger
    AFTER INSERT on Site FOR EACH ROW
    BEGIN

    -- Trigger #: 75 of 75 Source: Site Target: remrate_data_site --

    DECLARE sim_id INT;
    DECLARE version_id varchar(12);
    DECLARE lbldgrunno_id INT;

    SET lbldgrunno_id=NEW.LBLDGRUNNO;

    SELECT simulation_id, version INTO sim_id, version_id FROM axis.remrate_data_datatracker WHERE
      (`lBldgRunNo`=NEW.LBLDGRUNNO AND `status` IN (0,-1)) ORDER BY -id LIMIT 1;

    INSERT INTO axis.remrate_data_site
      (`simulation_id`, `lBldgRunNo`, `szSELabel`, `ISECity`, `fSEElev`, `nSEHS`, `nSECS`, `nSECSJSDay`, `nSEDegDayh`, `nSEDegDayc`, `fSETAmbHS`, `fSETambCS`, `fSEHDD65`, `fSECDH74`, `sCLIMZONE`, `sRateNo`, `fASHRAEWSF`, `fAveWindSpd`, `fAveAmbAirT`) VALUES
      ( sim_id, NEW.LBLDGRUNNO, NEW.SZSELABEL, NEW.ISECITY, NEW.FSEELEV, NEW.NSEHS, NEW.NSECS, NEW.NSECSJSDAY, NEW.NSEDEGDAYH, NEW.NSEDEGDAYC, NEW.FSETAMBHS, NEW.FSETAMBCS, NEW.FSEHDD65, NEW.FSECDH74, NEW.SCLIMZONE, NEW.SRATENO, NEW.fASHRAEWSF, NEW.fAveWindSpd, NEW.fAveAmbAirT );


    UPDATE axis.remrate_data_datatracker SET
      `status`=1, `last_update`=NOW() WHERE
      `lBldgRunNo`=NEW.lBldgRunNo AND `simulation_id`=sim_id AND `status`=0;
    UPDATE axis.remrate_data_building SET
      `sync_status`=1, `last_update`=NOW() WHERE
      `lBldgRunNo`=NEW.LBLDGRUNNO AND `simulation_id`=sim_id;


    -- Done doing stuff.. --

    END $$

DELIMITER ;
