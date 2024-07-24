# This is very similar to an export from REM/Rate to use it simply type the following
# mysql -u axis_test -p  remrate < axis/aec_remrate/data/All_FIELDS_16.3.2.sql

SET NAMES latin1;
SET character_set_results = NULL;
SET SQL_AUTO_IS_NULL = 0;

SET @RATING_NUMBER = CONCAT('16.3.2 Test: ', NOW());
SET @SBRDATE = DATE_FORMAT(NOW(), '%m/%d/%Y %H:%i:%s');

select database();
select database();

SELECT @@tx_isolation;
set @@sql_select_limit = DEFAULT;

SELECT @BLDG_RUN := IFNULL((max(lBldgRunNo) + 1), 1)
FROM BuildRun;

Select Count(*) as LCOUNT
FROM BuildRun
WHERE sBRRateNo = @RATING_NUMBER;

INSERT INTO BuildRun (lBldgRunNo, sBRDate, sBRProgVer, sBRRateNo, sBRFlag, lBRExpTpe, nInstance,
                      sBRProgFlvr, sBRUDRName, sBRUDRChk)
VALUES (@BLDG_RUN, @SBRDATE, N'16.3.2', @RATING_NUMBER, N'', 1, 0, N'Rate', N'', N'');
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
VALUES (@BLDG_RUN, @LMAX_Building, N'ALL_FIELDS_SET_16.3.2.blg', @RATING_NUMBER, 2, 21.164587,
        2135.000000, 29.362724, 222.000000, 11.581419, 1812.500000, 0.000000, 0.000000, 14.308522,
        128.300003, 0.000000, 0.000000, 30.431900, 2277.610107, 0.000000, 0.000000, 16.237514,
        966.000000, 2.391975, 31.000000, 2.176664, 86.000000, 3.120787, 14.400000, 0.500000,
        N'building notes
notes line 2', 0.015754, 0.015500, N'R-50.0', N'NA', N'R-35.0', N'R-11.0', N'R-34.3',
        N'R-0.0 Edge, R-0.0 Under', N'R*-19.9(assembly)', N'U-Value: 0.360, SHGC: 0.520',
        N'783.19 CFM25', N'Heating::  Fuel-fired air distribution, Natural gas, 80.0 AFUE.',
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
        N'L.A. Raters', N'303 222 1111', N'H.I. Scorer', N'303 333 2222', N'1/9/18',
        @RATING_NUMBER, N'Based on plans', N'New Home', N'bldr street 1', N'bldr street 1',
        N'the bldg name', N'a@laraters.com', N'rater street 1', N'rater city', N'AK', N'rater zip',
        N'www.laraters.com', N'bldr email', N'____-___', N'', N'0000', N'12345', N'Rater Name 1',
        N'RaterID1', N'Rater Name 2', N'RaterID2', N'Rater Name 3', N'RaterID3', N'Rater Name 4',
        N'RaterID4', N'', N'01/04/2022');

INSERT INTO BldgInfo (lBldgRunNo, lBldgNo, fBIVolume, fBIACond, nBIHType, nBILType, nBIStories,
                      nBIFType, nBIBeds, nBIUnits, sBIRateNo, nBICType, nBIYearBlt, nBIThBndry,
                      nBIStoryWCB, nBIInfltVol)
VALUES (@BLDG_RUN, @LMAX_Building, 16000.000000, 2000.000000, 1, 0, 2, 6, 3, 1, @RATING_NUMBER, 1,
        2022, 3, 2, 1);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'ek R-19 Draped, Full*', 14, 5, 6.800000, 4.400000, 1.000000,
        1.100000, 3, 4, 19.100000, 1.100000, 0.200000, 0.300000, 1, 2, N'qwer', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Cond Basement', 258.299988, 8.700000, 7.600000, 1.100000, 229,
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
VALUES (@BLDG_RUN, @LMAX_Building, N'fwall 2
', 4.000000, 7.700000, 6.700000, 1.000000, 230, @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_FndwType := IFNULL((max(lFWTWTNo) + 1), 1)
FROM FndwType;
INSERT INTO FndwType (lBldgRunNo, lFWTWTNo, sFWTType, nFWTType, nFWTStdTyp, fFWTMasThk, fFWTExtIns,
                      fFWTExInsT, fFWTExInsB, nFWTEInTTp, nFWTEInBTp, fFWTInInCt, fFWTInInFC,
                      fFWTInInsT, fFWTInInsB, nFWTIInTTp, nFWTIInBTp, sFWTNote, nFWTInsGrd)
VALUES (@BLDG_RUN, @LMAX_FndwType, N'R-5 Ext, 2ft deep', 11, 0, 8.000000, 5.000000, 0.000000,
        2.000000, 1, 4, 0.000000, 0.000000, 0.000000, 0.000000, 1, 1, N'', 3);
INSERT INTO FndWall (lBldgRunNo, lBldgNo, szFWName, fFWLength, fFWHeight, fFWDBGrade, fFWHAGrade,
                     nFWLoc, lFWFWTNo, sFWRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'fwall 3
', 3.000000, 6.000000, 2.000000, 4.000000, 229, @LMAX_FndwType, @RATING_NUMBER);
SELECT @LMAX_SlabType := IFNULL((max(lSTSTNo) + 1), 1)
FROM SlabType;
INSERT INTO SlabType (lBldgRunNo, lSTSTNo, sSTType, fSTPIns, fSTUIns, fSTFUWid, nSTRadiant,
                      fSTPInsDep, sSTNote, nSTInsGrde, nSTFlrCvr)
VALUES (@BLDG_RUN, @LMAX_SlabType, N'Uninsulated', 0.000000, 0.000000, 0.000000, 2, 0.000000, N'',
        1, 1);
INSERT INTO Slab (lBldgRunNo, lBldgNo, szSFName, fSFArea, fSFDep, fSFPer, fSFExPer, fSFOnPer,
                  lSFSlabTNo, sSFRateNo, nSFLoc)
VALUES (@BLDG_RUN, @LMAX_Building, N'Heated Basement', 1000.000000, 7.000000, 128.000000,
        125.000000, 1.200000, @LMAX_SlabType, @RATING_NUMBER, 2);
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
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.500000, 1.500000, 3.500000, 24.000000, 0.000000, 0.000000,
        0.000000, 2, @LMAX_CompType, 0, 2, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 1.000000, 1, 0.110000, 1, N'asf', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'pathlayer', 888.000000, 2, 1, 6, @LMAX_CeilType, 0.055933,
        @RATING_NUMBER, 2, 2, 888.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-50 Blown, Attic', 1, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'', N'', N'', 0.020070);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 43.045002, 0.610000, 0.450000, 4.375000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.845500, 51.669998, 0.610000, 0.450000, 13.000000,
        37.000000, 0.000000, 0.000000, 0.000000, 0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade', 0.044500, 38.670002, 0.610000, 0.450000, 0.000000,
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
VALUES (@BLDG_RUN, @LMAX_Building, N'asdf', 1000.000000, 2, 0, 4, @LMAX_CeilType, 0.020070,
        @RATING_NUMBER, 1, 2, 1000.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-35, Vaulted', 1, N'Gyp board', N'Cavity Ins/Frm',
        N'Continuous ins', N'Plywood', N'Shingles', N'', 0.034057);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.110000, 19.434999, 0.610000, 0.450000, 11.875000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.845500, 37.559998, 0.610000, 0.450000, 30.000000,
        5.000000, 0.930000, 0.400000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade', 0.044500, 7.560000, 0.610000, 0.450000, 0.000000,
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
VALUES (@BLDG_RUN, @LMAX_Building, N'qf vault', 222.000000, 1, 0, 5, @LMAX_CeilType, 0.034057,
        @RATING_NUMBER, 2, 1, 222.000000);
SELECT @LMAX_CeilType := IFNULL((max(lCTCTNo) + 1), 1)
FROM CeilType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Mobile Home Ceiling', 1, N'Gyp board', N'Framing',
        N'Insulation', N'', N'', N'', 0.100874);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity 1
', 0.798518, 13.782499, 0.610000, 0.562500, 0.000000, 12.000000, 0.000000, 0.000000, 0.000000,
        0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity 2
', 0.046982, 12.727953, 0.610000, 0.562500, 0.000000, 10.945454, 0.000000, 0.000000, 0.000000,
        0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame 1
', 0.103888, 7.657500, 0.610000, 0.562500, 4.375000, 1.500000, 0.000000, 0.000000, 0.000000,
        0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame 2
', 0.006112, 8.557500, 0.610000, 0.562500, 4.375000, 2.400000, 0.000000, 0.000000, 0.000000,
        0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade 1
', 0.042027, 1.782500, 0.610000, 0.562500, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.610000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade 2
', 0.002473, 1.782500, 0.610000, 0.562500, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.610000);
INSERT INTO CeilType (lBldgRunNo, lCTCTNo, fCTGypThk, fCTRftrWdt, fCTRftrHgt, fCTRftrSpc,
                      fCTContIns, fCTCvtyIns, fCTCInsThk, nCTCeilTyp, lCTCompNo, bCTQFValid,
                      NCTINSTYP, FCTUNRDEP, FCTUNRRVL, FCTCLGWID, FCTCLGRSE, FCTTRSHGT, FCTHELHGT,
                      FCTVNTSPC, NCTQFTYP, FCTFF, BCTDFLTFF, sCTNote, NCTINSGRDE)
VALUES (@BLDG_RUN, @LMAX_CeilType, 0.625000, 1.500000, 3.500000, 24.000000, 0.000000, 0.000000,
        3.500000, 2, @LMAX_CompType, 1, 1, 4.000000, 12.000000, 16.500000, 4.000000, 24.000000,
        4.000000, 1.000000, 2, 0.110000, 1, N'', 3);
INSERT INTO Roof (lBldgRunNo, lBldgNo, szROName, fROArea, nROType, nRORadBar, nROCol, lROCeilTNo,
                  fROUo, sRORateNo, nROClay, nROVent, fRORoofArea)
VALUES (@BLDG_RUN, @LMAX_Building, N'qwer', 333.000000, 2, 1, 2, @LMAX_CeilType, 0.100874,
        @RATING_NUMBER, 2, 2, 333.000000);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-110*', 1, N'Gyp board', N'Air Gap/Frm', N'Cavity ins/Frm',
        N'Continuous ins', N'Ext Finish', N'', 0.101792);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.731500, 13.240000, 0.680000, 0.450000, 0.000000,
        11.000000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.230000, 6.615000, 0.680000, 0.450000, 0.000000,
        4.375000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade', 0.038500, 3.270000, 0.680000, 0.450000, 0.000000,
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
        3.500000, 0.000000, 1, @LMAX_CompType, 1, 0.230000, 1, N'QF Wall notes rock', 3);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Exterior Wall', 1026.300049, 201, 1, 0.101792, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-22, R-10 Cont.', 1, N'Gyp board', N'Air Gap/Frm',
        N'Cavity ins/Frm', N'Continuous ins', N'Ext Finish', N'', 0.035648);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.761188, 34.239994, 0.680000, 0.450000, 0.000000,
        22.000000, 10.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.198750, 19.115002, 0.680000, 0.450000, 0.000000,
        6.875000, 10.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade', 0.040062, 13.270000, 0.680000, 0.450000, 0.000000,
        1.030000, 10.000000, 0.940000, 0.000000, 0.170000);
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
VALUES (@BLDG_RUN, @LMAX_WallType, 1.500000, 5.500000, 24.000000, 0.500000, 10.000000, 22.000000,
        5.500000, 0.000000, 1, @LMAX_CompType, 1, 0.198750, 1, N'', 3);
INSERT INTO AGWall (lBldgRunNo, lBldgNo, szAGName, fAGArea, nAGLoc, nAGCol, fAGUo, lAGWallTNo,
                    sAGRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Garage ', 200.000000, 202, 2, 0.035648, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_WallType := IFNULL((max(lWTWTNo) + 1), 1)
FROM WallType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-150*', 1, N'Gyp board', N'Air Gap/Frm', N'Cavity ins/Frm',
        N'Continuous ins', N'Ext Finish', N'', 0.088974);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.731500, 17.240000, 0.680000, 0.450000, 0.000000,
        15.000000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.230000, 6.615000, 0.680000, 0.450000, 0.000000,
        4.375000, 0.000000, 0.940000, 0.000000, 0.170000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade', 0.038500, 3.270000, 0.680000, 0.450000, 0.000000,
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
VALUES (@BLDG_RUN, @LMAX_Building, N'Common Wall', 513.200012, 203, 2, 0.088974, @LMAX_WallType,
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
VALUES (@BLDG_RUN, @LMAX_Building, N'pathlayer', 100.000000, 201, 6, 0.017709, @LMAX_WallType,
        @RATING_NUMBER);
SELECT @LMAX_FlrType := IFNULL((max(lFTFTNo) + 1), 1)
FROM FlrType;
SELECT @LMAX_CompType := IFNULL((max(lTCTTCTTNo) + 1), 1)
FROM CompType;
INSERT INTO CompType (lBldgRunNo, lTCTTCTTNo, sTCTType, nTCTQFVal, sTCTLNm1, sTCTLNm2, sTCTLNm3,
                      sTCTLNm4, sTCTLNm5, sTCTLNm6, fTCTUo)
VALUES (@BLDG_RUN, @LMAX_CompType, N'R-300*', 1, N'Floor covering', N'Subfloor', N'Cavity ins',
        N'Continuous ins', N'Framing', N'', 0.040867);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity', 0.826500, 34.625004, 0.920000, 1.230000, 0.820000,
        30.000000, 1.200000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Framing', 0.130000, 17.125000, 0.920000, 1.230000, 0.820000,
        0.000000, 1.200000, 12.500000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade', 0.043500, 4.625000, 0.920000, 1.230000, 0.820000,
        0.000000, 1.200000, 0.000000, 0.000000, 0.455000);
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
VALUES (@BLDG_RUN, @LMAX_FlrType, 1.500000, 11.500000, 16.000000, 1.200000, 30.000000, 10.000000, 1,
        @LMAX_CompType, 1, 0, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0,
        0.130000, 1, N'QF Note', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'ff1', 300.000000, 201, 0.040867, @LMAX_FlrType,
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
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity, Outrigger', 0.418198, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame, Outrigger', 0.059792, 7.195000, 0.920000, 0.000000,
        0.820000, 0.000000, 0.000000, 5.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cavity, Center', 0.418198, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Frame, Center', 0.059792, 7.195000, 0.920000, 0.000000,
        0.820000, 0.000000, 0.000000, 5.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade, Outrigger', 0.022010, 9.195000, 0.920000, 0.000000,
        0.820000, 7.000000, 0.000000, 0.000000, 0.000000, 0.455000);
INSERT INTO HeatPath (lBldgRunNo, lHPTCTTNo, sHPPthName, fHPPthArea, fHPPthRVal, fHPLRval1,
                      fHPLRval2, fHPLRval3, fHPLRval4, fHPLRval5, fHPLRval6, fHPLRval7, fHPLRval8)
VALUES (@BLDG_RUN, @LMAX_CompType, N'Cav.Grade, Center', 0.022010, 9.195000, 0.920000, 0.000000,
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
VALUES (@BLDG_RUN, @LMAX_FlrType, 1.500000, 11.500000, 16.000000, 0.000000, 0.000000, 0.000000, 1,
        @LMAX_CompType, 0, 1, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0,
        0.130000, 1, N'Path note', 3);
INSERT INTO FrameFlr (lBldgRunNo, lBldgNo, szFFName, fFFArea, nFFLoc, fFFUo, lFFFlorTNo, sFFRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'asdf', 444.000000, 202, 0.050193, @LMAX_FlrType,
        @RATING_NUMBER);
INSERT INTO Joist (lBldgRunNo, lBldgNo, szRJName, fRJArea, nRJLoc, fRJCoInsul, fRJFrInsul,
                   fRJSpacing, fRJUo, fRJInsulTh, sRJRateNo, nRJInsGrde)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rim, Cond', 128.300003, 202, 2.700000, 11.000000, 16.000000,
        0.069888, 3.500000, @RATING_NUMBER, 3);
SELECT @LMAX_DoorType := IFNULL((max(lDTDTNo) + 1), 1)
FROM DoorType;
INSERT INTO DoorType (lBldgRunNo, lDTDTNo, sDTType, nDTType, fDTRValue, sDTNote)
VALUES (@BLDG_RUN, @LMAX_DoorType, N'1-3/4 Wd solid core', 2, 2.100000, N'');
INSERT INTO Door (lBldgRunNo, lBldgNo, szDOName, fNOArea, nDOWallNum, lDODoorTNo, fDOUo, sDORateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'Ext Doors', 12.000000, 3, @LMAX_DoorType, 0.329497,
        @RATING_NUMBER);
SELECT @LMAX_DoorType := IFNULL((max(lDTDTNo) + 1), 1)
FROM DoorType;
INSERT INTO DoorType (lBldgRunNo, lDTDTNo, sDTType, nDTType, fDTRValue, sDTNote)
VALUES (@BLDG_RUN, @LMAX_DoorType, N'Steel-ureth fm strm*', 1, 1.700000, N'With Storm door');
INSERT INTO Door (lBldgRunNo, lBldgNo, szDOName, fNOArea, nDOWallNum, lDODoorTNo, fDOUo, sDORateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'door2', 2.400000, 7, @LMAX_DoorType, 0.275108, @RATING_NUMBER);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Wood', 0.580000, 0.490000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr, nWDOperate)
VALUES (@BLDG_RUN, @LMAX_Building, N'South Wall', 10.000000, 1, 0.800000, 0.200000, 1, 0,
        @LMAX_WndwType, @RATING_NUMBER, 2.000000, 1.200000, 1.300000, 0.400000, 0.700000, 1);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Dbl/LoE/Argon - Wood', 0.450000, 0.360000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr, nWDOperate)
VALUES (@BLDG_RUN, @LMAX_Building, N'North Wall', 5.000000, 5, 0.850000, 0.250000, 3, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.300000, 0.200000, 0.700000, 0.100000, 0.700000, 1);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Triple - Vinyl', 0.520000, 0.360000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr, nWDOperate)
VALUES (@BLDG_RUN, @LMAX_Building, N'East Wall', 11.000000, 3, 0.830000, 0.230000, 6, 0,
        @LMAX_WndwType, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000, 1);
SELECT @LMAX_WndwType := IFNULL((max(lWDTWinNo) + 1), 1)
FROM WndwType;
INSERT INTO WndwType (lBldgRunNo, lWDTWinNo, sWDTType, fWDTSHGC, fWDTUValue, sWDTNote)
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Double - Vinyl', 0.570000, 0.460000, N'');
INSERT INTO Window (lBldgRunNo, lBldgNo, szWDName, fWDArea, nWDOr, fWDSumShad, fWDWtrShad,
                    nWDSurfNum, nWDSurfTyp, lWDWinTNo, sWDRateNo, fWDOHDepth, fWDOHToTop,
                    fWDOHToBtm, fWDAdjSum, fWDAdjWtr, nWDOperate)
VALUES (@BLDG_RUN, @LMAX_Building, N'wall4', 5.000000, 7, 0.880000, 0.290000, 7, 0, @LMAX_WndwType,
        @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 1.000000, 1.000000, 1);
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
VALUES (@BLDG_RUN, @LMAX_Building, N'sklite2', 9.000000, 2, 3.000000, 0.700000, 0.100000, 4,
        @LMAX_WndwType, @RATING_NUMBER);
SELECT @LMAX_Equip := IFNULL((max(lEIEINo) + 1), 1)
FROM Equip;
INSERT INTO Equip (lEIEINo, lBldgRunNo, lBldgNo, fEIHSetPnt, fEICSetPnt, nEISBThrm, nEISUThrm,
                   nEIVentTyp, nEISBSch, fEISBTemp, nEIDuctLoc, nEIDuctLo2, nEIDuctLo3, fEIDuctIns,
                   fEIDuctIn2, fEIDuctIn3, fEIDuctSup, fEIDuctSu2, fEIDuctSu3, fEIDuctRet,
                   fEIDuctRe2, fEIDuctRe3, nEIDuctLk, nEIDTUNITS, fEIDTLKAGE, nEIDTQUAL, sEIRateNo,
                   nEIHTGCAPWT, nEICLGCAPWT, nEIDHWCAPWT, nEIDHUCAPWT, fEIWHFFlow, fEIWHFWatts)
VALUES (@LMAX_Equip, @BLDG_RUN, @LMAX_Building, 68.000000, 78.000000, 1, 0, 1, 0, 66.000000, 0, 0,
        0, 0.000000, 0.000000, 0.000000, 100.000000, 0.000000, 0.000000, 100.000000, 0.000000,
        0.000000, 2, 2, 100.000000, 1, @RATING_NUMBER, 1, 1, 1, 1, 200.000000, 50.000000);
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
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, @LMAX_HtgType, -1, -1, -1, -1, -1, NULL, 1,
        100.000000, 1, 30.658192, 0.000000, 0.000000, 1, Null, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_DehumidType := IFNULL((max(lDhuEqKey) + 1), 1)
from DehumidType;
INSERT INTO DehumidType (lBldgRunNo, lDhuEqKey, sName, nSystem, nFuel, fCapacity, fEfficiency,
                         sNote)
VALUES (@BLDG_RUN, @LMAX_DehumidType, N'Portable 20pts/day', 2, 4, 20.100000, 1.600000,
        N'Humidifier NOtes');
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, -1, -1, NULL, 9, 100.000000, 1,
        0.000000, 0.000000, 0.000000, 1, Null, 0.000000, 0.000000, 100.000000, 0.000000, 0.000000,
        1, @LMAX_DehumidType, -1, 0);
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
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, @LMAX_ClgType, -1, -1, NULL, 2,
        100.000000, 3, 0.000000, 42.857143, 0.000000, 1, Null, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
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
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, @LMAX_DhwType, -1, NULL, 3,
        100.000000, 1, 0.000000, 0.000000, 50.000000, 1,
        Null, 50.000000, 50.000000, 0.000000, 0.000000, 0.000000, 1, -1, -1, 0);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_DhwType := IFNULL((max(lDETDETNo) + 1), 1)
FROM DhwType;
INSERT INTO DhwType (lBldgRunNo, lDETDETNo, sDETType, nDETSystTp, nDETFuelTp, fDETTnkVol,
                     fDETTnkIns, fDETEnergy, fDETRecEff, sDETNote)
VALUES (@BLDG_RUN, @LMAX_DhwType, N'Demand-Gas 0.69EF', 3, 1, 0.000000, 0.000000, 0.699000, 0.000000,
        N'Notes for DH');
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, @LMAX_DhwType, -1, NULL, 3,
        100.000000, 5, 0.000000, 0.000000, 50.000000, 1, Null, 50.000000, 50.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
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
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, @LMAX_GshpType, -1, -1, -1, -1, NULL, 5,
        100.000000, 3, 7.345192, 14.285714, 0.000000, 1, Null, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
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
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, -1, -1, -1, @LMAX_AshpType, NULL, 4,
        100.000000, 1, 22.396448, 21.428572, 0.000000, 1, Null, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
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
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, -1, -1, @LMAX_DfhpType, -1, -1, -1, NULL, 6,
        100.000000, 1, 19.161371, 21.428572, 0.000000, 1, Null, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
SELECT @LMAX_EqInst := IFNULL((max(lEIEINo) + 1), 1)
FROM EqInst;
SELECT @LMAX_HtgType := IFNULL((max(lHETHETNo) + 1), 1)
FROM HtgType;
INSERT INTO HtgType (lBldgRunNo, lHETHETNo, sHETType, nHETSystTp, nHETFuelTp, fHETRatCap, fHETEff,
                     nHETEffUTp, nHETDSHtr, nHETFnCtrl, nHETFnDef, fHETFnHSpd, fHETFnLSpd, sHETNote,
                     fHETAuxElc, nHETAuxETp, nHETAuxDef, fHETFanPwr, fHETPmpEng, nHETPmpTyp,
                     fHETRCap17)
VALUES (@BLDG_RUN, @LMAX_HtgType, N'80AFUE Gas Furn 32k', 1, 1, 32.000000, 80.000000, 1, 0, 1, 1,
        533.000000, 0.000000, N'', 446.847992, 1, 1, 0.000000, 0.000000, 1, 0.000000);
INSERT INTO EqInst (lEIEINo, lBldgRunNo, lBldgNo, lEIHETNo, lEIGSTNo, lEIDFTNo, lEICLTNo, lEIDHTNo,
                    lEIASTNO, lEIHDTNO, nEISysType, fEIPerAdj, nEILoc, fEIHLdSrv, fEICLdSrv,
                    fEIDLdSrv, nEINoUnits, fEIDSE, fCWLoadSrvd, fDWLoadSrvd, fDhuLoadSrvd,
                    fMVHtgLoadSrvd, fMVClgLoadSrvd, nDwellUnitsDhw, lDhuEqKey, lSharedEqKey,
                    nPrecondSharedMV)
VALUES (@LMAX_EqInst, @BLDG_RUN, @LMAX_Building, @LMAX_HtgType, -1, -1, -1, -1, -1, NULL, 1,
        100.000000, 1, 20.438795, 0.000000, 0.000000, 1, Null, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 1, -1, -1, 0);
SELECT @LMAX_GshpWell := IFNULL((max(lGWellNo) + 1), 1)
FROM GshpWell;
INSERT INTO GshpWell (lBldgRunNo, sRateNo, lGWellNo, nGWType, fGWNoWells, fGWDepth, fGWLpFlow)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_GshpWell, 0, 8.000000, 100.000000, 2.000000);
SELECT @LMAX_DhwDistrib := IFNULL((max(lDhwDistNo) + 1), 1)
FROM DhwDistrib;
INSERT INTO DhwDistrib (lBldgRunNo, sRateNo, lDhwDistNo, bFixLowFlow, bDhwPipeIns, nRecircType,
                        fMaxFixDist, fSupRetDist, fPipeLenDhw, fPipeLenRec, fRecPumpPwr, bHasDwhr,
                        fDwhrEff, bDwhrPrehtC, bDwhrPrehtH, nShwrheads, nShwrToDwhr, fHwCtrlEff,
                        nHomesServed)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_DhwDistrib, 1, 1, 3, 89.000000, 100.000000, 109.000000,
        120.000000, 50.000000, 1, 89.199997, 1, 1, 2, 1, 0.000000, 1);
SELECT @LMAX_HvacCx := IFNULL((max(lHvacCxNo) + 1), 1)
from HvacCx;
INSERT INTO HvacCx (lBldgRunNo, sRateNo, lHvacCxNo, nDuctSysNo, nHtgEquipNo, nClgEquipNo,
                    nTotDuctLeakGrade, bTotDuctLeakExcep, bTotDuctLeakGrdIMet, fTotDuctLeakage,
                    nBFAirflowGrade, bBFAirflowException, nBFAirflowDesignSpec, nBFAirflowOpCond,
                    nBFWattDrawGrade, nBFWattDraw, fBFEffic, bRCSinglePkgSystem,
                    bRCOnboardDiagnostic, nRCTestMethod, nRCGrade, fDiffDTD, fDiffCTOA, fDeviation,
                    fRptdRefrigWeight)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_HvacCx, 0, -1, -1, 1, 0, 0, 0.000000, 3, 0, 2, 200, 3, 200,
        1.000000, 0, 0, 0, 3, 0.000000, 0.000000, 0.000000, 0.000000);
SELECT @LMAX_HvacCx := IFNULL((max(lHvacCxNo) + 1), 1)
from HvacCx;
INSERT INTO HvacCx (lBldgRunNo, sRateNo, lHvacCxNo, nDuctSysNo, nHtgEquipNo, nClgEquipNo,
                    nTotDuctLeakGrade, bTotDuctLeakExcep, bTotDuctLeakGrdIMet, fTotDuctLeakage,
                    nBFAirflowGrade, bBFAirflowException, nBFAirflowDesignSpec, nBFAirflowOpCond,
                    nBFWattDrawGrade, nBFWattDraw, fBFEffic, bRCSinglePkgSystem,
                    bRCOnboardDiagnostic, nRCTestMethod, nRCGrade, fDiffDTD, fDiffCTOA, fDeviation,
                    fRptdRefrigWeight)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_HvacCx, 1, -1, -1, 1, 1, 0, 0.000000, 1, 1, 2, 200, 1, 200,
        0.000000,
        0, 0, 0, 3, 0.000000, 0.000000, 0.000000, 0.000000);
SELECT @LMAX_HvacCx := IFNULL((max(lHvacCxNo) + 1), 1)
from HvacCx;
INSERT INTO HvacCx (lBldgRunNo, sRateNo, lHvacCxNo, nDuctSysNo, nHtgEquipNo, nClgEquipNo,
                    nTotDuctLeakGrade, bTotDuctLeakExcep, bTotDuctLeakGrdIMet, fTotDuctLeakage,
                    nBFAirflowGrade, bBFAirflowException, nBFAirflowDesignSpec, nBFAirflowOpCond,
                    nBFWattDrawGrade, nBFWattDraw, fBFEffic, bRCSinglePkgSystem,
                    bRCOnboardDiagnostic, nRCTestMethod, nRCGrade, fDiffDTD, fDiffCTOA, fDeviation,
                    fRptdRefrigWeight)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_HvacCx, 3, -1, -1, 1, 0, 1, 0.000000, 3, 0, 2, 201, 3, 203,
        1.009950,
        0, 0, 0, 3, 0.000000, 0.000000, 0.000000, 0.000000);
SELECT @LMAX_HvacCx := IFNULL((max(lHvacCxNo) + 1), 1)
from HvacCx;
INSERT INTO HvacCx (lBldgRunNo, sRateNo, lHvacCxNo, nDuctSysNo, nHtgEquipNo, nClgEquipNo,
                    nTotDuctLeakGrade, bTotDuctLeakExcep, bTotDuctLeakGrdIMet, fTotDuctLeakage,
                    nBFAirflowGrade, bBFAirflowException, nBFAirflowDesignSpec, nBFAirflowOpCond,
                    nBFWattDrawGrade, nBFWattDraw, fBFEffic, bRCSinglePkgSystem,
                    bRCOnboardDiagnostic, nRCTestMethod, nRCGrade, fDiffDTD, fDiffCTOA, fDeviation,
                    fRptdRefrigWeight)
VALUES (@BLDG_RUN, @RATING_NUMBER, @LMAX_HvacCx, -1, -1, 2, 1, 1, 1, 0.000000, 3, 1, 2, 200, 3, 200,
        1.000000,
        0, 0, 1, 1, 34.400002, 0.000000, 0.000000, 0.000000);
SELECT @LMAX_DuctSystem := IFNULL((max(lDSDSNo) + 1), 1)
FROM DuctSystem;
INSERT INTO DuctSystem (lBldgRunNo, lBldgNo, lDSDSNo, szDSName, lDSHtgNo, lDSClgNo, fDSSupArea,
                        fDSRetArea, lDSRegis, nDSDLeakTy, fDSDLeakTo, fDSDLeakSu, fDSDLeakRe,
                        nDSDLeakUn, lDSDLeakET, sDSRateNo, nDSDLeakTT, fDSCFArea, fDSDLeakRTo,
                        nDSDLeakRUn, nDSDLeakTEx, nDSInpType, nDSLtOType, nDSIECCEx, nDSRESNETEx,
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType, fDSDSE)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'measured', 8, -1, 50.200001, 9.300000, 1, 2,
        0.890000, 0.356000, 0.534000, 2, 2, @RATING_NUMBER, 1, 248.000000, 0.890000, 2, 0, 1, 2, 0,
        1, 1, 0.820000, 0.850000, 1, 3, Null);
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
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType, fDSDSE)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'total', 6, 6, 101.300003, 18.799999, 3, 2,
        1.200000, 0.480000, 0.720000, 12, 2, @RATING_NUMBER, 2, 500.000000, 0.890000, 2, 0, 0, 2,
        1, 0, 1, Null, Null, 1, 1, Null);
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
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType, fDSDSE)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'sup ret', 0, -1, 101.300003, 18.799999, 1, 3,
        30.000000, 12.000000, 18.000000, 2, 2, @RATING_NUMBER, 1, 500.000000, 15.000000, 2, 0, 0, 3,
        1, 0, 1, Null, Null, 0, 2, Null);
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
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType, fDSDSE)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'std 152', 5, 5, 101.300003, 18.799999, 1, 2,
        32.299999, 12.919999, 19.380001, 2, 2, @RATING_NUMBER, 3, 500.000000, 32.299999, 2, 0, 0, 2,
        0, 0, 1, Null, Null, 0, 3, Null);
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
                        nDSESTAREx, fDSTestLtO, fDSTestDL, nDSIsDucted, nDSTestType, fDSDSE)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, N'DFHP Sutt', 7, 7, 54.000004, 10.000000, 1, 2,
        0.000000, 0.000000, 0.000000, 2, 2, @RATING_NUMBER, 1, 200.000000, 0.000000, 2, 0, 0, 2, 1,
        0, 0, Null, Null, 0, 3, Null);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 100.000000, 10, 0.000000, 1, @RATING_NUMBER);
INSERT INTO Duct (lBldgRunNo, lBldgNo, lDUDSNo, fDUArea, nDULoc, fDUIns, nDUDctType, sDURateNo)
VALUES (@BLDG_RUN, @LMAX_Building, @LMAX_DuctSystem, 100.000000, 10, 0.000000, 2, @RATING_NUMBER);
INSERT INTO Infilt (lBldgRunNo, lBldgNo, lINInfilNo, nINType, fINHeatVal, fINCoolVal, nINWHInfUn,
                    lINMVType, fINMVRate, fINSREff, nINHrsDay, fINMVFan, sINRateNo, fINTREff,
                    nINVerify, nINShltrCl, nINClgVent, nINFanMotor, fINAnnual, fINTested,
                    nINGdAirXMF, nINNoMVMsrd, nINWattDflt)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 6, 7.100000, 7.100000, 3, Null, Null, Null, Null, Null,
        @RATING_NUMBER, Null, 2, 4, 1, Null, 7.100000, 7.000000, Null, Null, Null);
INSERT INTO MechVent (lBldgRunNo, lBldgNo, sMVRateNo, sMVName, nMVType, fMVRate, nMVHrsDay,
                      fMVFanPwr, fMVASRE, fMVATRE, nMVNotMsrd, nMVWattDflt, nMVFanMotor, nMVDuctNo,
                      nMVShrdMF, nMVHtgNo, nMVClgNo, fMVShrdCFM, fMVOAPct, fMVRecirc)
VALUES (@BLDG_RUN, @LMAX_Building, @RATING_NUMBER, N'Ventillation System 1', 1, 100.000000,
        24.000000, 100.000000, 11.200000, 9.000000, 1, 0, 0, -1, 0, -1, -1, 0.000000, 100.000000,
        0.000000);
INSERT INTO MechVent (lBldgRunNo, lBldgNo, sMVRateNo, sMVName, nMVType, fMVRate, nMVHrsDay,
                      fMVFanPwr, fMVASRE, fMVATRE, nMVNotMsrd, nMVWattDflt, nMVFanMotor, nMVDuctNo,
                      nMVShrdMF, nMVHtgNo, nMVClgNo, fMVShrdCFM, fMVOAPct, fMVRecirc)
VALUES (@BLDG_RUN, @LMAX_Building, @RATING_NUMBER, N'Number2', 4, 50.000000, 6.000000, 320.000000,
        0.000000, 0.000000, 0, 1, 1, 0, 0, -1, -1, 0.000000, 100.000000, 0.000000);
INSERT INTO LightApp (lBldgRunNo, lBldgNo, fLAOvnFuel, fLADryFuel, sLARateNo, nLAUseDef, fLARefKWh,
                      fLADishWEF, fLAFlrCent, fLAFanCFM, fLACFLCent, fLACFLExt, fLACFLGar,
                      nLARefLoc, fLADishWCap, fLADishWYr, nLAOvnInd, nLAOvnCon, nLADryLoc,
                      nLADryMoist, fLADryEF, fLADryMEF, fLADryGasEF, nLAWashLoc, fLAWashLER,
                      fLAWashCap, fLAWashElec, fLAWashGas, fLAWashGCst, fLAWashEff, fLALEDInt,
                      fLALEDExt, fLALEDGar, nLAFanCnt, nLAOvnLoc, nLADryUnit, nLAWashPre,
                      nLAWashUnit, nLAWashDhw, fLAWashIWF, nLAWashLoad, nLADishLoc, nLADishPre,
                      nLADishDhw, fLADishElec, fLADishGas, fLADishGCst, nLADishLoad)
VALUES (@BLDG_RUN, @LMAX_Building, 4, 4, @RATING_NUMBER, 0, 775.000000, 0.460000, 0.000000,
        70.400002, 9.800000, 4.100000, 1.700000, 1, 12.000000, 467.000000, 0, 1, 1, 0, 2.320000,
        2.060000, 2.670000, 1, 152.000000, 4.200000, 0.120000, 1.090000, 12.000000, 5, 90.199997,
        62.200001, 8.300000, 4, 1, 1, 7, 1, -1, 0.000000, 6, 1, 1, -1, 0.120000, 1.090000,
        33.119999, 4);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Int Ltg', 1, 1, 4, 1849.500000, 4, 1.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Ext Ltg', 1, 5, 4, 205.500000, 4, 1.100000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Refrigerator', 3, 1, 4, 775.000000, 4, 1.300000, 8, 3,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Dishwasher', 5, 1, 4, 0.587000, 4, 247.000000, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Dishwasher', 5, 1, 98, 7.300000, 5, 247.300003, 8, 1,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Rated - Ceiling Fan', 14, 1, 4, 42.613998, 2, 168.000000, 3, 3,
        3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Oven/Range', 7, 1, 4, 547.500000, 4, 1.500000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Dryer', 9, 1, 4, 900.000000, 4, 1.600000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Washer', 8, 1, 4, 90.000000, 4, 1.600000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Clothes Washer', 8, 1, 98, 8.249000, 5, 365.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Shower', 10, 1, 98, 46.743000, 5, 365.000000, 8, 1, 3);
INSERT INTO LAInst (lBldgRunNo, lBldgNo, SLAINAME, NLAITYPE, NLAILOC, NLAIFUEL, FLAIRATE, NLAIRATEU,
                    FLAIUSE, NLAIUSEU, NLAIQTY, NLAIEFF)
VALUES (@BLDG_RUN, @LMAX_Building, N'Plug Loads', 2, 1, 4, 2871.199951, 4, 1.900000, 8, 1, 3);
INSERT INTO MandReq (lBldgRunNo, lBldgNo, nMRIECC04, nMRIECC06, nMRIECC09, nMRESV2TBC, nMRESV2PRD,
                     nMRESV3TEC, nMRESV3HC, nMRESV3HR, nMRESV3WM, nMRESV3AP, nMRESV3RF, nMRESV3CF,
                     nMRESV3EF, nMRESV3DW, nMRESV3NRF, nMRESV3NCF, nMRESV3NEF, nMRESV3NDW,
                     sMRRateNo, nMRIECCNY, nMRESV3SAF, fMRESV3BFA, nMRESV3NBB, nMRIECC12,
                     nMRFLORIDA, nMRESV3SLAB, nMRIECC15, sMRESQUAL4, nMRIECC18, nMRIECCMI,
                     NMRESMFWSHR, NMRESMFDRYR, NMRESMFWIN, nMRIECCNC, nMRNGBS15)
VALUES (@BLDG_RUN, @LMAX_Building, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 2, 3, 4,
        @RATING_NUMBER, 1, 1, 300.000000, 0, 1, 0, 1, 1, N'ENERGY STAR v1.2 MF WA, OR', 1, 1, 0, 0,
        1, 1, 0);
INSERT INTO DOEChallenge (lBldgRunNo, lBldgNo, sDCBldrID, nDCFenstrtn, nDCInsul, nDCDuctLoc,
                          nDCAppl, nDCLighting, nDCFanEff, nDCAirQual, nDCSolarE, nDCSolarHW,
                          nDCAirPlus, nDCWtrSense, nDCIBHS, nDCMGMT, nDCWaiver, sDCRateNo,
                          nDCWaterEff, nDCPassiveHome)
VALUES (@BLDG_RUN, @LMAX_Building, N'ID156', 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1, 3, 2, 1,
        @RATING_NUMBER, 1, 1);
INSERT INTO AddMass (lBldgRunNo, lBldgNo, szAMName, fAMArea, nAMLoc, nAMType, fAMThk, sAMRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, N'intmass', 66.000000, 1, 1, 7.000000, @RATING_NUMBER);
INSERT INTO ActSolar (lBldgRunNo, lBldgNo, nASSystem, nASLoop, fASColArea, nASOr, nASTilt, nASSpecs,
                      fASStgVol, sASRateNo)
VALUES (@BLDG_RUN, @LMAX_Building, 1, 1, 88.000000, 1, 44.000000, 1, 33.000000, @RATING_NUMBER);
INSERT INTO PhotoVol (lBldgRunNo, lBldgNo, sPVName, nPVColType, fPVArea, fPVPower, fPVTilt, nPVOr,
                      fPVInvEff, sPVRateNo, nPVNumBeds)
VALUES (@BLDG_RUN, @LMAX_Building, N'pv1', 0, 111.199997, 88.000000, 55.000000, 2, 12.000000,
        @RATING_NUMBER, 3);
INSERT INTO PhotoVol (lBldgRunNo, lBldgNo, sPVName, nPVColType, fPVArea, fPVPower, fPVTilt, nPVOr,
                      fPVInvEff, sPVRateNo, nPVNumBeds)
VALUES (@BLDG_RUN, @LMAX_Building, N'pv2', 0, 99.000000, 77.000000, 49.000000, 4, 11.100000,
        @RATING_NUMBER, 3);
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
VALUES (@BLDG_RUN, @LMAX_WndwType, N'Triple - Wood', 0.530000, 0.390000, N'');
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
VALUES (@BLDG_RUN, 1, 4, 340.291626, 0.000000, 16.644718, 0.000000, 178.106262, @RATING_NUMBER,
        0.000000, 356.936340);
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
VALUES (@BLDG_RUN, 4, 1, 3469.385010, 4067.768066, 3.589183, 14672.875000, 1492.694702,
        @RATING_NUMBER, -27.186556, 22186.429688);
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
VALUES (@BLDG_RUN, 4, 7, 12.396146, 0.000000, 0.001242, 1.275003, 13.672392, @RATING_NUMBER,
        0.000000, 13.672392);
INSERT INTO FuelSum (lBldgRunNo, nFSFuel, nFSUnits, fFSHCons, fFSCCons, fFSWCons, fFSLACons,
                     fFSTotCost, sRateNo, fFSPVCons, fFSTotCons)
VALUES (@BLDG_RUN, 4, 8, 0.000000, 4.168509, 0.000000, 2.528205, 6.696714, @RATING_NUMBER, 0.000000,
        6.696715);
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
VALUES (@BLDG_RUN, 1.042022, 2.923477, 0.403939, 9.297644, -0.458490, 0.846872, 0.014910, 14.942533,
        2.050218, 6.940500, 0.136648, 0.346018, 11.247483, 5.678439, 0.099973, 0.000000, 0.000000,
        1.471491, -1.066414, 7.846936, 1.151022, 9.717331, 0.398213, 14.786115, 7.513192, -0.000000,
        0.000000, -0.587917, 0.805596, -23.825886, 25.194178, 0.000000, -6.505344, 0.337568,
        0.005943, 47.797642, 40.587124, 0.677983, 12.726692, 106.114594, 48.846821, 0.000000,
        48.846821, 8.711559, 19.869438, 5.101706, 45.870068, 13.883167, 399.599792, 275.850739,
        1.678428, 8.562843, 150.000000, 1820.801147, 10.315793, 0.000000, 4.914720, 2.802926,
        18.618872, 3.784524, 3.299328, 203.649902, 0.000000, 97.024269, 55.334152, 367.565674,
        139.846344, 50.078068, 988.619507, -0.092787, -1.831758, 8749.809570, 1.419991, 4.644241,
        0.003152, 0.005589, 0.350511, 0.169645, @RATING_NUMBER, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 9.219870);
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
                          bNYPass, fNYRMVCT, fNYDMVCT)
VALUES (@BLDG_RUN, @RATING_NUMBER, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0, 398.351227, 151.318634, 112.952866, 423.833618, -0.000000, 150.000000,
        1236.456299, 472.306946, 246.640045, 18.554508, 469.779449, -1.882059, 150.000000,
        1355.398926, 0, 418.020691, 465.761230, 0, 0, 0, 386.970337, 151.050217, 112.952866,
        406.568298, -0.000000, 150.000000, 1207.541748, 472.306946, 246.640045, 18.554508,
        469.779449, -1.882059, 150.000000, 1355.398926, 0, 416.658691, 465.761230, 0, 0, 0,
        336.825470, 131.355011, 112.952866, 417.094543, -0.000000, 150.000000, 1148.227905,
        472.306946, 246.640045, 18.554508, 469.779449, -1.882059, 150.000000, 1355.398926, 0,
        383.978699, 465.761230, 0, 0, 0, 18.520144, 90.788872);
INSERT INTO HERSCode (lBldgRunNo, sRateNo, fHERSScor, fHERSCost, fHERSStars, fHERSRHCn, fHERSRCCn,
                      fHERSRDCN, fHERSRLACn, fHERSRPVCn, fHERSRTCn, fHERSDHCn, fHERSDCCn, fHERSDDCN,
                      fHERSDLACn, fHERSDPVCn, fHERSDTCn, FNYHERS, bTaxCredit, FHERS130, NBADORIENT)
VALUES (@BLDG_RUN, @RATING_NUMBER, -999.000000, -999.000000, 150.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0, -999.000000, -1);
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
                  bPass18IECC, f18IERMVCT, f18IEDMVCT)
VALUES (@BLDG_RUN, @RATING_NUMBER, 28.384636, 16.569714, 48.918495, 45.602112, -0.000000,
        139.474960, 44.559189, 13.458432, 1.685858, 50.078068, -0.092787, 109.688759, 1, 0.092624,
        0.060693, 0, 0, 28.384636, 16.569714, 48.918495, 45.602112, -0.000000, 139.474960,
        44.559189, 13.458432, 1.685858, 50.078068, -0.092787, 109.688759, 1, 0.092624, 0.060693, 0,
        0, 28.384636, 16.569714, 48.918495, 45.602112, -0.000000, 139.474960, 44.559189, 13.939558,
        1.685777, 50.078068, -0.092787, 110.169807, 1, 0.092624, 0.060693, 0, 0, 28.384636,
        16.569714, 48.918495, 45.602112, -0.000000, 139.474960, 44.559189, 13.939558, 1.685777,
        50.078068, -0.092787, 110.169807, 1, 0.092624, 0.060693, 0, 0, 301.673187, 239.404480,
        113.225746, 917.106567, -0.000000, 150.000000, 1721.409912, 316.211853, 265.664978,
        6.357284, 992.840027, -1.839578, 150.000000, 1729.234619, 1, 420.379791, 465.761230, 0, 0,
        0, 260.890991, 172.341492, 113.225746, 921.147583, -0.000000, 150.000000, 1617.605835,
        316.211853, 265.664978, 18.801216, 992.840027, -1.839578, 150.000000, 1741.678467, 0,
        420.379791, 465.761230, 0, 0, 0, 302.809418, 202.683670, 112.952866, 918.391479, -0.000000,
        150.000000, 1686.837402, 379.575317, 317.682556, 18.554508, 989.378967, -1.833165,
        150.000000, 1853.358276, 0, 414.557129, 465.761230, 0, 0, 0, 301.091614, 129.016190,
        112.952866, 428.438660, -0.000000, 150.000000, 1121.499268, 472.306946, 246.640045,
        18.554508, 469.779449, -1.882059, 150.000000, 1355.398926, 0, 379.064026, 465.761230, 0, 0,
        0, 305.725891, 129.623184, 112.952866, 428.350098, -0.000000, 150.000000, 1126.652100,
        472.306946, 246.640045, 18.554508, 469.779449, -1.882059, 150.000000, 1355.398926, 0,
        384.886719, 465.761230, 0, 0, 0, 305.089386, 129.665375, 112.952866, 399.080780, -0.000000,
        150.000000, 1115.332031, 472.306946, 246.640045, 18.554508, 378.990570, -1.882059,
        150.000000, 1355.398926, 0, 383.978699, 465.761230, 0, 0, 0, 18.543673, 90.788872);
INSERT INTO Site (lBldgRunNo, szSELabel, ISECity, fSEElev, nSEHS, nSECS, nSECSJSDay, nSEDegDayh,
                  nSEDegDayc, fSETAmbHS, fSETambCS, fSEHDD65, fSECDH74, sCLIMZONE, sRateNo,
                  fASHRAEWSF, fAveWindSpd, fAveAmbAirT)
VALUES (@BLDG_RUN, N'Fredonia, AZ', 0, 4672, 195, 170, 114, 3996.000000, 1102.000000, 45.049999,
        75.760002, 3847.000000, 23971.000000, N'5B', @RATING_NUMBER, 0.470000, 4.900000, 59.400002);
