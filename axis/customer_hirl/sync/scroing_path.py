"""scroing_path.py: """

__author__ = "Artem Hruzd"
__date__ = "05/26/2021 9:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

HIRL_INTERNAL_API_SCORING_PATH = [
    {
        "ID": 1,
        "fkStandardID": 2,
        "ScoringPath": "Single-Family New Construction",
        "ScoringPathAlias": "Single-Family New Construction",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Buy",
    },
    {
        "ID": 2,
        "fkStandardID": 2,
        "ScoringPath": "Multi-Unit New Construction",
        "ScoringPathAlias": "Multi-Unit New Construction",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Rent",
    },
    {
        "ID": 3,
        "fkStandardID": 2,
        "ScoringPath": "Single-Family Additions >= 75%",
        "ScoringPathAlias": "Single-Family Additions &ge; 75%",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Buy",
    },
    {
        "ID": 5,
        "fkStandardID": 2,
        "ScoringPath": "Green Subdivision",
        "ScoringPathAlias": "Green Subdivision",
        "ProjectType": "GS",
        "FindABuilderTabIndex": "3",
        "GCPStandardYear": "2008",
    },
    {
        "ID": 6,
        "fkStandardID": 2,
        "ScoringPath": "Single-Family Green Remodel Renovation",
        "ScoringPathAlias": "Single-Family Green Remodel Path (pre-1980)",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 8,
        "fkStandardID": 2,
        "ScoringPath": "Multi-Unit Green Remodel Renovation",
        "ScoringPathAlias": "Multi-Unit Green Remodel Path (pre-1980)",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 9,
        "fkStandardID": 2,
        "ScoringPath": "Single-Family Additions < 75%",
        "ScoringPathAlias": "Single-Family Additions < 75%",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 16,
        "fkStandardID": 2,
        "ScoringPath": "Green Building Renovations with Additions < 75%",
        "ScoringPathAlias": "Green Building Path Renovations with Additions < 75% ",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 19,
        "fkStandardID": 2,
        "ScoringPath": "Single-Family Green Building Renovation",
        "ScoringPathAlias": "Single-Family Green Building Path Renovation ",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 20,
        "fkStandardID": 2,
        "ScoringPath": "Multi-Unit  Green Building Renovation",
        "ScoringPathAlias": "Multi-Unit Green Building Path Renovation ",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 21,
        "fkStandardID": 2,
        "ScoringPath": "Renovations with Addition >= 75%",
        "ScoringPathAlias": "Renovations with Addition &ge; 75%",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Buy",
    },
    {
        "ID": 26,
        "fkStandardID": 2,
        "ScoringPath": "Green Remodel Renovations with Additions < 75%",
        "ScoringPathAlias": "Green Remodel Path including Additions < 75%",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Remodel",
    },
    {
        "ID": 27,
        "fkStandardID": 2,
        "ScoringPath": "Modular - Single-Family",
        "ScoringPathAlias": "Modular - Single-Family",
        "ProjectType": "NA",
        "GCPStandardYear": "2008",
        "NGBSdotCom": "Buy",
    },
    {
        "ID": 28,
        "fkStandardID": 1,
        "ScoringPath": "Single-Family New Construction",
        "ScoringPathAlias": "Single-Family New Construction",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
    },
    {
        "ID": 29,
        "fkStandardID": 3,
        "ScoringPath": "2012 SF New Construction",
        "ScoringPathAlias": "2012 SF New Construction",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Buy",
        "ViewIndex": "10",
    },
    {
        "ID": 30,
        "fkStandardID": 3,
        "ScoringPath": "2012 MF New Construction",
        "ScoringPathAlias": "2012 MF New Construction",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Rent",
        "ViewIndex": "30",
    },
    {
        "ID": 31,
        "fkStandardID": 3,
        "ScoringPath": "2012 SF Whole House Remodel",
        "ScoringPathAlias": "2012 SF Whole House Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "20",
    },
    {
        "ID": 32,
        "fkStandardID": 3,
        "ScoringPath": "2012 MF Remodel Building",
        "ScoringPathAlias": "2012 MF Remodel Building",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "40",
    },
    {
        "ID": 33,
        "fkStandardID": 3,
        "ScoringPath": "2012 Green Subdivision",
        "ScoringPathAlias": "2012 Green Subdivision",
        "ProjectType": "GS",
        "FindABuilderTabIndex": "3",
        "GCPStandardYear": "2012",
        "ViewIndex": "90",
    },
    {
        "ID": 34,
        "fkStandardID": 3,
        "ScoringPath": "2012 Kitchen Remodel",
        "ScoringPathAlias": "2012 Kitchen Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "50",
    },
    {
        "ID": 35,
        "fkStandardID": 3,
        "ScoringPath": "2012 Bathroom Remodel",
        "ScoringPathAlias": "2012 Bathroom Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "60",
    },
    {
        "ID": 36,
        "fkStandardID": 3,
        "ScoringPath": "2012 Basement  Remodel",
        "ScoringPathAlias": "2012 Basement  Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "70",
    },
    {
        "ID": 37,
        "fkStandardID": 3,
        "ScoringPath": "2012 Small Addition",
        "ScoringPathAlias": "2012 Small Addition",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2012",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "80",
    },
    {
        "ID": 38,
        "fkStandardID": 4,
        "ScoringPath": "2015 SF New Construction",
        "ScoringPathAlias": "2015 SF New Construction",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Buy",
        "ViewIndex": "10",
    },
    {
        "ID": 39,
        "fkStandardID": 4,
        "ScoringPath": "2015 MF New Construction",
        "ScoringPathAlias": "2015 MF New Construction",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Rent",
        "ViewIndex": "70",
    },
    {
        "ID": 40,
        "fkStandardID": 4,
        "ScoringPath": "2015 SF Whole House Remodel",
        "ScoringPathAlias": "2015 SF Whole House Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "20",
    },
    {
        "ID": 41,
        "fkStandardID": 4,
        "ScoringPath": "2015 MF Remodel Building",
        "ScoringPathAlias": "2015 MF Remodel Building",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "80",
    },
    {
        "ID": 42,
        "fkStandardID": 4,
        "ScoringPath": "2015 Green Subdivision",
        "ScoringPathAlias": "2015 Green Subdivision",
        "ProjectType": "GS",
        "FindABuilderTabIndex": "3",
        "GCPStandardYear": "2015",
        "ViewIndex": "110",
    },
    {
        "ID": 43,
        "fkStandardID": 4,
        "ScoringPath": "2015 SF Kitchen Remodel",
        "ScoringPathAlias": "2015 SF Kitchen Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "30",
    },
    {
        "ID": 44,
        "fkStandardID": 4,
        "ScoringPath": "2015 SF Bathroom Remodel",
        "ScoringPathAlias": "2015 SF Bathroom Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "40",
    },
    {
        "ID": 45,
        "fkStandardID": 4,
        "ScoringPath": "2015 SF Basement Remodel",
        "ScoringPathAlias": "2015 SF Basement Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "50",
    },
    {
        "ID": 46,
        "fkStandardID": 4,
        "ScoringPath": "2015 SF Small Addition",
        "ScoringPathAlias": "2015 SF Small Addition",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "2",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "60",
    },
    {
        "ID": 47,
        "fkStandardID": 4,
        "ScoringPath": "2015 MF Kitchen Remodel",
        "ScoringPathAlias": "2015 MF Kitchen Remodel",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "90",
    },
    {
        "ID": 48,
        "fkStandardID": 4,
        "ScoringPath": "2015 MF Bathroom Remodel",
        "ScoringPathAlias": "2015 MF Bathroom Remodel",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2015",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "100",
    },
    {
        "ID": 49,
        "fkStandardID": 5,
        "ScoringPath": "2020 SF New Construction",
        "ScoringPathAlias": "2020 SF New Construction",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2020",
        "NGBSdotCom": "Buy",
        "ViewIndex": "10",
    },
    {
        "ID": 50,
        "fkStandardID": 5,
        "ScoringPath": "2020 MF New Construction",
        "ScoringPathAlias": "2020 MF New Construction",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2020",
        "NGBSdotCom": "Rent",
        "ViewIndex": "20",
    },
    {
        "ID": 51,
        "fkStandardID": 5,
        "ScoringPath": "2020 SF Whole House Remodel",
        "ScoringPathAlias": "2020 SF Whole House Remodel",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2020",
        "NGBSdotCom": "Remodel",
        "ViewIndex": "30",
    },
    {
        "ID": 52,
        "fkStandardID": 5,
        "ScoringPath": "2020 MF Remodel Building",
        "ScoringPathAlias": "2020 MF Remodel Building",
        "ProjectType": "MF",
        "FindABuilderTabIndex": "1",
        "GCPStandardYear": "2020",
        "NGBSdotCom": "Rent",
        "ViewIndex": "40",
    },
    {
        "ID": 53,
        "fkStandardID": 5,
        "ScoringPath": "2020 SF Certified Path",
        "ScoringPathAlias": "2020 SF Certified Path",
        "ProjectType": "SF",
        "FindABuilderTabIndex": "0",
        "GCPStandardYear": "2020",
        "NGBSdotCom": "Buy",
        "ViewIndex": "70",
    },
    {
        "ID": 54,
        "fkStandardID": 5,
        "ScoringPath": "2020 Green Subdivision",
        "ScoringPathAlias": "2020 Green Subdivision",
        "ProjectType": "GS",
        "FindABuilderTabIndex": "3",
        "GCPStandardYear": "2020",
        "ViewIndex": "80",
    },
]
