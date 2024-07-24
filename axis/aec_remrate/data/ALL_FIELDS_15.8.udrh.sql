# This is very similar to an export from REM/Rate®  to use it simply type the following
# mysql -u axis_test -p  remrate < axis/aec_remrate/data/All_FIELDS_15.8.udrh.sql

SET NAMES latin1;
SET character_set_results = NULL;
SET SQL_AUTO_IS_NULL = 0;

SET @RATING_NUMBER = CONCAT('15.7 UDHR: ', DATE_FORMAT(NOW(), '%m/%d/%Y %H:%i'));
SET @SBRDATE = DATE_FORMAT(NOW(), '%m/%d/%Y %H:%i:%s');

select database();
select database();
SELECT @@tx_isolation;
SET @@sql_select_limit = DEFAULT;
SELECT @BLDG_RUN := IFNULL((max(lBldgRunNo) + 1), 1)
FROM BuildRun;
Select Count(*) as LCOUNT
FROM BuildRun
WHERE sBRRateNo = @RATING_NUMBER;

INSERT INTO BuildRun (lBldgRunNo, sBRDate, sBRProgVer, sBRRateNo, sBRFlag, lBRExpTpe, nInstance,
                      sBRProgFlvr, sBRUDRName, sBRUDRChk)
VALUES (@BLDG_RUN, @SBRDATE, N'15.8', @RATING_NUMBER, N'', 4, 5, N'Rate',
        N'WA Perf Path Central - Medium.udr', N'EA2507BC');
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'ek elec*', 4, 1);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 6, 15.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 600.000000, 0.073000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1400.000000, 0.063000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.055000);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 7, 12, 0.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 500000.000000, 0.070000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.060000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'ek wood*', 6, 5);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 11.110000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 13.330000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'ek kero*', 5, 2);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 2.220000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.900000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'Default Oil Provider', 3, 2);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 0.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.900000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'Default Propane Provider', 2, 2);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 9, 3, 4.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.900000);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 4, 8, 4.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.700000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'Default Gas Provider', 1, 4);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 5.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.500000);
SELECT @LMAX_Building := IFNULL((max(lBldgNo) + 1), 1)
FROM Building;
INSERT INTO Building (lBldgRunNo, lBldgNo, sBUBldgNam, sBURateNo, nBUBlgType, fCeilAtRo, fCeilAtAr,
                      fCeilCaRo, fCeilCaAr, fAGWCORo, fAGWCOAr, fAGWBORo, fAGWBOAr, fJoiCORo,
                      fJoiCOAr, fJoiBORo, fJoiBOAr, fFndCORo, fFndCOAr, fFndBORo, fFndBOAr,
                      fFrFCARo, fFrFCAAr, fWinCORo, fWinCOAr, fSkyCORo, fSkyCOAr, fDorCORo,
                      fDorCOAr, fAMThDry, sNotes, fWinWall, fWinFloor, sCeilATDom, sCeilSADOM,
                      sCeilCADOM, sAGWDOM, sFNDWDOM, sSLABDOM, sFRFDOM, sWINDOM, sDUCTDOM, sHTGDOM,
                      sCLGDOM, sDHWDOM)
VALUES (@BLDG_RUN, @LMAX_Building, N'ALL_FIELDS_SET_15.8.blg', @RATING_NUMBER, 2, 20.976839,
        2135.000000, 28.870138, 222.000000, 10.344359, 1116.300049, 0.000000, 0.000000, 11.608522,
        128.300003, 0.000000, 0.000000, 20.722126, 1136.010010, 0.000000, 0.000000, 15.727734,
        966.000000, 2.040816, 21.000000, 2.176664, 86.000000, 0.000000, 0.000000, 0.500000,
        N'building notes;notes line 2', 0.027524, 0.015500, N'R-50.0', N'NA', N'R-35.0', N'R-11.0',
        N'R-34.3', N'R-0.0 Edge, R-0.0 Under', N'R*-19.9(assembly)', N'U-Value: 0.490, SHGC: 0.580',
        N'758.06 CFM25.', N'Heating::  Fuel-fired air distribution, Natural gas, 80.0 AFUE.',
        N'Cooling::  Air conditioner, Electric, 10.0 SEER.',
        N'Water Heating::  Conventional, Natural gas, 0.56 EF, 40.0 Gal.');
INSERT INTO ProjInfo (lBldgRunNo, lBldgNo, sPIPOwner, sPIStreet, sPICity, sPIState, sPIZip,
                      sPIPhone, SPIBuilder, sPIModel, sPIBldrDev, sPIBldrPho, sPIRatOrg, sPIRatPhon,
                      sPIRatName, sPIRaterNo, sPIRatDate, sPIRatngNo, sPIRatType, sPIRatReas,
                      sPIBldrStr, sPIBldrCty, sPIBlgName, sPIRatEMal, sPIRatStr, sPIRatCity,
                      sPIRatSt, sPIRatZip, sPIRatWeb, sPIBldrEml, sPIPRVDRID, sPIREGID, SPISAMSETID,
                      sPIBldrPrmt, sPIVer1Name, sPIVer1ID, sPIVer2Name, sPIVer2ID, sPIVer3Name,
                      sPIVer3ID, sPIVer4Name, sPIVer4ID, sPIRegDate, sPIPRMTDate)
VALUES (@BLDG_RUN, @LMAX_Building, N'I.M. Smith', N'2342 Maybee Ave.', N'Denver', N'CO', N'80333',
        N'303 444 4444', N'WeeBeeGood Builders', N'The Jubilee', N'Rocky View', N'303 111 2222',
        N'L.A. Raters', N'303 222 1111', N'H.I. Scorer', N'303 333 2222', N'1/9/18', @RATING_NUMBER,
        N'Based on plans', N'New home', N'bldr street 1', N'bldr street 1', N'the bldg name',
        N'a@laraters.com', N'rater street 1', N'rater city', N'AK', N'rater zip',
        N'www.laraters.com', N'bldr email', N'____-___', N'', N'0000', N'12345', N'Rater Name 1',
        N'RaterID1', N'Rater Name 2', N'RaterID2', N'Rater Name 3', N'RaterID3', N'Rater Name 4',
        N'RaterID4', N'', N'06/26/2019');
INSERT INTO BldgInfo (lBldgRunNo, lBldgNo, fBIVolume, fBIACond, nBIHType, nBILType, nBIStories,
                      nBIFType, nBIBeds, nBIUnits, sBIRateNo, nBICType, nBIYearBlt, nBIThBndry,
                      nBIStoryWCB, nBIInfltVol)
VALUES (@BLDG_RUN, @LMAX_Building, 16000.000000, 2000.000000, 1, 0, 1, 6, 3, 1, @RATING_NUMBER, 1,
        2008, 3, 1, 1);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'ek R-19 Draped, Full*', 14, 5, 6.800000, 4.400000, 5.500000,
        6.600000, 3, 4, 19.100000, 1.100000, 2.200000, 3.300000, 1, 2, N'qwer', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Cond Basement', 128.300003, 8.700000, 7.600000, 1.100000, 201,
        @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'Mobile Home Skirt', 18, 6, 0.100000, 0.000000, 0.000000,
        0.000000, 1, 4, 8.000000, 0.000000, 0.000000, 0.000000, 1, 2, N'', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'fwall 2', 4.000000, 7.700000, 7.700000, 0.000000, 202,
        @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'R-5 Ext, 2ft deep', 11, 0, 8.000000, 5.000000, 0.000000,
        2.000000, 1, 4, 0.000000, 0.000000, 0.000000, 0.000000, 1, 1, N'', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'fwall 3', 3.000000, 6.000000, 2.000000, 4.000000, 213,
        @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_SlabType := IFNULL((max(lSTSTNo) + 1), 1)
FROM SlabType;
INSERT INTO SlabType (lBldgRunNo, lSTSTNo, sSTType, fSTPIns, fSTUIns, fSTFUWid, nSTRadiant,
                      fSTPInsDep, sSTNote, nSTInsGrde, nSTFlrCvr)
VALUES (@BLDG_RUN, @LMAX_SlabType, N'Uninsulated', 0.000000, 0.000000, 0.000000, 2, 0.000000, N'',
        1, 1);
INSERT INTO Slab (lBldgRunNo, lBldgNo, szSFName, fSFArea, fSFDep, fSFPer, fSFExPer, fSFOnPer,
                  lSFSlabTNo, sSFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Heated Basement', 1000.000000, 7.000000, 128.000000,
        128.000000, 0.000000, @LMAX_SlabType, @RATING_NUMBER);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'ek R-38 Blown, Attic*', 0, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'', N'', N'', 0.055933);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 12.534999, 0.610000, 0.450000, 4.375000,
        6.000000, 0.110000, 0.220000, 0.330000, 0.440000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.840000, 20.670000, 0.610000, 0.450000, 13.000000,
        6.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 7.670000, 0.610000, 0.450000, 0.000000,
        6.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 3.500000, 24.000000, 6.000000, 13.000000,
        3.500000, 2, @LMAX_CompType, 0, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 1, 0.110000, 1, N'asf', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'pathlayer', 888.000000, 2, 2, 2, @LMAX_CeilType, 0.055933,
        @RATING_NUMBER, 2, 2, 888.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-50 Blown, Attic', 1, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'', N'', N'', 0.020105);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 43.045002, 0.610000, 0.450000, 4.375000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.840000, 51.669998, 0.610000, 0.450000, 13.000000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 38.670002, 0.610000, 0.450000, 0.000000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 3.500000, 24.000000, 37.000000, 13.000000,
        3.500000, 2, @LMAX_CompType, 1, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 0, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'asdf', 1000.000000, 2, 2, 2, @LMAX_CeilType, 0.020105,
        @RATING_NUMBER, 2, 2, 1000.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-35, Vaulted', 1, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'Plywood', N'Shingles', N'', 0.034638);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 19.434999, 0.610000, 0.450000, 11.875000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.840000, 37.559998, 0.610000, 0.450000, 30.000000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 7.560000, 0.610000, 0.450000, 0.000000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 9.500000, 24.000000, 5.000000, 30.000000,
        9.500000, 1, @LMAX_CompType, 1, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 0, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'qf vault', 222.000000, 1, 2, 2, @LMAX_CeilType, 0.034638,
        @RATING_NUMBER, 2, 2, 222.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Mobile Home Ceiling', 1, N'Gyp board', N'Framing',
        N'Insulation', N'', N'', N'', 0.103559);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity 1', 0.793324, 13.782499, 0.610000, 0.562500, 0.000000,
        12.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity 2', 0.046676, 12.727953, 0.610000, 0.562500, 0.000000,
        10.945454, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame 1', 0.103888, 7.657500, 0.610000, 0.562500, 4.375000,
        1.500000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame 2', 0.006112, 8.557500, 0.610000, 0.562500, 4.375000,
        2.400000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade 1', 0.047222, 1.782500, 0.610000, 0.562500, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade 2', 0.002778, 1.782500, 0.610000, 0.562500, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.625000, 1.500000, 3.500000, 24.000000, 0.000000, 0.000000,
        3.500000, 2, @LMAX_CompType, 1, 1, 4.000000, 12.000000, 16.500000, 4.000000, 24.000000,
        4.000000, 1.000000, 2, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'qwer', 333.000000, 2, 1, 2, @LMAX_CeilType, 0.103559,
        @RATING_NUMBER, 2, 2, 333.000000);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-110*', 1, N'Gyp board', N'Air Gap/Frm', N'Cavity ins/Frm',
        N'Continuous ins', N'Ext Finish', N'', 0.104441);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.720000, 13.240000, 0.680000, 0.450000, 0.000000,
        11.000000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.230000, 6.615000, 0.680000, 0.450000, 0.000000,
        4.375000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.270000, 0.680000, 0.450000, 0.000000,
        1.030000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO WallType (lBldgRunNo, lWTWTNo, fWTStudWdt, fWTStudDpt, fWTStudSpg, fWTGypThk,
                      fWTContIns, fWTCvtyIns, fWTCInsThk, fWTBlckIns, nWTCntnTyp, lWTCompNo,
                      bWTQFValid, fWTFF, bWTDFLTFF, sWTNote, nWTInsGrde)
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 3.500000, 16.000000, 0.500000, 0.000000, 11.000000,
        3.500000, 0.000000, 1, @LMAX_CompType, 1, 0.230000, 1, N'qwer', 3);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Exterior Wall', 1026.300049, 201, 1, 0.104441, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-150*', 1, N'Gyp board', N'Air Gap/Frm', N'Cavity ins/Frm',
        N'Continuous ins', N'Ext Finish', N'', 0.091823);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.720000, 17.240000, 0.680000, 0.450000, 0.000000,
        15.000000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.230000, 6.615000, 0.680000, 0.450000, 0.000000,
        4.375000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.270000, 0.680000, 0.450000, 0.000000,
        1.030000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO WallType (lBldgRunNo, lWTWTNo, fWTStudWdt, fWTStudDpt, fWTStudSpg, fWTGypThk,
                      fWTContIns, fWTCvtyIns, fWTCInsThk, fWTBlckIns, nWTCntnTyp, lWTCompNo,
                      bWTQFValid, fWTFF, bWTDFLTFF, sWTNote, nWTInsGrde)
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 3.500000, 16.000000, 0.500000, 0.000000, 15.000000,
        3.500000, 0.000000, 1, @LMAX_CompType, 1, 0.230000, 1, N'BigWall', 3);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Common Wall', 513.200012, 213, 1, 0.091823, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'SIP 12-3/8"', 0, N'Gyp board', N'Air Gap/Frm',
        N'Continuous ins', N'Ext Finish', N'', N'', 0.017709);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'SIP', 1.000000, 56.469997, 0.680000, 0.450000, 1.030000,
        53.200001, 0.940000, 0.000000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO WallType (lBldgRunNo, lWTWTNo, fWTStudWdt, fWTStudDpt, fWTStudSpg, fWTGypThk,
                      fWTContIns, fWTCvtyIns, fWTCInsThk, fWTBlckIns, nWTCntnTyp, lWTCompNo,
                      bWTQFValid, fWTFF, bWTDFLTFF, sWTNote, nWTInsGrde)
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 3.500000, 16.000000, 0.500000, 16.500000, 0.000000,
        0.000000, 0.000000, 1, @LMAX_CompType, 0, 0.230000, 1, N'', 1);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'pathlayer', 100.000000, 201, 2, 0.017709, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-300*', 1, N'Floor covering', N'Subfloor', N'Cavity ins',
        N'Continuous ins', N'Framing', N'', 0.047294);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.820000, 33.425003, 0.920000, 1.230000, 0.820000,
        30.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.130000, 15.925000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 12.500000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.425000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO FlrType (lBldgRunNo, lFTFTNo, fFTJstWdt, fFTJstHgt, fFTJstSpg, fFTContIns, fFTCvtyIns,
                     fFTCInsThk, nFTCovType, nFTTCTNo, bFTQFValid, NFTQFTYPE, FFTFLRWID, FFTOUTWID,
                     FFTBATTHK, FFTBATRVL, FFTBLKTHK, FFTBLKRVL, NFTCNTINS, NFTOUTINS, FFTFF,
                     BFTDFLTFF, SFTNOTE, nFTInsGrde)
VALUES (@BLDG_RUN, @LMAX_FlrType, 1.500000, 11.500000, 16.000000, 0.000000, 30.000000, 10.000000, 1,
        @LMAX_CompType, 1, 0, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0,
        0.130000, 1, N'', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ff1', 300.000000, 201, 0.047294, @LMAX_FlrType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Mobile Home Floor', 1, N'Floor covering', N'Particle board',
        N'Batt insulation', N'Blanket insulation', N'Framing', N'', 0.112370);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity, Outrigger', 0.415208, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame, Outrigger', 0.059792, 7.195000, 0.920000, 0.000000,
        0.820000, 0.000000, 0.000000, 5.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity, Center', 0.415208, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame, Center', 0.059792, 7.195000, 0.920000, 0.000000,
        0.820000, 0.000000, 0.000000, 5.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade, Outrigger', 0.025000, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade, Center', 0.025000, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO FlrType (lBldgRunNo, lFTFTNo, fFTJstWdt, fFTJstHgt, fFTJstSpg, fFTContIns, fFTCvtyIns,
                     fFTCInsThk, nFTCovType, nFTTCTNo, bFTQFValid, NFTQFTYPE, FFTFLRWID, FFTOUTWID,
                     FFTBATTHK, FFTBATRVL, FFTBLKTHK, FFTBLKRVL, NFTCNTINS, NFTOUTINS, FFTFF,
                     BFTDFLTFF, SFTNOTE, nFTInsGrde)
VALUES (@BLDG_RUN, @LMAX_FlrType, 2.000000, 6.000000, 24.000000, 0.000000, 0.000000, 0.000000, 0,
        @LMAX_CompType, 1, 2, 12.000000, 6.000000, 4.000000, 7.000000, 0.000000, 0.000000, 1, 1,
        0.119583, 1, N'', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ff mh', 222.000000, 202, 0.112370, @LMAX_FlrType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-25 pl*', 0, N'Floor covering', N'Subfloor', N'Cavity ins',
        N'Continuous ins', N'Framing', N'', 0.050193);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.820000, 28.890100, 0.920100, 1.230000, 0.820000,
        25.000000, 0.000000, 0.000000, 0.000000, 0.920000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.130000, 14.515000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 10.625000, 0.000000, 0.920000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.890000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.920000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO FlrType (lBldgRunNo, lFTFTNo, fFTJstWdt, fFTJstHgt, fFTJstSpg, fFTContIns, fFTCvtyIns,
                     fFTCInsThk, nFTCovType, nFTTCTNo, bFTQFValid, NFTQFTYPE, FFTFLRWID, FFTOUTWID,
                     FFTBATTHK, FFTBATRVL, FFTBLKTHK, FFTBLKRVL, NFTCNTINS, NFTOUTINS, FFTFF,
                     BFTDFLTFF, SFTNOTE, nFTInsGrde)
VALUES (@BLDG_RUN, @LMAX_FlrType, 1.500000, 8.500000, 16.000000, 0.000000, 25.000000, 8.500000, 1,
        @LMAX_CompType, 0, 1, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0,
        0.130000, 1, N'', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'asdf', 444.000000, 203, 0.050193, @LMAX_FlrType,
        @RATING_NUMBER);
INSERT INTO Joist (lBldgRunNo, lBldgNo, szRJName, fRJArea, nRJLoc, fRJCoInsul, fRJFrInsul,
                   fRJSpacing, fRJUo, fRJInsulTh, sRJRateNo, nRJInsGrde)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rim, Cond', 128.300003, 201, 0.000000, 11.000000, 16.000000,
        0.086144, 3.500000, @RATING_NUMBER, 3);
SELECT @LMAX_DoorType := IFNULL((max(lDTDTNo) + 1), 1)
FROM DoorType;
INSERT INTO DoorType (lBldgRunNo, lDTDTNo, sDTType, nDTType, fDTRValue, sDTNote)
VALUES (@BLDG_RUN, @LMAX_DoorType, N'1-3/4 Wd solid core', 2, 2.100000, N'');
INSERT INTO Door (lBldgRunNo, lBldgNo, szDOName, fNOArea, nDOWallNum, lDODoorTNo, fDOUo, sDORateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Ext Doors', 40.000000, 2, @LMAX_DoorType, 0.329497,
        @RATING_NUMBER);
SELECT @LMAX_DoorType := IFNULL((max(lDTDTNo) + 1), 1)
FROM DoorType;
INSERT INTO DoorType (lBldgRunNo, lDTDTNo, sDTType, nDTType, fDTRValue, sDTNote)
VALUES (@BLDG_RUN, @LMAX_DoorType, N'Steel-ureth fm strm*', 1, 1.700000, N'');
INSERT INTO Door (lBldgRunNo, lBldgNo, szDOName, fNOArea, nDOWallNum, lDODoorTNo, fDOUo, sDORateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'door2', 0.000000, 6, @LMAX_DoorType, 0.000000, @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Wood', 0.580000, 0.490000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'South Wall', 10.000000, 1, 0.850000, 0.700000, 1, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Wood', 0.580000, 0.490000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'North Wall', 5.000000, 5, 0.850000, 0.250000, 2, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Wood', 0.580000, 0.490000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'East Wall', 11.000000, 3, 0.850000, 0.700000, 5, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Vinyl', 0.570000, 0.460000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'wall4', 5.000000, 7, 0.880000, 0.290000, 6, 0, @LMAX_WndwType,
        @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Dbl/LoE/Argon - Wood', 0.450000, 0.360000, N'');
INSERT INTO Skylight (lBldgRunNo, lBldgNo, szSKName, fSKGlzArea, nSKOr, fSKPitch, fSKSumShad,
                      fSKWtrShad, nSKSurfNum, lSKWinTNo, sSKRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sklite', 77.000000, 8, 2.000000, 0.700000, 1.000000, 2,
        @LMAX_WndwType, @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Single - Metal', 0.800000, 1.310000, N'');
INSERT INTO Skylight (lBldgRunNo, lBldgNo, szSKName, fSKGlzArea, nSKOr, fSKPitch, fSKSumShad,
                      fSKWtrShad, nSKSurfNum, lSKWinTNo, sSKRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sklite2', 9.000000, 2, 2.000000, 0.700000, 1.000000, 4,
        @LMAX_WndwType, @RATING_NUMBER);
SELECT @LMAX_Equip := IFNULL((max(lEIEINo) + 1), 1)
FROM Equip;
INSERT INTO Equip (lEIEINo, lBldgRunNo, lBldgNo, fEIHSetPnt, fEICSetPnt, nEISBThrm, nEISUThrm,
                   nEIVentTyp, nEISBSch, fEISBTemp, nEIDuctLoc, nEIDuctLo2, nEIDuctLo3, fEIDuctIns,
                   fEIDuctIn2, fEIDuctIn3, fEIDuctSup, fEIDuctSu2, fEIDuctSu3, fEIDuctRet,
                   fEIDuctRe2, fEIDuctRe3, nEIDuctLk, nEIDTUNITS, fEIDTLKAGE, nEIDTQUAL, sEIRateNo,
                   nEIHTGCAPWT, nEICLGCAPWT, nEIDHWCAPWT)
VALUES (@LMAX_Equip, @BLDG_RUN, @LMAX_Building, 68.000000, 78.000000, 1, 1, 1, 0, 66.000000, 5, 0,
        0, 0.000000, 0.000000, 0.000000, 100.000000, 0.000000, 0.000000, 100.000000, 0.000000,
        0.000000, 2, 11, 0.000000, 1, @RATING_NUMBER, 1, 1, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_HtgType := IFNULL((max(lHETHETNo) + 1), 1)
FROM HtgType;
INSERT INTO HtgType (lBldgRunNo, lHETHETNo, sHETType, nHETSystTp, nHETFuelTp, fHETRatCap, fHETEff,
                     nHETEffUTp, nHETDSHtr, nHETFnCtrl, nHETFnDef, fHETFnHSpd, fHETFnLSpd, sHETNote,
                     fHETAuxElc, nHETAuxETp, nHETAuxDef, fHETFanPwr, fHETPmpEng, nHETPmpTyp,
                     fHETRCap17)
VALUES (@BLDG_RUN, @LMAX_HtgType, N'80AFUE Gas Furn 48k', 1, 1, 48.000000, 80.000000, 1, 0, 1, 1,
        800.000000, 0.000000, N'', 611.392029, 1, 1, 0.000000, 0.000000, 1, 0.000000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, @LMAX_HtgType, -1, -1, -1, -1, -1, NULL, 1,
        100.000000, 1, 30.658192, 0.000000, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_ClgType := IFNULL((max(lCETCETNo) + 1), 1)
FROM ClgType;
INSERT INTO ClgType (lBldgRunNo, lCETCETNo, sCETType, nCETSystTp, nCETFuelTp, fCETRatCap, fCETEff,
                     fCETSHF, nCETEffUTp, nCETDSHtr, nCETFnCtrl, nCETFnDef, fCETFnHSpd, fCETFnLSpd,
                     sCETNote, fCETFanPwr, fCETPmpEng, nCETPmpTyp, nCETFanDef)
VALUES (@BLDG_RUN, @LMAX_ClgType, N'10SEER A/C 3 ton', 1, 4, 36.000000, 10.000000, 0.700000, 1, 0,
        1, 0, 825.000000, 0.000000, N'', 0.000000, 0.000000, 1, 0);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, @LMAX_ClgType, -1, -1, NULL, 2,
        100.000000, 5, 0.000000, 42.857143, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_DhwType := IFNULL((max(lDETDETNo) + 1), 1)
FROM DhwType;
INSERT INTO DhwType (lBldgRunNo, lDETDETNo, sDETType, nDETSystTp, nDETFuelTp, fDETTnkVol,
                     fDETTnkIns, fDETEnergy, fDETRecEff, sDETNote)
VALUES (@BLDG_RUN, @LMAX_DhwType, N'40 gal. 0.56EF Gas', 1, 1, 40.000000, 0.000000, 0.560000,
        0.760000, N'');
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, @LMAX_DhwType, -1, NULL, 3,
        100.000000, 1, 0.000000, 0.000000, 100.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_GshpType := IFNULL((max(lGSTGSTNo) + 1), 1)
FROM GshpType;
INSERT INTO GshpType (lBldgRunNo, lGSTGSTNo, sGSTType, nGSTType, nGSTFuel, fGSTHCOP70, fGSTHCOP50,
                      fGSTCEER70, fGSTCEER50, fGSTHCap70, fGSTHCap50, fGSTCCap70, fGSTCCap50,
                      fGSTHCOP32, fGSTHCap32, fGSTCEER77, fGSTCCap77, fGSTSHF, nGSTFanDef,
                      nGSTDSHtr, sGSTNote, fGSTBKUPCP, fGSTFanPwr, fGSTPmpEng, nGSTPmpEnT,
                      nGSTDbType)
VALUES (@BLDG_RUN, @LMAX_GshpType, N'GSHP 1 Ton', 1, 4, 3.830000, 3.445800, 15.394000, 17.948400,
        20.306000, 15.814600, 12.129300, 13.279700, 3.100000, 11.500000, 14.500000, 12.000000,
        0.700000, 1, 0, N'', 0.000000, 80.000000, 0.000000, 1, 1);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, @LMAX_GshpType, -1, -1, -1, -1, NULL, 5,
        100.000000, 1, 7.345192, 14.285714, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_AshpType := IFNULL((max(lASTASTNo) + 1), 1)
FROM AshpType;
INSERT INTO AshpType (lBldgRunNo, lASTASTNo, sASTType, nASTFuel, fASTHCap47, FASTHEFF, NASTHEFFU,
                      fASTCCAP, FASTCEFF, NASTCEFFU, fASTSHF, nASTDSHtr, sASTNote, fASTBKUPCP,
                      nASTFnCtrl, nASTFnDef, fASTFnHSpd, fASTFnLSpd, fASTHCap17)
VALUES (@BLDG_RUN, @LMAX_AshpType, N'18k 10seer 6.8hspf', 4, 18.000000, 6.800000, 3, 18.000000,
        10.000000, 1, 0.700000, 0, N'', 5.000000, 1, 1, 0.000000, 0.000000, 10.980000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, -1, @LMAX_AshpType, NULL, 4,
        100.000000, 1, 22.396448, 21.428572, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_DfhpType := IFNULL((max(lDFTDFTNo) + 1), 1)
FROM DfhpType;
INSERT INTO DfhpType (lBldgRunNo, lDFTDFTNo, sDFTType, nDFTFuel, fDFTHHSPF, fDFTHCap47, nDFTBFuel,
                      nDFTBEffU, fDFTBSEff, fDFTBCap, fDFTCSEER, fDFTCCap, fDFTCSHF, nDFTDSHtr,
                      fDFTSwitch, nDFTFnCtrl, nDFTFnDef, fDFTFnHSpd, fDFTFnLSpd, sDFTNote)
VALUES (@BLDG_RUN, @LMAX_DfhpType, N'DFHP 1.5 Ton', 4, 7.000000, 13.400000, 1, 1, 78.000000,
        30.000000, 10.000000, 18.000000, 0.700000, 0, 33.000000, 1, 1, 413.000000, 0.000000, N'');
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, @LMAX_DfhpType, -1, -1, -1, NULL, 6,
        100.000000, 1, 19.161371, 21.428572, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_HtgType := IFNULL((max(lHETHETNo) + 1), 1)
FROM HtgType;
INSERT INTO HtgType (lBldgRunNo, lHETHETNo, sHETType, nHETSystTp, nHETFuelTp, fHETRatCap, fHETEff,
                     nHETEffUTp, nHETDSHtr, nHETFnCtrl, nHETFnDef, fHETFnHSpd, fHETFnLSpd, sHETNote,
                     fHETAuxElc, nHETAuxETp, nHETAuxDef, fHETFanPwr, fHETPmpEng, nHETPmpTyp,
                     fHETRCap17)
VALUES (@BLDG_RUN, @LMAX_HtgType, N'80AFUE Gas Furn 32k*', 6, 1, 32.000000, 30.000000, 1, 1, 1, 1,
        533.000000, 0.000000, N'Notes', 0.000000, 1, 0, 10.000000, 0.000000, 1, 30.000000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, @LMAX_HtgType, -1, -1, -1, -1, -1, NULL, 1,
        100.000000, 1, 20.438795, 0.000000, 0.000000, 1);
SELECT @LMAX_GshpWell := IFNULL((max(lGWellNo) + 1), 1)
FROM GshpWell;
INSERT INTO GshpWell (lBldgRunNo, sRateNo, lGWellNo, nGWType, fGWNoWells, fGWDepth, fGWLpFlow)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_GshpWell, 0, 8.000000, 100.000000, 2.000000);
SELECT @LMAX_DhwDistrib := IFNULL((max(lDhwDistNo) + 1), 1)
FROM DhwDistrib;
INSERT INTO DhwDistrib (lBldgRunNo, sRateNo, lDhwDistNo, bFixLowFlow, bDhwPipeIns, nRecircType,
                        fMaxFixDist, fSupRetDist, fPipeLenDhw, fPipeLenRec, fRecPumpPwr, bHasDwhr,
                        fDwhrEff, bDwhrPrehtC, bDwhrPrehtH, nShwrheads, nShwrToDwhr, fHwCtrlEff)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_DhwDistrib, 1, 1, 3, 89.000000, 100.000000, 89.000000,
        100.000000, 50.000000, 1, 89.199997, 1, 1, 2, 1, 0.000000);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'measured', 6, -1, 50.220001, 9.300000, 1, 2,
        0.890000, 0.356000, 0.534000, 2, 2, @RATING_NUMBER, 1, 248.000000, 0.890000, 1, 0, 1, 2, 0,
        0, 1, 0.820000, 0.850000, 1, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 100.000000, 5, 0.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 100.000000, 5, 0.000000, 2, @RATING_NUMBER);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'total', 4, 5, 101.250000, 18.750000, 1, 2,
        1.200000, 0.480000, 0.720000, 12, 2, @RATING_NUMBER, 2, 500.000000, 0.890000, 0, 0, 0, 2, 1,
        0, 1, Null, Null, 0, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 80.000000, 7, 3.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 75.000000, 7, 4.000000, 2, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 20.000000, 6, 3.100000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 25.000000, 6, 4.100000, 2, @RATING_NUMBER);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'sup ret', 0, -1, 101.250000, 18.750000, 1, 3,
        30.000000, 12.000000, 18.000000, 2, 2, @RATING_NUMBER, 1, 500.000000, 15.000000, 0, 0, 0, 3,
        1, 0, 1, Null, Null, 0, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 80.000000, 7, 3.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 75.000000, 7, 4.000000, 2, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 20.000000, 6, 3.100000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 25.000000, 6, 4.100000, 2, @RATING_NUMBER);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'std 152', 3, 1, 101.250000, 18.750000, 1, 3,
        7.170000, 5.130000, 2.040000, 2, 2, @RATING_NUMBER, 3, 500.000000, 32.299999, 2, 0, 0, 3, 0,
        0, 1, Null, Null, 0, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 80.000000, 7, 3.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 75.000000, 7, 4.000000, 2, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 20.000000, 6, 3.100000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 25.000000, 6, 4.100000, 2, @RATING_NUMBER);
INSERT INTO Infilt (lBldgRunNo, lBldgNo, lINInfilNo, nINType, fINHeatVal, fINCoolVal, nINWHInfUn,
                    lINMVType, fINMVRate, fINSREff, nINHrsDay, fINMVFan, sINRateNo, fINTREff,
                    nINVerify, nINShltrCl, nINClgVent, nINFanMotor, fINAnnual, fINTested,
                    nINGdAirXMF, nINNoMVMsrd, nINWattDflt)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 6, 7.100000, 7.100000, 3, 1, 100.000000, 8.000000, 24.000000,
        100.000000, @RATING_NUMBER, 9.000000, 2, 4, 1, 1, 7.100000, 7.000000, 0, 1, 1);
INSERT INTO LightApp (lBldgRunNo, lBldgNo, fLAOvnFuel, fLADryFuel, sLARateNo, nLAUseDef, fLARefKWh,
                      fLADishWEF, fLAFlrCent, fLAFanCFM, fLACFLCent, fLACFLExt, fLACFLGar,
                      nLARefLoc, fLADishWCap, fLADishWYr, nLAOvnInd, nLAOvnCon, nLADryLoc,
                      nLADryMoist, fLADryEF, fLADryMEF, fLADryGasEF, nLAWashLoc, fLAWashLER,
                      fLAWashCap, fLAWashElec, fLAWashGas, fLAWashGCst, fLAWashEff, fLALEDInt,
                      fLALEDExt, fLALEDGar)
VALUES (@BLDG_RUN, @LMAX_Building, 4, 4, @RATING_NUMBER, 1, 775.000000, 0.460000, 10.000000,
        70.400002, 9.800000, 4.100000, 1.700000, 1, 12.000000, 0.000000, 0, 1, 1, 0, 2.320000,
        0.331000, 2.670000, 1, 487.000000, 3.200000, 0.080300, 0.580000, 23.000000, 1, 90.199997,
        62.200001, 8.300000);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Int Ltg', 1, 1, 4, 1849.500000, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Ext Ltg', 1, 5, 4, 205.500000, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Refrigerator', 3, 1, 4, 775.000000, 4, 1.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Dishwasher', 5, 1, 4, 0.586957, 4, 247.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Dishwasher', 5, 1, 98, 7.347020, 5, 247.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Ceiling Fan', 14, 1, 4, 42.613602, 2, 168.000000, 3, 3,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Oven/Range', 7, 1, 4, 547.505005, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Dryer', 9, 1, 4, 900.007996, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Washer', 8, 1, 4, 90.000801, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Washer', 8, 1, 98, 8.248850, 5, 365.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Shower', 10, 1, 98, 46.743500, 5, 365.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Plug Loads', 2, 1, 4, 2871.169922, 4, 1.000000, 8, 1, 3);
INSERT INTO MandReq (lBldgRunNo, lBldgNo, nMRIECC04, nMRIECC06, nMRIECC09, nMRESV2TBC, nMRESV2PRD,
                     nMRESV3TEC, nMRESV3HC, nMRESV3HR, nMRESV3WM, nMRESV3AP, nMRESV3RF, nMRESV3CF,
                     nMRESV3EF, nMRESV3DW, nMRESV3NRF, nMRESV3NCF, nMRESV3NEF, nMRESV3NDW,
                     sMRRateNo, nMRIECCNY, nMRESV3SAF, fMRESV3BFA, nMRESV3NBB, nMRIECC12,
                     nMRFLORIDA, nMRESV3SLAB, nMRIECC15, sMRESQUAL4, nMRIECC18, nMRIECCMI,
                     NMRESMFWSHR, NMRESMFDRYR, NMRESMFWIN, nMRIECCNC)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 2, 3, 4,
        @RATING_NUMBER, 1, 1, 300.000000, 0, 1, 0, 1, 1, N'ENERGY STAR v1.1 MF', 0, 1, 1, 0, 1, 1);
INSERT INTO DOEChallenge (lBldgRunNo, lBldgNo, sDCBldrID, nDCFenstrtn, nDCInsul, nDCDuctLoc,
                          nDCAppl, nDCLighting, nDCFanEff, nDCAirQual, nDCSolarE, nDCSolarHW,
                          nDCAirPlus, nDCWtrSense, nDCIBHS, nDCMGMT, nDCWaiver, sDCRateNo,
                          nDCWaterEff)
VALUES (@BLDG_RUN, @LMAX_Building, N'ID156', 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1, 3, 2, 1,
        @RATING_NUMBER, 1);
INSERT INTO AddMass (lBldgRunNo, lBldgNo, szAMName, fAMArea, nAMLoc, nAMType, fAMThk, sAMRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'intmass', 66.000000, 1, 1, 7.000000, @RATING_NUMBER);
INSERT INTO ActSolar (lBldgRunNo, lBldgNo, nASSystem, nASLoop, fASColArea, nASOr, nASTilt, nASSpecs,
                      fASStgVol, sASRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 0, 0.000000, 0, 0.000000, 0, 0.000000, @RATING_NUMBER);
INSERT INTO PhotoVol (lBldgRunNo, lBldgNo, sPVName, nPVColType, fPVArea, fPVPower, fPVTilt, nPVOr,
                      fPVInvEff, sPVRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'pv1', 0, 111.199997, 88.000000, 55.000000, 2, 12.000000,
        @RATING_NUMBER);
INSERT INTO PhotoVol (lBldgRunNo, lBldgNo, sPVName, nPVColType, fPVArea, fPVPower, fPVTilt, nPVOr,
                      fPVInvEff, sPVRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'pv2', 0, 99.000000, 77.000000, 49.000000, 4, 11.100000,
        @RATING_NUMBER);
INSERT INTO SunSpace (lBldgRunNo, lBldgNo, fSSRfArea, fSSRFIns, fSSAGWArea, fSSAGWIns, fSSBGWArea,
                      fSSBGWIns, fSSArea, fSSFrmIns, fSSSlbPer, fSSSlbDep, fSSSlbThk, fSSSlbPIns,
                      fSSSlbUIns, sSSRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, 100.000000, 5.100000, 155.000000, 4.800000, 77.000000, 3.300000,
        101.000000, 7.000000, 111.000000, 3.000000, 8.000000, 5.500000, 4.400000, @RATING_NUMBER);
INSERT INTO SSMass (lBldgRunNo, lBldgNo, szSSMName, fSSMArea, nSSMType, fSSMThk, fSSMWVol,
                    sSSMRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ss intmass', 88.000000, 2, 12.000000, 0.000000,
        @RATING_NUMBER);
INSERT INTO SSCmnWal (lBldgRunNo, lBldgNo, szSSCName, fSSCArea, nSSCMTyp, fSSCMThk, fSSCIns,
                      nSSCFan, fSSCFlRate, sSSCRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sswall', 77.000000, 1, 5.000000, 4.000000, 1, 5.000000,
        @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Vinyl', 0.570000, 0.460000, N'');
INSERT INTO SSWindow (lBldgRunNo, lBldgNo, szSSWName, fSSWArea, nSSWOr, fSSWSum, fSSWWtr,
                      lSSWWdwTNo, sSSWRateNo, fSSOHDepth, fSSOHToTop, fSSOHToBtm, fSSAdjSum,
                      fSSAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'sswin1', 88.000000, 7, 0.700000, 0.850000, @LMAX_WndwType,
        @RATING_NUMBER, 2.000000, 3.000000, 4.000000, 0.700000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double/LoE - Wood', 0.460000, 0.390000, N'');
INSERT INTO SSSkLght (lBldgRunNo, lBldgNo, szSSSName, fSSSArea, nSSSOr, fSSSPitch, fSSSSum, fSSSWtr,
                      lSSSWdwTNo, sSSSRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sssky', 66.000000, 2, 3.000000, 0.700000, 1.000000,
        @LMAX_WndwType, @RATING_NUMBER);
INSERT INTO ResnetDisc (lBldgRunNo, lBldgNo, nRDQ1, nRDQ2A, nRDQ2B, nRDQ2C, nRDQ2D, nRDQ2E,
                        sRDQ2EOTHR, nRDQ3A, nRDQ3B, nRDQ3C, NRDQ4HVACI, NRDQ4HVACB, NRDQ4THMLI,
                        NRDQ4THMLB, NRDQ4AIRSI, NRDQ4AIRSB, NRDQ4WINI, NRDQ4WINB, NRDQ4APPLI,
                        NRDQ4APPLB, NRDQ4CNSTI, NRDQ4CNSTB, NRDQ4OTHRI, NRDQ4OTHRB, SRDQ4OTHR,
                        sRateNo, nRDQ5)
VALUES (@BLDG_RUN, @LMAX_Building, 1, 1, 0, 1, 1, 1, N'this is the other text', 0, 1, 0, 1, 2, 2, 3,
        3, 1, 2, 3, 3, 1, 1, 3, 3, 2, N'other specify', @RATING_NUMBER, 1);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 1, 4, 487.494995, 0.000000, 211.724884, 0.000000, 349.091492, @RATING_NUMBER,
        0.000000, 699.219849);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 2, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 3, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 1, 3017.357666, 2976.077637, 71.890625, 7324.115723, 924.485962,
        @RATING_NUMBER, -27.186556, 13362.254883);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 5, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 6, 5, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 7, 10.639091, 0.000000, 0.013116, 0.600679, 11.252886, @RATING_NUMBER,
        0.000000, 11.252886);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 8, 0.000000, 3.781754, 0.010440, 1.236865, 5.029059, @RATING_NUMBER, 0.000000,
        5.029059);
INSERT INTO EconParam (lBldgRunNo, lBldgNo, sRateNo, nFSBaseline, sFSBldgName, fEPImpCost,
                       fEPImpLife, fEPMortRat, fEPMortPer, fEPDownPay, fEPAppVal, fEPInf,
                       fEPDisRate, fEPEnInf, fEPAnalPer, nEPImpLifeD, nEPMortRatD, nEPMortPerD,
                       nEPDownPayD, nEPInfD, nEPDisRateD, nEPEnInfD, nEPAnalPerD, nEPDOECalc,
                       nEPCalcMthd)
VALUES (@BLDG_RUN, @LMAX_Building, @RATING_NUMBER, 18, N'REM UDRH/Building Baseline: None',
        500.000000, 25.000000, 5.700000, 30.000000, 10.000000, 0.000000, 2.000000, 4.000000,
        2.300000, 15.000000, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1);
INSERT INTO Results (lBldgRunNo, fHTEff, fClgEff, fHWEff, fLhROOF, fLcROOF, fLhJOIST, fLcJOIST,
                     fLhAGWALL, fLcAGWALL, fLhFNDWALL, fLcFNDWALL, fLhWNDOSK, fLcWNDOSK, fLhFFLR,
                     fLcFFLR, fLhCRAWL, fLcCRAWL, fLhSLAB, fLcSLAB, fLhINF, fLcINF, fLhMECHVNT,
                     fLcMECHVNT, fLhDUCT, fLcDUCT, fLhASOL, fLcASOL, fLhSS, fLcSS, fLhIGAIN,
                     fLcIGAIN, fLhWHF, fLcWHF, fLhDOOR, fLcDOOR, fLhTOTAL, fLcTOTAL, fTotDHW,
                     fSolSave, fHtPeak, fAcsPeak, fAclPeak, fAcTPeak, fHbuck, fAcbuck, fWbuck,
                     fhCons, fcCons, fhCost, fcCost, fWcons, fWCost, fServCost, fTotCost, fRefrCons,
                     fFrzCons, fDryCons, fOvenCons, fLaOthCons, fLiHsCons, fLiCsCons, fRefrCost,
                     fFrzCost, fDryCost, fOvenCost, fLaOthCost, fLightCost, fLATotCons, fLATotCost,
                     fPVTotCons, fPVTotCost, fShellArea, fHTGLdPHDD, fCLGLdPHDD, fHTGDdPHDD,
                     fClgDdPHDD, fHTGACH, fCLGACH, sRateNo, fEMCO2TOT, fEMSO2TOT, fEMNOXTOT,
                     fEMCO2HTG, fEMCO2CLG, fEMCO2DHW, fEMCO2LA, fEMCO2PV, fEMSO2HTG, fEMSO2CLG,
                     fEMSO2DHW, fEMSO2LA, fEMSO2PV, fEMNOXHTG, fEMNOXCLG, fEMNOXDHW, fEMNOXLA,
                     fEMNOXPV, fEMHERSCO2, fEMHERSSO2, fEMHERSNOX, fSRCEGYHTG, fSRCEGYCLG,
                     fSRCEGYDHW, fSRCEGYLA, fSRCEGYPV, fDHWNoLoss)
VALUES (@BLDG_RUN, 0.801140, 2.924843, 0.474217, 8.056259, 2.494124, 1.167890, 0.050888, 10.419005,
        2.323617, 5.041217, 0.246012, -1.357768, 11.728258, 5.882336, 0.256310, 0.000000, 0.000000,
        1.459454, -1.012856, 6.598091, 1.270727, 8.825421, 0.545544, 14.003529, 6.000143, 0.000000,
        0.000000, -0.569761, 0.736330, -12.220259, 14.165796, 0.000000, -9.096495, 0.000000,
        0.000000, 47.305416, 29.708399, 10.156643, 0.000000, 92.049232, 44.314800, 0.000000,
        44.314800, 7.628934, 20.304394, 5.175532, 59.047649, 10.157262, 450.470642, 206.237045,
        21.417706, 110.848022, 150.000000, 1423.577637, 2.645075, 0.000000, 5.269911, 1.452560,
        8.327645, 1.012100, 0.882344, 53.744579, 0.000000, 107.077919, 29.514175, 169.207214,
        38.492706, 24.996983, 507.907104, -0.092787, -1.885312, 6887.609375, 1.785337, 4.318529,
        0.003474, 0.006442, 0.257930, 0.139037, @RATING_NUMBER, 22883.583984, 8.730013, 26.371870,
        9122.621094, 3227.907959, 2618.672607, 7943.869141, -29.487032, 1.991118, 1.935028,
        0.059446, 4.762097, -0.017677, 10.899126, 3.537632, 3.261329, 8.706098, -0.032316, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 6.143121);
INSERT INTO RegionalCode (lBldgRunNo, sRateNo, fNVRebate, fNYECRHCn, fNYECRCCn, fNYECRDCN,
                          fNYECRLACn, fNYECRPVCn, fNYECRTCn, fNYECDHCn, fNYECDCCn, fNYECDDCN,
                          fNYECDLACn, fNYECDPVCn, fNYECDTCn, bNYECC, fNVECRHCn, fNVECRCCn,
                          fNVECRDCN, fNVECRLACn, fNVECRPVCn, fNVECRTCn, fNVECDHCn, fNVECDCCn,
                          fNVECDDCN, fNVECDLACn, fNVECDPVCn, fNVECDTCn, bNVECC, fNCRHCT, fNCRCCT,
                          fNCRDCT, fNCRLACT, fNCRPVCT, fNCRSVCT, fNCRTCT, fNCDHCT, fNCDCCT, fNCDDCT,
                          fNCDLACT, fNCDPVCT, fNCDSVCT, fNCDTCT, bNCMeetCT, fNCRUA, fNCDUA,
                          bNCDctPass, bNCUAPass, bNCPass, fNCHRHCT, fNCHRCCT, fNCHRDCT, fNCHRLACT,
                          fNCHRPVCT, fNCHRSVCT, fNCHRTCT, fNCHDHCT, fNCHDCCT, fNCHDDCT, fNCHDLACT,
                          fNCHDPVCT, fNCHDSVCT, fNCHDTCT, bNCHMeetCT, fNCHRUA, fNCHDUA, bNCHDctPass,
                          bNCHUAPass, bNCHPass, fNYRHCT, fNyRCCT, fNYRDCT, fNYRLACT, fNYRPVCT,
                          fNYRSVCT, fNYRTCT, fNYDHCT, fNYDCCT, fNYDDCT, fNYDLACT, fNYDPVCT,
                          fNYDSVCT, fNYDTCT, bNYMeetCT, fNYRUA, fNYDUA, bNYDctPass, bNYUAPass,
                          bNYPass)
VALUES (@BLDG_RUN, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0, 306.913208, 134.770798, 88.419525, 498.012695, -0.000000, 150.000000,
        1178.116211, 423.246979, 243.292740, 98.045738, 508.088898, -1.885987, 150.000000,
        1420.788330, 0, 300.183197, 394.475922, 0, 0, 0, 298.189423, 134.542358, 88.430824,
        481.575378, -0.000000, 150.000000, 1152.738037, 423.246979, 243.292740, 98.045738,
        508.088898, -1.885987, 150.000000, 1420.788330, 0, 299.553192, 394.475922, 0, 0, 0,
        247.697296, 115.177917, 88.193954, 502.346924, -0.000000, 150.000000, 1103.416016,
        423.246979, 243.292740, 98.045738, 508.088898, -1.885987, 150.000000, 1420.788330, 0,
        278.656494, 394.475922, 0, 0, 0);
INSERT INTO HERSCode (lBldgRunNo, sRateNo, fHERSScor, fHERSCost, fHERSStars, fHERSRHCn, fHERSRCCn,
                      fHERSRDCN, fHERSRLACn, fHERSRPVCn, fHERSRTCn, fHERSDHCn, fHERSDCCn, fHERSDDCN,
                      fHERSDLACn, fHERSDPVCn, fHERSDTCn, FNYHERS, bTaxCredit, FHERS130)
VALUES (@BLDG_RUN, @RATING_NUMBER, -999.000000, 1360.895996, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0, 0.000000);
INSERT INTO ENERGYSTAR (lBldgRunNo, sRateNo, BESTARV2, BESTARV25, FV25HERSPV, FV25HERS, FV25HERSSA,
                        FV25SZADJF, BESTARV3, FV3HERSPV, FV3HERS, FV3HERSSA, FV3SZADJF, BESTARV3HI,
                        FV3HIHERSPV, FV3HIHERS, FV3HIHERSSA, FV3HISZADJF, BESTARV31, FV31HERSPV,
                        FV31HERS, FV31HERSSA, FV31SZADJF, BDOEPROGRAM, FDOEHERS, FDOEHERSSA,
                        BESTARV32W, FV32WHERSPV, FV32WHERS, FV32WHERSSA, FV32WSZADJF, BESTARV10MF,
                        FV10MFHERSPV, FV10MFHERS, BESTARV11MF, FV11MFHERSPV, FV11MFHERS,
                        BESTARV12MF, FV12MFHERSPV, FV12MFHERS)
VALUES (@BLDG_RUN, @RATING_NUMBER, 0, 0, -999.000000, -999.000000, -999.000000, 1.000000, Null,
        Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, 0,
        -999.000000, -999.000000, Null, Null, Null, Null, Null, Null, Null, Null, 0, -999.000000,
        -999.000000, Null, Null, Null);
INSERT INTO IECC (lBldgRunNo, sRateNo, f98IERHCn, f98IERCCn, f98IERDCN, f98IERLACn, f98IERPVCn,
                  f98IERTCn, f98IEDHCn, f98IEDCCn, f98IEDDCN, f98IEDLACn, f98IEDPVCn, f98IEDTCn,
                  b98IECC, f98IECCRUo, f98IECCDUo, b98IECCDuP, b98IECCuoP, f00IERHCn, f00IERCCn,
                  f00IERDCN, f00IERLACn, f00IERPVCn, f00IERTCn, f00IEDHCn, f00IEDCCn, f00IEDDCN,
                  f00IEDLACn, f00IEDPVCn, f00IEDTCn, b00IECC, f00IECCRUo, f00IECCDUo, b00IECCDuP,
                  b00IECCuoP, f01IERHCn, f01IERCCn, f01IERDCN, f01IERLACn, f01IERPVCn, f01IERTCn,
                  f01IEDHCn, f01IEDCCn, f01IEDDCN, f01IEDLACn, f01IEDPVCn, f01IEDTCn, b01IECC,
                  f01IECCRUo, f01IECCDUo, b01IECCDuP, b01IECCuoP, f03IERHCn, f03IERCCn, f03IERDCN,
                  f03IERLACn, f03IERPVCn, f03IERTCn, f03IEDHCn, f03IEDCCn, f03IEDDCN, f03IEDLACn,
                  f03IEDPVCn, f03IEDTCn, b03IECC, f03IECCRUo, f03IECCDUo, b03IECCDuP, b03IECCuoP,
                  f04IERHCT, f04IERCCT, f04IERDCT, f04IERLACT, f04IERPVCT, f04IERSVCT, f04IERTCT,
                  f04IEDHCT, f04IEDCCT, f04IEDDCT, f04IEDLACT, f04IEDPVCT, f04IEDSVCT, f04IEDTCT,
                  b04IECC, f04IECCRUA, f04IECCDUA, b04IECCDuP, b04IECCuAP, bPass04IECC, f06IERHCT,
                  f06IERCCT, f06IERDCT, f06IERLACT, f06IERPVCT, f06IERSVCT, f06IERTCT, f06IEDHCT,
                  f06IEDCCT, f06IEDDCT, f06IEDLACT, f06IEDPVCT, f06IEDSVCT, f06IEDTCT, b06IECC,
                  f06IECCRUA, f06IECCDUA, b06IECCDuP, b06IECCuAP, bPass06IECC, f09IERHCT, f09IERCCT,
                  f09IERDCT, f09IERLACT, f09IERPVCT, f09IERSVCT, f09IERTCT, f09IEDHCT, f09IEDCCT,
                  f09IEDDCT, f09IEDLACT, f09IEDPVCT, f09IEDSVCT, f09IEDTCT, b09IECC, f09IECCRUA,
                  f09IECCDUA, b09IECCDuP, b09IECCuAP, bPass09IECC, f12IERHCT, f12IERCCT, f12IERDCT,
                  f12IERLACT, f12IERPVCT, f12IERSVCT, f12IERTCT, f12IEDHCT, f12IEDCCT, f12IEDDCT,
                  f12IEDLACT, f12IEDPVCT, f12IEDSVCT, f12IEDTCT, b12IECC, f12IECCRUA, f12IECCDUA,
                  b12IECCDuP, b12IECCuAP, bPass12IECC, f15IERHCT, f15IERCCT, f15IERDCT, f15IERLACT,
                  f15IERPVCT, f15IERSVCT, f15IERTCT, f15IEDHCT, f15IEDCCT, f15IEDDCT, f15IEDLACT,
                  f15IEDPVCT, f15IEDSVCT, f15IEDTCT, b15IECC, f15IECCRUA, f15IECCDUA, b15IECCDuP,
                  b15IECCuAP, bPass15IECC, f18IERHCT, f18IERCCT, f18IERDCT, f18IERLACT, f18IERPVCT,
                  f18IERSVCT, f18IERTCT, f18IEDHCT, f18IEDCCT, f18IEDDCT, f18IEDLACT, f18IEDPVCT,
                  f18IEDSVCT, f18IEDTCT, b18IECC, f18IECCRUA, f18IECCDUA, b18IECCDuP, b18IECCuAP,
                  bPass18IECC)
VALUES (@BLDG_RUN, @RATING_NUMBER, 21.513630, 12.273309, 29.560535, 22.007195, -0.000000, 85.354668,
        57.755569, 9.704201, 28.048618, 24.996983, -0.092787, 120.412590, 0, 0.078729, 0.067889, 0,
        0, 21.513630, 12.273309, 29.560535, 22.007195, -0.000000, 85.354668, 57.755569, 9.704201,
        28.048618, 24.996983, -0.092787, 120.412590, 0, 0.078729, 0.067889, 0, 0, 21.513630,
        12.273309, 29.560535, 22.007195, -0.000000, 85.354668, 57.755569, 9.704201, 28.048618,
        24.996983, -0.092787, 120.412590, 0, 0.078729, 0.067889, 0, 0, 21.513630, 12.273309,
        29.560535, 22.007195, -0.000000, 85.354668, 57.755569, 9.704201, 28.048618, 24.996983,
        -0.092787, 120.412590, 0, 0.078729, 0.067889, 0, 0, 244.167938, 168.142807, 89.006973,
        462.836700, -0.000000, 150.000000, 1114.154419, 379.778839, 217.348206, 98.898865,
        509.071655, -1.889635, 150.000000, 1353.208008, 0, 303.238586, 394.475922, 0, 0, 0,
        217.599716, 114.320976, 89.006973, 464.539490, -0.000000, 150.000000, 1035.467163,
        379.778839, 217.348206, 98.898865, 509.071655, -1.889635, 150.000000, 1353.208008, 0,
        303.238586, 394.475922, 0, 0, 0, 280.509979, 133.858124, 88.453003, 463.327454, -0.000000,
        150.000000, 1116.148560, 422.891113, 242.473068, 98.045471, 508.103821, -1.886042,
        150.000000, 1419.627441, 0, 299.504791, 394.475922, 0, 0, 0, 243.876190, 114.600822,
        88.200089, 502.424805, -0.000000, 150.000000, 1099.101929, 423.246979, 243.292740,
        98.045738, 508.088898, -1.885987, 150.000000, 1420.788330, 0, 274.922699, 394.475922, 0, 0,
        0, 247.697296, 115.177917, 88.193954, 502.346924, -0.000000, 150.000000, 1103.416016,
        423.246979, 243.292740, 98.045738, 508.088898, -1.885987, 150.000000, 1420.788330, 0,
        278.656494, 394.475922, 0, 0, 0, 247.381378, 115.191994, 88.194534, 496.982330, -0.000000,
        150.000000, 1097.750244, 423.246979, 243.292740, 98.045738, 508.088898, -1.885987,
        150.000000, 1420.788330, 0, 278.236511, 394.475922, 0, 0, 0);
INSERT INTO Site (lBldgRunNo, szSELabel, ISECity, fSEElev, nSEHS, nSECS, nSECSJSDay, nSEDegDayh,
                  nSEDegDayc, fSETAmbHS, fSETambCS, fSEHDD65, fSECDH74, sCLIMZONE, sRateNo,
                  fASHRAEWSF, fAveWindSpd, fAveAmbAirT)
VALUES (@BLDG_RUN, N'Fredonia, AZ', 0, 4672, 195, 170, 114, 3996.000000, 1102.000000, 45.049999,
        75.760002, 3847.000000, 23971.000000, N'5B', @RATING_NUMBER, 0.470000, 4.900000, 59.400002);

SELECT @BLDG_RUN := IFNULL((max(lBldgRunNo) + 1), 1)
FROM BuildRun;
INSERT INTO BuildRun (lBldgRunNo, sBRDate, sBRProgVer, sBRRateNo, sBRFlag, lBRExpTpe, nInstance,
                      sBRProgFlvr, sBRUDRName, sBRUDRChk)
VALUES (@BLDG_RUN, @SBRDATE, N'15.8', @RATING_NUMBER, N'', 5, 6, N'Rate',
        N'WA Perf Path Central - Medium.udr', N'EA2507BC');
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'ek elec*', 4, 1);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 6, 15.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 600.000000, 0.073000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1400.000000, 0.063000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.055000);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 7, 12, 0.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 500000.000000, 0.070000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.060000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'ek wood*', 6, 5);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 11.110000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 13.330000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'ek kero*', 5, 2);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 2.220000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.900000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'Default Oil Provider', 3, 2);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 0.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.900000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'Default Propane Provider', 2, 2);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 9, 3, 4.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.900000);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 4, 8, 4.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.700000);
SELECT @LMAX_UtilRate := IFNULL((max(lURURNo) + 1), 1)
FROM UtilRate;
INSERT INTO UtilRate (lBldgRunNo, lURURNo, sURName, nURFuelTyp, nURUnits)
VALUES (@BLDG_RUN, @LMAX_UtilRate, N'Default Gas Provider', 1, 4);
SELECT @LMAX_SeasnRat := IFNULL((max(lSRSRNo) + 1), 1)
FROM SeasnRat;
INSERT INTO SeasnRat (lBldgRunNo, lSRSRNo, lSRURNo, nSRStrtMth, nSRStopMth, fSRSvcChrg)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, @LMAX_UtilRate, 1, 12, 5.000000);
INSERT INTO Block (lBldgRunNo, lBLSRNo, fBLBlckMax, fBLRate)
VALUES (@BLDG_RUN, @LMAX_SeasnRat, 1000000.000000, 0.500000);
SELECT @LMAX_Building := IFNULL((max(lBldgNo) + 1), 1)
FROM Building;
INSERT INTO Building (lBldgRunNo, lBldgNo, sBUBldgNam, sBURateNo, nBUBlgType, fCeilAtRo, fCeilAtAr,
                      fCeilCaRo, fCeilCaAr, fAGWCORo, fAGWCOAr, fAGWBORo, fAGWBOAr, fJoiCORo,
                      fJoiCOAr, fJoiBORo, fJoiBOAr, fFndCORo, fFndCOAr, fFndBORo, fFndBOAr,
                      fFrFCARo, fFrFCAAr, fWinCORo, fWinCOAr, fSkyCORo, fSkyCOAr, fDorCORo,
                      fDorCOAr, fAMThDry, sNotes, fWinWall, fWinFloor, sCeilATDom, sCeilSADOM,
                      sCeilCADOM, sAGWDOM, sFNDWDOM, sSLABDOM, sFRFDOM, sWINDOM, sDUCTDOM, sHTGDOM,
                      sCLGDOM, sDHWDOM)
VALUES (@BLDG_RUN, @LMAX_Building, N'ALL_FIELDS_SET_15.8.blg', @RATING_NUMBER, 2, 38.461536,
        2135.000000, 27.027027, 222.000000, 22.727272, 1116.300049, 0.000000, 0.000000, 22.727272,
        128.300003, 0.000000, 0.000000, 21.371450, 1136.010010, 0.000000, 0.000000, 34.482758,
        966.000000, 4.000000, 21.000000, 2.000000, 86.000000, 0.000000, 0.000000, 0.500000,
        N'building notes;notes line 2', 0.027524, 0.015500, N'R-50.0', N'NA', N'R-35.0', N'R-11.0',
        N'R-34.3', N'R-0.0 Edge, R-0.0 Under', N'R*-34.5(assembly)', N'U-Value: 0.250, SHGC: 0.300',
        N'69.92 CFM25.', N'Heating::  Fuel-fired air distribution, Natural gas, 94.0 AFUE.',
        N'Cooling::  Air conditioner, Electric, 13.0 SEER.',
        N'Water Heating::  Conventional, Natural gas, 0.60 EF, 50.0 Gal.');
INSERT INTO ProjInfo (lBldgRunNo, lBldgNo, sPIPOwner, sPIStreet, sPICity, sPIState, sPIZip,
                      sPIPhone, SPIBuilder, sPIModel, sPIBldrDev, sPIBldrPho, sPIRatOrg, sPIRatPhon,
                      sPIRatName, sPIRaterNo, sPIRatDate, sPIRatngNo, sPIRatType, sPIRatReas,
                      sPIBldrStr, sPIBldrCty, sPIBlgName, sPIRatEMal, sPIRatStr, sPIRatCity,
                      sPIRatSt, sPIRatZip, sPIRatWeb, sPIBldrEml, sPIPRVDRID, sPIREGID, SPISAMSETID,
                      sPIBldrPrmt, sPIVer1Name, sPIVer1ID, sPIVer2Name, sPIVer2ID, sPIVer3Name,
                      sPIVer3ID, sPIVer4Name, sPIVer4ID, sPIRegDate, sPIPRMTDate)
VALUES (@BLDG_RUN, @LMAX_Building, N'I.M. Smith', N'2342 Maybee Ave.', N'Denver', N'CO', N'80333',
        N'303 444 4444', N'WeeBeeGood Builders', N'The Jubilee', N'Rocky View', N'303 111 2222',
        N'L.A. Raters', N'303 222 1111', N'H.I. Scorer', N'303 333 2222', N'1/9/18', @RATING_NUMBER,
        N'Based on plans', N'New home', N'bldr street 1', N'bldr street 1', N'the bldg name',
        N'a@laraters.com', N'rater street 1', N'rater city', N'AK', N'rater zip',
        N'www.laraters.com', N'bldr email', N'____-___', N'', N'0000', N'12345', N'Rater Name 1',
        N'RaterID1', N'Rater Name 2', N'RaterID2', N'Rater Name 3', N'RaterID3', N'Rater Name 4',
        N'RaterID4', N'', N'06/26/2019');
INSERT INTO BldgInfo (lBldgRunNo, lBldgNo, fBIVolume, fBIACond, nBIHType, nBILType, nBIStories,
                      nBIFType, nBIBeds, nBIUnits, sBIRateNo, nBICType, nBIYearBlt, nBIThBndry,
                      nBIStoryWCB, nBIInfltVol)
VALUES (@BLDG_RUN, @LMAX_Building, 16000.000000, 2000.000000, 1, 0, 1, 6, 3, 1, @RATING_NUMBER, 1,
        2008, 3, 1, 1);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'ek R-19 Draped, Full*', 14, 5, 6.800000, 4.400000, 5.500000,
        6.600000, 3, 4, 19.100000, 1.100000, 2.200000, 3.300000, 1, 2, N'qwer', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Cond Basement', 128.300003, 8.700000, 7.600000, 1.100000, 201,
        @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'Mobile Home Skirt', 18, 6, 0.100000, 0.000000, 0.000000,
        0.000000, 1, 4, 8.000000, 0.000000, 0.000000, 0.000000, 1, 2, N'', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'fwall 2', 4.000000, 7.700000, 7.700000, 0.000000, 202,
        @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'R-5 Ext, 2ft deep', 11, 0, 8.000000, 5.000000, 0.000000,
        2.000000, 1, 4, 0.000000, 0.000000, 0.000000, 0.000000, 1, 1, N'', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'fwall 3', 3.000000, 6.000000, 2.000000, 4.000000, 213,
        @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_SlabType := IFNULL((max(lSTSTNo) + 1), 1)
FROM SlabType;
INSERT INTO SlabType (lBldgRunNo, lSTSTNo, sSTType, fSTPIns, fSTUIns, fSTFUWid, nSTRadiant,
                      fSTPInsDep, sSTNote, nSTInsGrde, nSTFlrCvr)
VALUES (@BLDG_RUN, @LMAX_SlabType, N'Uninsulated', 0.000000, 0.000000, 0.000000, 2, 0.000000, N'',
        1, 1);
INSERT INTO Slab (lBldgRunNo, lBldgNo, szSFName, fSFArea, fSFDep, fSFPer, fSFExPer, fSFOnPer,
                  lSFSlabTNo, sSFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Heated Basement', 1000.000000, 7.000000, 128.000000,
        128.000000, 0.000000, @LMAX_SlabType, @RATING_NUMBER);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'ek R-38 Blown, Attic*', 0, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'', N'', N'', 0.055933);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 12.534999, 0.610000, 0.450000, 4.375000,
        6.000000, 0.110000, 0.220000, 0.330000, 0.440000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.840000, 20.670000, 0.610000, 0.450000, 13.000000,
        6.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 7.670000, 0.610000, 0.450000, 0.000000,
        6.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 3.500000, 24.000000, 6.000000, 13.000000,
        3.500000, 2, @LMAX_CompType, 0, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 1, 0.110000, 1, N'asf', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'pathlayer', 888.000000, 2, 2, 2, @LMAX_CeilType, 0.026000,
        @RATING_NUMBER, 2, 2, 888.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-50 Blown, Attic', 1, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'', N'', N'', 0.020105);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 43.045002, 0.610000, 0.450000, 4.375000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.840000, 51.669998, 0.610000, 0.450000, 13.000000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 38.670002, 0.610000, 0.450000, 0.000000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 3.500000, 24.000000, 37.000000, 13.000000,
        3.500000, 2, @LMAX_CompType, 1, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 0, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'asdf', 1000.000000, 2, 2, 2, @LMAX_CeilType, 0.026000,
        @RATING_NUMBER, 2, 2, 1000.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-35, Vaulted', 1, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'Plywood', N'Shingles', N'', 0.034638);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 19.434999, 0.610000, 0.450000, 11.875000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.840000, 37.559998, 0.610000, 0.450000, 30.000000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 7.560000, 0.610000, 0.450000, 0.000000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 9.500000, 24.000000, 5.000000, 30.000000,
        9.500000, 1, @LMAX_CompType, 1, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 0, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'qf vault', 222.000000, 1, 2, 2, @LMAX_CeilType, 0.037000,
        @RATING_NUMBER, 2, 2, 222.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Mobile Home Ceiling', 1, N'Gyp board', N'Framing',
        N'Insulation', N'', N'', N'', 0.103559);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity 1', 0.793324, 13.782499, 0.610000, 0.562500, 0.000000,
        12.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity 2', 0.046676, 12.727953, 0.610000, 0.562500, 0.000000,
        10.945454, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame 1', 0.103888, 7.657500, 0.610000, 0.562500, 4.375000,
        1.500000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame 2', 0.006112, 8.557500, 0.610000, 0.562500, 4.375000,
        2.400000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade 1', 0.047222, 1.782500, 0.610000, 0.562500, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade 2', 0.002778, 1.782500, 0.610000, 0.562500, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.625000, 1.500000, 3.500000, 24.000000, 0.000000, 0.000000,
        3.500000, 2, @LMAX_CompType, 1, 1, 4.000000, 12.000000, 16.500000, 4.000000, 24.000000,
        4.000000, 1.000000, 2, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'qwer', 333.000000, 2, 1, 2, @LMAX_CeilType, 0.026000,
        @RATING_NUMBER, 2, 2, 333.000000);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-110*', 1, N'Gyp board', N'Air Gap/Frm', N'Cavity ins/Frm',
        N'Continuous ins', N'Ext Finish', N'', 0.104441);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.720000, 13.240000, 0.680000, 0.450000, 0.000000,
        11.000000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.230000, 6.615000, 0.680000, 0.450000, 0.000000,
        4.375000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.270000, 0.680000, 0.450000, 0.000000,
        1.030000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO WallType (lBldgRunNo, lWTWTNo, fWTStudWdt, fWTStudDpt, fWTStudSpg, fWTGypThk,
                      fWTContIns, fWTCvtyIns, fWTCInsThk, fWTBlckIns, nWTCntnTyp, lWTCompNo,
                      bWTQFValid, fWTFF, bWTDFLTFF, sWTNote, nWTInsGrde)
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 3.500000, 16.000000, 0.500000, 0.000000, 11.000000,
        3.500000, 0.000000, 1, @LMAX_CompType, 1, 0.230000, 1, N'qwer', 3);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Exterior Wall', 1026.300049, 201, 1, 0.044000, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-150*', 1, N'Gyp board', N'Air Gap/Frm', N'Cavity ins/Frm',
        N'Continuous ins', N'Ext Finish', N'', 0.091823);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.720000, 17.240000, 0.680000, 0.450000, 0.000000,
        15.000000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.230000, 6.615000, 0.680000, 0.450000, 0.000000,
        4.375000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.270000, 0.680000, 0.450000, 0.000000,
        1.030000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO WallType (lBldgRunNo, lWTWTNo, fWTStudWdt, fWTStudDpt, fWTStudSpg, fWTGypThk,
                      fWTContIns, fWTCvtyIns, fWTCInsThk, fWTBlckIns, nWTCntnTyp, lWTCompNo,
                      bWTQFValid, fWTFF, bWTDFLTFF, sWTNote, nWTInsGrde)
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 3.500000, 16.000000, 0.500000, 0.000000, 15.000000,
        3.500000, 0.000000, 1, @LMAX_CompType, 1, 0.230000, 1, N'BigWall', 3);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Common Wall', 513.200012, 213, 1, 0.091823, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'SIP 12-3/8"', 0, N'Gyp board', N'Air Gap/Frm',
        N'Continuous ins', N'Ext Finish', N'', N'', 0.017709);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'SIP', 1.000000, 56.469997, 0.680000, 0.450000, 1.030000,
        53.200001, 0.940000, 0.000000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO WallType (lBldgRunNo, lWTWTNo, fWTStudWdt, fWTStudDpt, fWTStudSpg, fWTGypThk,
                      fWTContIns, fWTCvtyIns, fWTCInsThk, fWTBlckIns, nWTCntnTyp, lWTCompNo,
                      bWTQFValid, fWTFF, bWTDFLTFF, sWTNote, nWTInsGrde)
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 3.500000, 16.000000, 0.500000, 16.500000, 0.000000,
        0.000000, 0.000000, 1, @LMAX_CompType, 0, 0.230000, 1, N'', 1);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'pathlayer', 100.000000, 201, 2, 0.044000, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-300*', 1, N'Floor covering', N'Subfloor', N'Cavity ins',
        N'Continuous ins', N'Framing', N'', 0.047294);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.820000, 33.425003, 0.920000, 1.230000, 0.820000,
        30.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.130000, 15.925000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 12.500000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.425000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO FlrType (lBldgRunNo, lFTFTNo, fFTJstWdt, fFTJstHgt, fFTJstSpg, fFTContIns, fFTCvtyIns,
                     fFTCInsThk, nFTCovType, nFTTCTNo, bFTQFValid, NFTQFTYPE, FFTFLRWID, FFTOUTWID,
                     FFTBATTHK, FFTBATRVL, FFTBLKTHK, FFTBLKRVL, NFTCNTINS, NFTOUTINS, FFTFF,
                     BFTDFLTFF, SFTNOTE, nFTInsGrde)
VALUES (@BLDG_RUN, @LMAX_FlrType, 1.500000, 11.500000, 16.000000, 0.000000, 30.000000, 10.000000, 1,
        @LMAX_CompType, 1, 0, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0,
        0.130000, 1, N'', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ff1', 300.000000, 201, 0.029000, @LMAX_FlrType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Mobile Home Floor', 1, N'Floor covering', N'Particle board',
        N'Batt insulation', N'Blanket insulation', N'Framing', N'', 0.112370);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity, Outrigger', 0.415208, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame, Outrigger', 0.059792, 7.195000, 0.920000, 0.000000,
        0.820000, 0.000000, 0.000000, 5.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity, Center', 0.415208, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame, Center', 0.059792, 7.195000, 0.920000, 0.000000,
        0.820000, 0.000000, 0.000000, 5.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade, Outrigger', 0.025000, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade, Center', 0.025000, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO FlrType (lBldgRunNo, lFTFTNo, fFTJstWdt, fFTJstHgt, fFTJstSpg, fFTContIns, fFTCvtyIns,
                     fFTCInsThk, nFTCovType, nFTTCTNo, bFTQFValid, NFTQFTYPE, FFTFLRWID, FFTOUTWID,
                     FFTBATTHK, FFTBATRVL, FFTBLKTHK, FFTBLKRVL, NFTCNTINS, NFTOUTINS, FFTFF,
                     BFTDFLTFF, SFTNOTE, nFTInsGrde)
VALUES (@BLDG_RUN, @LMAX_FlrType, 2.000000, 6.000000, 24.000000, 0.000000, 0.000000, 0.000000, 0,
        @LMAX_CompType, 1, 2, 12.000000, 6.000000, 4.000000, 7.000000, 0.000000, 0.000000, 1, 1,
        0.119583, 1, N'', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ff mh', 222.000000, 202, 0.029000, @LMAX_FlrType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-25 pl*', 0, N'Floor covering', N'Subfloor', N'Cavity ins',
        N'Continuous ins', N'Framing', N'', 0.050193);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.820000, 28.890100, 0.920100, 1.230000, 0.820000,
        25.000000, 0.000000, 0.000000, 0.000000, 0.920000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.130000, 14.515000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 10.625000, 0.000000, 0.920000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Grade', 0.050000, 3.890000, 0.920000, 1.230000, 0.820000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.920000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'', 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000);
INSERT INTO FlrType (lBldgRunNo, lFTFTNo, fFTJstWdt, fFTJstHgt, fFTJstSpg, fFTContIns, fFTCvtyIns,
                     fFTCInsThk, nFTCovType, nFTTCTNo, bFTQFValid, NFTQFTYPE, FFTFLRWID, FFTOUTWID,
                     FFTBATTHK, FFTBATRVL, FFTBLKTHK, FFTBLKRVL, NFTCNTINS, NFTOUTINS, FFTFF,
                     BFTDFLTFF, SFTNOTE, nFTInsGrde)
VALUES (@BLDG_RUN, @LMAX_FlrType, 1.500000, 8.500000, 16.000000, 0.000000, 25.000000, 8.500000, 1,
        @LMAX_CompType, 0, 1, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0,
        0.130000, 1, N'', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'asdf', 444.000000, 203, 0.029000, @LMAX_FlrType,
        @RATING_NUMBER);
INSERT INTO Joist (lBldgRunNo, lBldgNo, szRJName, fRJArea, nRJLoc, fRJCoInsul, fRJFrInsul,
                   fRJSpacing, fRJUo, fRJInsulTh, sRJRateNo, nRJInsGrde)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rim, Cond', 128.300003, 201, 0.000000, 11.000000, 16.000000,
        0.044000, 3.500000, @RATING_NUMBER, 3);
SELECT @LMAX_DoorType := IFNULL((max(lDTDTNo) + 1), 1)
FROM DoorType;
INSERT INTO DoorType (lBldgRunNo, lDTDTNo, sDTType, nDTType, fDTRValue, sDTNote)
VALUES (@BLDG_RUN, @LMAX_DoorType, N'1-3/4 Wd solid core', 2, 2.100000, N'');
INSERT INTO Door (lBldgRunNo, lBldgNo, szDOName, fNOArea, nDOWallNum, lDODoorTNo, fDOUo, sDORateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Ext Doors', 40.000000, 2, @LMAX_DoorType, 0.329497,
        @RATING_NUMBER);
SELECT @LMAX_DoorType := IFNULL((max(lDTDTNo) + 1), 1)
FROM DoorType;
INSERT INTO DoorType (lBldgRunNo, lDTDTNo, sDTType, nDTType, fDTRValue, sDTNote)
VALUES (@BLDG_RUN, @LMAX_DoorType, N'Steel-ureth fm strm*', 1, 1.700000, N'');
INSERT INTO Door (lBldgRunNo, lBldgNo, szDOName, fNOArea, nDOWallNum, lDODoorTNo, fDOUo, sDORateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'door2', 0.000000, 6, @LMAX_DoorType, 0.000000, @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'UDRH(1)', 0.300000, 0.250000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'South Wall', 10.000000, 1, 0.850000, 0.700000, 1, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Wood', 0.580000, 0.490000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'North Wall', 5.000000, 5, 0.850000, 0.250000, 2, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'UDRH(3)', 0.300000, 0.250000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'East Wall', 11.000000, 3, 0.850000, 0.700000, 5, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Vinyl', 0.570000, 0.460000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'wall4', 5.000000, 7, 0.880000, 0.290000, 6, 0, @LMAX_WndwType,
        @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'UDRH(1)', 0.400000, 0.500000, N'');
INSERT INTO Skylight (lBldgRunNo, lBldgNo, szSKName, fSKGlzArea, nSKOr, fSKPitch, fSKSumShad,
                      fSKWtrShad, nSKSurfNum, lSKWinTNo, sSKRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sklite', 77.000000, 8, 2.000000, 0.700000, 1.000000, 2,
        @LMAX_WndwType, @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'UDRH(2)', 0.400000, 0.500000, N'');
INSERT INTO Skylight (lBldgRunNo, lBldgNo, szSKName, fSKGlzArea, nSKOr, fSKPitch, fSKSumShad,
                      fSKWtrShad, nSKSurfNum, lSKWinTNo, sSKRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sklite2', 9.000000, 2, 2.000000, 0.700000, 1.000000, 4,
        @LMAX_WndwType, @RATING_NUMBER);
SELECT @LMAX_Equip := IFNULL((max(lEIEINo) + 1), 1)
FROM Equip;
INSERT INTO Equip (lEIEINo, lBldgRunNo, lBldgNo, fEIHSetPnt, fEICSetPnt, nEISBThrm, nEISUThrm,
                   nEIVentTyp, nEISBSch, fEISBTemp, nEIDuctLoc, nEIDuctLo2, nEIDuctLo3, fEIDuctIns,
                   fEIDuctIn2, fEIDuctIn3, fEIDuctSup, fEIDuctSu2, fEIDuctSu3, fEIDuctRet,
                   fEIDuctRe2, fEIDuctRe3, nEIDuctLk, nEIDTUNITS, fEIDTLKAGE, nEIDTQUAL, sEIRateNo,
                   nEIHTGCAPWT, nEICLGCAPWT, nEIDHWCAPWT)
VALUES (@LMAX_Equip, @BLDG_RUN, @LMAX_Building, 68.000000, 78.000000, 1, 1, 1, 0, 66.000000, 5, 0,
        0, 0.000000, 0.000000, 0.000000, 100.000000, 0.000000, 0.000000, 100.000000, 0.000000,
        0.000000, 2, 11, 0.000000, 1, @RATING_NUMBER, 1, 1, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_HtgType := IFNULL((max(lHETHETNo) + 1), 1)
FROM HtgType;
INSERT INTO HtgType (lBldgRunNo, lHETHETNo, sHETType, nHETSystTp, nHETFuelTp, fHETRatCap, fHETEff,
                     nHETEffUTp, nHETDSHtr, nHETFnCtrl, nHETFnDef, fHETFnHSpd, fHETFnLSpd, sHETNote,
                     fHETAuxElc, nHETAuxETp, nHETAuxDef, fHETFanPwr, fHETPmpEng, nHETPmpTyp,
                     fHETRCap17)
VALUES (@BLDG_RUN, @LMAX_HtgType, N'UDRH', 1, 1, 48.000000, 94.000000, 1, 0, 1, 1, 800.000000,
        0.000000, N'', 712.000000, 1, 1, 0.000000, 0.000000, 1, 0.000000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, @LMAX_HtgType, -1, -1, -1, -1, -1, NULL, 1,
        100.000000, 3, 34.408604, 0.000000, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
Select max(lCETCETNo) as LMAX
from ClgType;
INSERT INTO ClgType (lBldgRunNo, lCETCETNo, sCETType, nCETSystTp, nCETFuelTp, fCETRatCap, fCETEff,
                     fCETSHF, nCETEffUTp, nCETDSHtr, nCETFnCtrl, nCETFnDef, fCETFnHSpd, fCETFnLSpd,
                     sCETNote, fCETFanPwr, fCETPmpEng, nCETPmpTyp, nCETFanDef)
VALUES (@BLDG_RUN, 58814, N'UDRH', 1, 4, 36.000000, 13.000000, 0.700000, 1, 0, 1, 0, 825.000000,
        0.000000, N'', 0.000000, 0.000000, 1, 0);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, 58814, -1, -1, NULL, 2, 100.000000, 3,
        0.000000, 42.857143, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
Select max(lDETDETNo) as LMAX
from DhwType;
INSERT INTO DhwType (lBldgRunNo, lDETDETNo, sDETType, nDETSystTp, nDETFuelTp, fDETTnkVol,
                     fDETTnkIns, fDETEnergy, fDETRecEff, sDETNote)
VALUES (@BLDG_RUN, @LMAX_DuctSystem, N'UDRH', 1, 1, 50.000000, 0.000000, 0.600000, 0.800000, N'');
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, @LMAX_DuctSystem, -1, NULL, 3,
        100.000000, 3, 0.000000, 0.000000, 100.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
Select max(lGSTGSTNo) as LMAX
from GshpType;
INSERT INTO GshpType (lBldgRunNo, lGSTGSTNo, sGSTType, nGSTType, nGSTFuel, fGSTHCOP70, fGSTHCOP50,
                      fGSTCEER70, fGSTCEER50, fGSTHCap70, fGSTHCap50, fGSTCCap70, fGSTCCap50,
                      fGSTHCOP32, fGSTHCap32, fGSTCEER77, fGSTCCap77, fGSTSHF, nGSTFanDef,
                      nGSTDSHtr, sGSTNote, fGSTBKUPCP, fGSTFanPwr, fGSTPmpEng, nGSTPmpEnT,
                      nGSTDbType)
VALUES (@BLDG_RUN, 5798, N'UDRH', 1, 4, 2.768200, 2.384000, 15.394000, 17.948400, 20.306000,
        15.814617, 12.129277, 13.279700, 2.038200, 11.500000, 14.500000, 12.000000, 0.700000, 1, 0,
        N'', 0.000000, 80.000000, 0.000000, 1, 1);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, 5798, -1, -1, -1, -1, NULL, 5, 100.000000, 3,
        8.243728, 14.285714, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
Select max(lASTASTNo) as LMAX
from AshpType;
INSERT INTO AshpType (lBldgRunNo, lASTASTNo, sASTType, nASTFuel, fASTHCap47, FASTHEFF, NASTHEFFU,
                      fASTCCAP, FASTCEFF, NASTCEFFU, fASTSHF, nASTDSHtr, sASTNote, fASTBKUPCP,
                      nASTFnCtrl, nASTFnDef, fASTFnHSpd, fASTFnLSpd, fASTHCap17)
VALUES (@BLDG_RUN, 23823, N'UDRH', 4, 18.000000, 6.954000, 3, 18.000000, 14.000000, 1, 0.700000, 0,
        N'', 0.000000, 1, 1, 0.000000, 0.000000, 10.980000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, -1, 23823, NULL, 4, 100.000000, 3,
        12.903226, 21.428572, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
Select max(lDFTDFTNo) as LMAX
from DfhpType;
INSERT INTO DfhpType (lBldgRunNo, lDFTDFTNo, sDFTType, nDFTFuel, fDFTHHSPF, fDFTHCap47, nDFTBFuel,
                      nDFTBEffU, fDFTBSEff, fDFTBCap, fDFTCSEER, fDFTCCap, fDFTCSHF, nDFTDSHtr,
                      fDFTSwitch, nDFTFnCtrl, nDFTFnDef, fDFTFnHSpd, fDFTFnLSpd, sDFTNote)
VALUES (@BLDG_RUN, 5259, N'UDRH', 4, 6.954000, 13.400000, 1, 1, 94.000000, 30.000000, 14.000000,
        18.000000, 0.700000, 0, 33.000000, 1, 1, 413.000000, 0.000000, N'');
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, 5259, -1, -1, -1, NULL, 6, 100.000000, 3,
        21.505377, 21.428572, 0.000000, 1);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_HtgType := IFNULL((max(lHETHETNo) + 1), 1)
FROM HtgType;
INSERT INTO HtgType (lBldgRunNo, lHETHETNo, sHETType, nHETSystTp, nHETFuelTp, fHETRatCap, fHETEff,
                     nHETEffUTp, nHETDSHtr, nHETFnCtrl, nHETFnDef, fHETFnHSpd, fHETFnLSpd, sHETNote,
                     fHETAuxElc, nHETAuxETp, nHETAuxDef, fHETFanPwr, fHETPmpEng, nHETPmpTyp,
                     fHETRCap17)
VALUES (@BLDG_RUN, @LMAX_HtgType, N'80AFUE Gas Furn 32k*', 6, 1, 32.000000, 30.000000, 1, 1, 1, 1,
        533.000000, 0.000000, N'Notes', 0.000000, 1, 0, 10.000000, 0.000000, 1, 30.000000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, @LMAX_HtgType, -1, -1, -1, -1, -1, NULL, 1,
        100.000000, 3, 22.939068, 0.000000, 0.000000, 1);
Select max(lGWellNo) as LMAX
from GshpWell;
INSERT INTO GshpWell (lBldgRunNo, sRateNo, lGWellNo, nGWType, fGWNoWells, fGWDepth, fGWLpFlow)
VALUES (@BLDG_RUN, @RATING_NUMBER, 6, 0, 8.000000, 100.000000, 2.000000);
Select max(lDhwDistNo) as LMAX
from DhwDistrib;
INSERT INTO DhwDistrib (lBldgRunNo, sRateNo, lDhwDistNo, bFixLowFlow, bDhwPipeIns, nRecircType,
                        fMaxFixDist, fSupRetDist, fPipeLenDhw, fPipeLenRec, fRecPumpPwr, bHasDwhr,
                        fDwhrEff, bDwhrPrehtC, bDwhrPrehtH, nShwrheads, nShwrToDwhr, fHwCtrlEff)
VALUES (@BLDG_RUN, @RATING_NUMBER, 29716, 1, 1, 3, 89.000000, 100.000000, 89.000000, 100.000000,
        50.000000, 0, 89.199997, 1, 1, 2, 1, 0.000000);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'measured', 6, -1, 50.220001, 9.300000, 1, 2,
        0.040000, 0.016000, 0.024000, 11, 2, @RATING_NUMBER, 1, 248.000000, 0.040000, 1, 0, 0, 2, 0,
        0, 1, Null, Null, 1, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 100.000000, 5, 0.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 100.000000, 5, 0.000000, 2, @RATING_NUMBER);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'total', 4, 5, 101.250000, 18.750000, 1, 2,
        0.040000, 0.016000, 0.024000, 11, 2, @RATING_NUMBER, 2, 500.000000, 1.440000, 0, 0, 0, 2, 1,
        0, 1, Null, Null, 0, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 80.000000, 8, 0.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 75.000000, 8, 0.000000, 2, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 20.000000, 6, 3.100000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 25.000000, 6, 4.100000, 2, @RATING_NUMBER);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'sup ret', 0, -1, 101.250000, 18.750000, 1, 2,
        0.040000, 0.016000, 0.024000, 11, 2, @RATING_NUMBER, 1, 500.000000, 0.060000, 0, 0, 0, 2, 1,
        0, 1, Null, Null, 0, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 80.000000, 8, 0.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 75.000000, 8, 0.000000, 2, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 20.000000, 6, 3.100000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 25.000000, 6, 4.100000, 2, @RATING_NUMBER);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'std 152', 3, 1, 101.250000, 18.750000, 1, 2,
        0.040000, 0.016000, 0.024000, 11, 2, @RATING_NUMBER, 3, 500.000000, 0.040000, 2, 0, 0, 2, 0,
        0, 1, Null, Null, 0, 1);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 80.000000, 8, 0.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 75.000000, 8, 0.000000, 2, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 20.000000, 6, 3.100000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 25.000000, 6, 4.100000, 2, @RATING_NUMBER);
INSERT INTO Infilt (lBldgRunNo, lBldgNo, lINInfilNo, nINType, fINHeatVal, fINCoolVal, nINWHInfUn,
                    lINMVType, fINMVRate, fINSREff, nINHrsDay, fINMVFan, sINRateNo, fINTREff,
                    nINVerify, nINShltrCl, nINClgVent, nINFanMotor, fINAnnual, fINTested,
                    nINGdAirXMF, nINNoMVMsrd, nINWattDflt)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 6, 5.000000, 5.000000, 3, 1, 100.000000, 0.000000, 24.000000,
        100.000000, @RATING_NUMBER, 0.000000, 2, 4, 1, 1, 5.000000, 7.000000, 0, 1, 1);
INSERT INTO LightApp (lBldgRunNo, lBldgNo, fLAOvnFuel, fLADryFuel, sLARateNo, nLAUseDef, fLARefKWh,
                      fLADishWEF, fLAFlrCent, fLAFanCFM, fLACFLCent, fLACFLExt, fLACFLGar,
                      nLARefLoc, fLADishWCap, fLADishWYr, nLAOvnInd, nLAOvnCon, nLADryLoc,
                      nLADryMoist, fLADryEF, fLADryMEF, fLADryGasEF, nLAWashLoc, fLAWashLER,
                      fLAWashCap, fLAWashElec, fLAWashGas, fLAWashGCst, fLAWashEff, fLALEDInt,
                      fLALEDExt, fLALEDGar)
VALUES (@BLDG_RUN, @LMAX_Building, 4, 4, @RATING_NUMBER, 1, 691.000000, 0.460000, 10.000000,
        70.400002, 9.800000, 4.100000, 1.700000, 1, 12.000000, 0.000000, 0, 1, 1, 1, 2.617391,
        0.796842, 2.670000, 1, 487.000000, 3.200000, 0.080300, 0.580000, 23.000000, 1, 90.199997,
        62.200001, 8.300000);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Int Ltg', 1, 1, 4, 1849.500000, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Ext Ltg', 1, 5, 4, 205.500000, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Refrigerator', 3, 1, 4, 775.000000, 4, 1.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Dishwasher', 5, 1, 4, 0.586957, 4, 247.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Dishwasher', 5, 1, 98, 7.347020, 5, 247.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Ceiling Fan', 14, 1, 4, 42.613602, 2, 168.000000, 3, 3,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Oven/Range', 7, 1, 4, 547.505005, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Dryer', 9, 1, 4, 900.007996, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Washer', 8, 1, 4, 90.000801, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Washer', 8, 1, 98, 8.248850, 5, 365.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Shower', 10, 1, 98, 46.743500, 5, 365.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Plug Loads', 2, 1, 4, 2871.169922, 4, 1.000000, 8, 1, 3);
INSERT INTO MandReq (lBldgRunNo, lBldgNo, nMRIECC04, nMRIECC06, nMRIECC09, nMRESV2TBC, nMRESV2PRD,
                     nMRESV3TEC, nMRESV3HC, nMRESV3HR, nMRESV3WM, nMRESV3AP, nMRESV3RF, nMRESV3CF,
                     nMRESV3EF, nMRESV3DW, nMRESV3NRF, nMRESV3NCF, nMRESV3NEF, nMRESV3NDW,
                     sMRRateNo, nMRIECCNY, nMRESV3SAF, fMRESV3BFA, nMRESV3NBB, nMRIECC12,
                     nMRFLORIDA, nMRESV3SLAB, nMRIECC15, sMRESQUAL4, nMRIECC18, nMRIECCMI,
                     NMRESMFWSHR, NMRESMFDRYR, NMRESMFWIN, nMRIECCNC)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 2, 3, 4,
        @RATING_NUMBER, 1, 1, 300.000000, 0, 1, 0, 1, 1, N'ENERGY STAR v1.1 MF', 0, 1, 1, 0, 1, 1);
INSERT INTO DOEChallenge (lBldgRunNo, lBldgNo, sDCBldrID, nDCFenstrtn, nDCInsul, nDCDuctLoc,
                          nDCAppl, nDCLighting, nDCFanEff, nDCAirQual, nDCSolarE, nDCSolarHW,
                          nDCAirPlus, nDCWtrSense, nDCIBHS, nDCMGMT, nDCWaiver, sDCRateNo,
                          nDCWaterEff)
VALUES (@BLDG_RUN, @LMAX_Building, N'ID156', 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1, 3, 2, 1,
        @RATING_NUMBER, 1);
INSERT INTO AddMass (lBldgRunNo, lBldgNo, szAMName, fAMArea, nAMLoc, nAMType, fAMThk, sAMRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'intmass', 66.000000, 1, 1, 7.000000, @RATING_NUMBER);
INSERT INTO ActSolar (lBldgRunNo, lBldgNo, nASSystem, nASLoop, fASColArea, nASOr, nASTilt, nASSpecs,
                      fASStgVol, sASRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 0, 0.000000, 0, 0.000000, 0, 0.000000, @RATING_NUMBER);
INSERT INTO PhotoVol (lBldgRunNo, lBldgNo, sPVName, nPVColType, fPVArea, fPVPower, fPVTilt, nPVOr,
                      fPVInvEff, sPVRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'', 0, 0.000000, 0.000000, 0.000000, 0, 0.000000,
        @RATING_NUMBER);
INSERT INTO SunSpace (lBldgRunNo, lBldgNo, fSSRfArea, fSSRFIns, fSSAGWArea, fSSAGWIns, fSSBGWArea,
                      fSSBGWIns, fSSArea, fSSFrmIns, fSSSlbPer, fSSSlbDep, fSSSlbThk, fSSSlbPIns,
                      fSSSlbUIns, sSSRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, 100.000000, 5.100000, 155.000000, 4.800000, 77.000000, 3.300000,
        101.000000, 7.000000, 111.000000, 3.000000, 8.000000, 5.500000, 4.400000, @RATING_NUMBER);
INSERT INTO SSMass (lBldgRunNo, lBldgNo, szSSMName, fSSMArea, nSSMType, fSSMThk, fSSMWVol,
                    sSSMRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ss intmass', 88.000000, 2, 12.000000, 0.000000,
        @RATING_NUMBER);
INSERT INTO SSCmnWal (lBldgRunNo, lBldgNo, szSSCName, fSSCArea, nSSCMTyp, fSSCMThk, fSSCIns,
                      nSSCFan, fSSCFlRate, sSSCRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sswall', 77.000000, 1, 5.000000, 4.000000, 1, 5.000000,
        @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Vinyl', 0.570000, 0.460000, N'');
INSERT INTO SSWindow (lBldgRunNo, lBldgNo, szSSWName, fSSWArea, nSSWOr, fSSWSum, fSSWWtr,
                      lSSWWdwTNo, sSSWRateNo, fSSOHDepth, fSSOHToTop, fSSOHToBtm, fSSAdjSum,
                      fSSAdjWtr)
VALUES (@BLDG_RUN, @LMAX_Building, N'sswin1', 88.000000, 7, 0.700000, 0.850000, @LMAX_WndwType,
        @RATING_NUMBER, 2.000000, 3.000000, 4.000000, 0.700000, 1.000000);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double/LoE - Wood', 0.460000, 0.390000, N'');
INSERT INTO SSSkLght (lBldgRunNo, lBldgNo, szSSSName, fSSSArea, nSSSOr, fSSSPitch, fSSSSum, fSSSWtr,
                      lSSSWdwTNo, sSSSRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'sssky', 66.000000, 2, 3.000000, 0.700000, 1.000000,
        @LMAX_WndwType, @RATING_NUMBER);
INSERT INTO ResnetDisc (lBldgRunNo, lBldgNo, nRDQ1, nRDQ2A, nRDQ2B, nRDQ2C, nRDQ2D, nRDQ2E,
                        sRDQ2EOTHR, nRDQ3A, nRDQ3B, nRDQ3C, NRDQ4HVACI, NRDQ4HVACB, NRDQ4THMLI,
                        NRDQ4THMLB, NRDQ4AIRSI, NRDQ4AIRSB, NRDQ4WINI, NRDQ4WINB, NRDQ4APPLI,
                        NRDQ4APPLB, NRDQ4CNSTI, NRDQ4CNSTB, NRDQ4OTHRI, NRDQ4OTHRB, SRDQ4OTHR,
                        sRateNo, nRDQ5)
VALUES (@BLDG_RUN, @LMAX_Building, 1, 1, 0, 1, 1, 1, N'this is the other text', 0, 1, 0, 1, 2, 2, 3,
        3, 1, 2, 3, 3, 1, 1, 3, 3, 2, N'other specify', @RATING_NUMBER, 1);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 1, 4, 286.577301, 0.000000, 247.284988, 0.000000, 266.626373, @RATING_NUMBER,
        0.000000, 533.862305);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 2, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 3, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 1, 1111.796509, 1595.687134, 72.576248, 6281.648926, 639.115906,
        @RATING_NUMBER, -0.000000, 9061.708984);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 5, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 6, 5, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, @RATING_NUMBER, 0.000000,
        0.000000);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 7, 2.356029, 0.000000, 0.013353, 0.518886, 2.888268, @RATING_NUMBER, 0.000000,
        2.888268);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 8, 0.000000, 1.487892, 0.010440, 1.060259, 2.558591, @RATING_NUMBER, 0.000000,
        2.558591);
INSERT INTO EconParam (lBldgRunNo, lBldgNo, sRateNo, nFSBaseline, sFSBldgName, fEPImpCost,
                       fEPImpLife, fEPMortRat, fEPMortPer, fEPDownPay, fEPAppVal, fEPInf,
                       fEPDisRate, fEPEnInf, fEPAnalPer, nEPImpLifeD, nEPMortRatD, nEPMortPerD,
                       nEPDownPayD, nEPInfD, nEPDisRateD, nEPEnInfD, nEPAnalPerD, nEPDOECalc,
                       nEPCalcMthd)
VALUES (@BLDG_RUN, @LMAX_Building, @RATING_NUMBER, 18, N'REM UDRH/Building Baseline: None',
        500.000000, 25.000000, 5.700000, 30.000000, 10.000000, 0.000000, 2.000000, 4.000000,
        2.300000, 15.000000, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1);
INSERT INTO Results (lBldgRunNo, fHTEff, fClgEff, fHWEff, fLhROOF, fLcROOF, fLhJOIST, fLcJOIST,
                     fLhAGWALL, fLcAGWALL, fLhFNDWALL, fLcFNDWALL, fLhWNDOSK, fLcWNDOSK, fLhFFLR,
                     fLcFFLR, fLhCRAWL, fLcCRAWL, fLhSLAB, fLcSLAB, fLhINF, fLcINF, fLhMECHVNT,
                     fLcMECHVNT, fLhDUCT, fLcDUCT, fLhASOL, fLcASOL, fLhSS, fLcSS, fLhIGAIN,
                     fLcIGAIN, fLhWHF, fLcWHF, fLhDOOR, fLcDOOR, fLhTOTAL, fLcTOTAL, fTotDHW,
                     fSolSave, fHtPeak, fAcsPeak, fAclPeak, fAcTPeak, fHbuck, fAcbuck, fWbuck,
                     fhCons, fcCons, fhCost, fcCost, fWcons, fWCost, fServCost, fTotCost, fRefrCons,
                     fFrzCons, fDryCons, fOvenCons, fLaOthCons, fLiHsCons, fLiCsCons, fRefrCost,
                     fFrzCost, fDryCost, fOvenCost, fLaOthCost, fLightCost, fLATotCons, fLATotCost,
                     fPVTotCons, fPVTotCost, fShellArea, fHTGLdPHDD, fCLGLdPHDD, fHTGDdPHDD,
                     fClgDdPHDD, fHTGACH, fCLGACH, sRateNo, fEMCO2TOT, fEMSO2TOT, fEMNOXTOT,
                     fEMCO2HTG, fEMCO2CLG, fEMCO2DHW, fEMCO2LA, fEMCO2PV, fEMSO2HTG, fEMSO2CLG,
                     fEMSO2DHW, fEMSO2LA, fEMSO2PV, fEMNOXHTG, fEMNOXCLG, fEMNOXDHW, fEMNOXLA,
                     fEMNOXPV, fEMHERSCO2, fEMHERSSO2, fEMHERSNOX, fSRCEGYHTG, fSRCEGYCLG,
                     fSRCEGYDHW, fSRCEGYLA, fSRCEGYPV, fDHWNoLoss)
VALUES (@BLDG_RUN, 0.814541, 3.690723, 0.499952, 5.023248, 2.226044, 0.597313, 0.026314, 4.744130,
        1.082384, 4.909039, 0.241862, 0.062317, 9.379951, 2.868117, 0.126350, 0.000000, 0.000000,
        1.463500, -1.011199, 4.652647, 0.462504, 9.605453, 1.098145, 2.900770, 1.181934, 0.000000,
        0.000000, -0.564761, 0.735830, -9.828079, 12.068655, 0.000000, -7.518981, 0.000000,
        0.000000, 26.433693, 20.099792, 12.486837, 0.000000, 24.136108, 19.117342, 0.000000,
        19.117342, 6.824166, 20.515562, 5.155720, 32.452259, 5.446031, 221.459595, 111.728386,
        24.976093, 128.769745, 150.000000, 1055.742188, 2.358383, 0.000000, 1.998696, 1.452560,
        8.327645, 1.012100, 0.882344, 48.818047, 0.000000, 41.372593, 30.067690, 172.380569,
        39.214607, 21.439075, 443.784454, -0.000000, -0.000000, 6887.609375, 0.997625, 2.921784,
        0.000911, 0.002779, 0.181641, 0.097913, @RATING_NUMBER, 16234.841797, 5.923902, 18.779491,
        4644.802734, 1730.711182, 3046.137451, 6813.190918, 0.000000, 0.740078, 1.037506, 0.062026,
        4.084291, 0.000000, 5.620240, 1.896776, 3.795546, 7.466928, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 7.843919);
INSERT INTO RegionalCode (lBldgRunNo, sRateNo, fNVRebate, fNYECRHCn, fNYECRCCn, fNYECRDCN,
                          fNYECRLACn, fNYECRPVCn, fNYECRTCn, fNYECDHCn, fNYECDCCn, fNYECDDCN,
                          fNYECDLACn, fNYECDPVCn, fNYECDTCn, bNYECC, fNVECRHCn, fNVECRCCn,
                          fNVECRDCN, fNVECRLACn, fNVECRPVCn, fNVECRTCn, fNVECDHCn, fNVECDCCn,
                          fNVECDDCN, fNVECDLACn, fNVECDPVCn, fNVECDTCn, bNVECC, fNCRHCT, fNCRCCT,
                          fNCRDCT, fNCRLACT, fNCRPVCT, fNCRSVCT, fNCRTCT, fNCDHCT, fNCDCCT, fNCDDCT,
                          fNCDLACT, fNCDPVCT, fNCDSVCT, fNCDTCT, bNCMeetCT, fNCRUA, fNCDUA,
                          bNCDctPass, bNCUAPass, bNCPass, fNCHRHCT, fNCHRCCT, fNCHRDCT, fNCHRLACT,
                          fNCHRPVCT, fNCHRSVCT, fNCHRTCT, fNCHDHCT, fNCHDCCT, fNCHDDCT, fNCHDLACT,
                          fNCHDPVCT, fNCHDSVCT, fNCHDTCT, bNCHMeetCT, fNCHRUA, fNCHDUA, bNCHDctPass,
                          bNCHUAPass, bNCHPass, fNYRHCT, fNyRCCT, fNYRDCT, fNYRLACT, fNYRPVCT,
                          fNYRSVCT, fNYRTCT, fNYDHCT, fNYDCCT, fNYDDCT, fNYDLACT, fNYDPVCT,
                          fNYDSVCT, fNYDTCT, bNYMeetCT, fNYRUA, fNYDUA, bNYDctPass, bNYUAPass,
                          bNYPass)
VALUES (@BLDG_RUN, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0, 281.652344, 131.296631, 97.347534, 427.644836, -0.000000, 150.000000,
        1087.941406, 258.028931, 158.062622, 97.249832, 442.428619, -0.000000, 150.000000,
        1105.770020, 0, 300.183197, 247.905914, 0, 0, 0, 272.926666, 131.056473, 97.351379,
        411.020599, -0.000000, 150.000000, 1062.355103, 258.028931, 158.062622, 97.249832,
        442.428619, -0.000000, 150.000000, 1105.770020, 0, 299.553192, 247.905914, 0, 0, 0,
        222.865280, 120.352203, 97.431519, 432.186646, -0.000000, 150.000000, 1022.708069,
        258.028931, 158.062622, 97.249832, 442.428619, -0.000000, 150.000000, 1105.770020, 0,
        278.656494, 247.905914, 1, 0, 0);
INSERT INTO HERSCode (lBldgRunNo, sRateNo, fHERSScor, fHERSCost, fHERSStars, fHERSRHCn, fHERSRCCn,
                      fHERSRDCN, fHERSRLACn, fHERSRPVCn, fHERSRTCn, fHERSDHCn, fHERSDCCn, fHERSDDCN,
                      fHERSDLACn, fHERSDPVCn, fHERSDTCn, FNYHERS, bTaxCredit, FHERS130)
VALUES (@BLDG_RUN, @RATING_NUMBER, -999.000000, 1190.206787, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0, 0.000000);
INSERT INTO ENERGYSTAR (lBldgRunNo, sRateNo, BESTARV2, BESTARV25, FV25HERSPV, FV25HERS, FV25HERSSA,
                        FV25SZADJF, BESTARV3, FV3HERSPV, FV3HERS, FV3HERSSA, FV3SZADJF, BESTARV3HI,
                        FV3HIHERSPV, FV3HIHERS, FV3HIHERSSA, FV3HISZADJF, BESTARV31, FV31HERSPV,
                        FV31HERS, FV31HERSSA, FV31SZADJF, BDOEPROGRAM, FDOEHERS, FDOEHERSSA,
                        BESTARV32W, FV32WHERSPV, FV32WHERS, FV32WHERSSA, FV32WSZADJF, BESTARV10MF,
                        FV10MFHERSPV, FV10MFHERS, BESTARV11MF, FV11MFHERSPV, FV11MFHERS,
                        BESTARV12MF, FV12MFHERSPV, FV12MFHERS)
VALUES (@BLDG_RUN, @RATING_NUMBER, 0, 0, -999.000000, -999.000000, -999.000000, 1.000000, Null,
        Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, 0,
        -999.000000, -999.000000, Null, Null, Null, Null, Null, Null, Null, Null, 0, -999.000000,
        -999.000000, Null, Null, Null);
INSERT INTO IECC (lBldgRunNo, sRateNo, f98IERHCn, f98IERCCn, f98IERDCN, f98IERLACn, f98IERPVCn,
                  f98IERTCn, f98IEDHCn, f98IEDCCn, f98IEDDCN, f98IEDLACn, f98IEDPVCn, f98IEDTCn,
                  b98IECC, f98IECCRUo, f98IECCDUo, b98IECCDuP, b98IECCuoP, f00IERHCn, f00IERCCn,
                  f00IERDCN, f00IERLACn, f00IERPVCn, f00IERTCn, f00IEDHCn, f00IEDCCn, f00IEDDCN,
                  f00IEDLACn, f00IEDPVCn, f00IEDTCn, b00IECC, f00IECCRUo, f00IECCDUo, b00IECCDuP,
                  b00IECCuoP, f01IERHCn, f01IERCCn, f01IERDCN, f01IERLACn, f01IERPVCn, f01IERTCn,
                  f01IEDHCn, f01IEDCCn, f01IEDDCN, f01IEDLACn, f01IEDPVCn, f01IEDTCn, b01IECC,
                  f01IECCRUo, f01IECCDUo, b01IECCDuP, b01IECCuoP, f03IERHCn, f03IERCCn, f03IERDCN,
                  f03IERLACn, f03IERPVCn, f03IERTCn, f03IEDHCn, f03IEDCCn, f03IEDDCN, f03IEDLACn,
                  f03IEDPVCn, f03IEDTCn, b03IECC, f03IECCRUo, f03IECCDUo, b03IECCDuP, b03IECCuoP,
                  f04IERHCT, f04IERCCT, f04IERDCT, f04IERLACT, f04IERPVCT, f04IERSVCT, f04IERTCT,
                  f04IEDHCT, f04IEDCCT, f04IEDDCT, f04IEDLACT, f04IEDPVCT, f04IEDSVCT, f04IEDTCT,
                  b04IECC, f04IECCRUA, f04IECCDUA, b04IECCDuP, b04IECCuAP, bPass04IECC, f06IERHCT,
                  f06IERCCT, f06IERDCT, f06IERLACT, f06IERPVCT, f06IERSVCT, f06IERTCT, f06IEDHCT,
                  f06IEDCCT, f06IEDDCT, f06IEDLACT, f06IEDPVCT, f06IEDSVCT, f06IEDTCT, b06IECC,
                  f06IECCRUA, f06IECCDUA, b06IECCDuP, b06IECCuAP, bPass06IECC, f09IERHCT, f09IERCCT,
                  f09IERDCT, f09IERLACT, f09IERPVCT, f09IERSVCT, f09IERTCT, f09IEDHCT, f09IEDCCT,
                  f09IEDDCT, f09IEDLACT, f09IEDPVCT, f09IEDSVCT, f09IEDTCT, b09IECC, f09IECCRUA,
                  f09IECCDUA, b09IECCDuP, b09IECCuAP, bPass09IECC, f12IERHCT, f12IERCCT, f12IERDCT,
                  f12IERLACT, f12IERPVCT, f12IERSVCT, f12IERTCT, f12IEDHCT, f12IEDCCT, f12IEDDCT,
                  f12IEDLACT, f12IEDPVCT, f12IEDSVCT, f12IEDTCT, b12IECC, f12IECCRUA, f12IECCDUA,
                  b12IECCDuP, b12IECCuAP, bPass12IECC, f15IERHCT, f15IERCCT, f15IERDCT, f15IERLACT,
                  f15IERPVCT, f15IERSVCT, f15IERTCT, f15IEDHCT, f15IEDCCT, f15IEDDCT, f15IEDLACT,
                  f15IEDPVCT, f15IEDSVCT, f15IEDTCT, b15IECC, f15IECCRUA, f15IECCDUA, b15IECCDuP,
                  b15IECCuAP, bPass15IECC, f18IERHCT, f18IERCCT, f18IERDCT, f18IERLACT, f18IERPVCT,
                  f18IERSVCT, f18IERTCT, f18IEDHCT, f18IEDCCT, f18IEDDCT, f18IEDLACT, f18IEDPVCT,
                  f18IEDSVCT, f18IEDTCT, b18IECC, f18IECCRUA, f18IECCDUA, b18IECCDuP, b18IECCuAP,
                  bPass18IECC)
VALUES (@BLDG_RUN, @RATING_NUMBER, 17.210453, 10.633814, 36.717297, 18.449287, -0.000000, 83.010849,
        29.206486, 5.555595, 31.128607, 21.439075, -0.000000, 87.329758, 0, 0.078729, 0.042664, 1,
        1, 17.210453, 10.633814, 36.717297, 18.449287, -0.000000, 83.010849, 29.206486, 5.555595,
        31.128607, 21.439075, -0.000000, 87.329758, 0, 0.078729, 0.042664, 1, 1, 17.210453,
        10.633814, 36.717297, 18.449287, -0.000000, 83.010849, 29.206486, 5.555595, 31.128607,
        21.439075, -0.000000, 87.329758, 0, 0.078729, 0.042664, 1, 1, 17.210453, 10.633814,
        36.717297, 18.449287, -0.000000, 83.010849, 29.206486, 5.555595, 31.128607, 21.439075,
        -0.000000, 87.329758, 0, 0.078729, 0.042664, 1, 1, 232.181030, 164.405792, 96.934296,
        392.178711, -0.000000, 150.000000, 1035.699829, 225.048431, 139.545120, 97.461700,
        443.370300, -0.000000, 150.000000, 1055.425537, 0, 303.238586, 247.905914, 1, 0, 0,
        204.547562, 111.917267, 96.934296, 393.979858, -0.000000, 150.000000, 957.379028,
        225.048431, 139.545120, 97.461700, 443.370300, -0.000000, 150.000000, 1055.425537, 0,
        303.238586, 247.905914, 1, 1, 1, 255.398376, 130.285675, 97.358566, 392.711395, -0.000000,
        150.000000, 1025.754028, 258.051575, 157.523407, 97.249847, 442.438782, -0.000000,
        150.000000, 1105.263672, 0, 299.504791, 247.905914, 1, 0, 0, 219.130127, 119.666176,
        97.302444, 432.268738, -0.000000, 150.000000, 1018.367493, 258.028931, 158.062622,
        97.249832, 442.428619, -0.000000, 150.000000, 1105.770020, 0, 274.922699, 247.905914, 1, 0,
        0, 222.865280, 120.352203, 97.431519, 432.186646, -0.000000, 150.000000, 1022.708069,
        258.028931, 158.062622, 97.249832, 442.428619, -0.000000, 150.000000, 1105.770020, 0,
        278.656494, 247.905914, 1, 0, 0, 222.794342, 120.547539, 97.431519, 426.742615, -0.000000,
        150.000000, 1017.388428, 258.028931, 158.062622, 97.249832, 442.428619, -0.000000,
        150.000000, 1105.770020, 0, 278.236511, 247.905914, 1, 0, 0);
INSERT INTO Site (lBldgRunNo, szSELabel, ISECity, fSEElev, nSEHS, nSECS, nSECSJSDay, nSEDegDayh,
                  nSEDegDayc, fSETAmbHS, fSETambCS, fSEHDD65, fSECDH74, sCLIMZONE, sRateNo,
                  fASHRAEWSF, fAveWindSpd, fAveAmbAirT)
VALUES (@BLDG_RUN, N'Fredonia, AZ', 0, 4672, 195, 170, 114, 3996.000000, 1102.000000, 45.049999,
        75.760002, 3847.000000, 23971.000000, N'5B', @RATING_NUMBER, 0.470000, 4.900000, 59.400002);
