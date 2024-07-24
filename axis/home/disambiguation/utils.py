"""Support utils."""


import logging
import re
import sys
import traceback

from django.apps import apps
from django.db import transaction
from unidecode import unidecode

from axis.geographic.utils.city import resolve_city
from axis.geographic.utils.legacy import do_blind_geocode

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)
app = apps.get_app_config("home")

ADDRESS_PROFILE_THRESHOLD = 400
ADDRESS_LEVENSHTEIN_THRESHOLD = 6

# NOTE: Any company listed here should be related to HIRL, and HIRL should be related to them.
# This ensures that the set of NGBS programs are visible to the companies in this list, allowing
# them to properly discover the relevant homes.
AUTOMATIC_HOME_RELATIONSHIPS = [
    # list of company slugs
    "neea",
    # 'general-ncbpa-general',  # Not using 'buildingnc' because HIRL is same company_type
]

ADDRESS_SUFFIX_SIMPLIFICATIONS = {
    "ALY": ["ALLEE", "ALLEY", "ALLY", "ALY"],
    "ANX": ["ANEX", "ANNEX", "ANNX", "ANX"],
    "ARC": ["ARC", "ARCADE"],
    "AVE": ["AV", "AVE", "AVEN", "AVENU", "AVENUE", "AVN", "AVNUE"],
    "BCH": ["BCH", "BEACH"],
    "BG": ["BURG"],
    "BGS": ["BURGS"],
    "BLF": ["BLF", "BLUF", "BLUFF"],
    "BLFS": ["BLUFFS"],
    "BLVD": ["BLVD", "BOUL", "BOULEVARD", "BOULV"],
    "BND": ["BEND", "BND"],
    "BR": ["BR", "BRNCH", "BRANCH"],
    "BRG": ["BRDGE", "BRG", "BRIDGE"],
    "BRK": ["BRK", "BROOK"],
    "BRKS": ["BROOKS"],
    "BTM": ["BOT", "BTM", "BOTTM", "BOTTOM"],
    "BYP": ["BYP", "BYPA", "BYPAS", "BYPASS", "BYPS"],
    "BYU": ["BAYOO", "BAYOU"],
    "CIR": ["CIR", "CIRC", "CIRCL", "CIRCLE", "CRCL", "CRCLE"],
    "CIRS": ["CIRCLES"],
    "CLB": ["CLB", "CLUB"],
    "CLF": ["CLF", "CLIFF"],
    "CLFS": ["CLFS", "CLIFFS"],
    "CMN": ["COMMON"],
    "CMNS": ["COMMONS"],
    "COR": ["COR", "CORNER"],
    "CORS": ["CORNERS", "CORS"],
    "CP": ["CAMP", "CP", "CMP"],
    "CPE": ["CAPE", "CPE"],
    "CRES": ["CRESCENT", "CRES", "CRSENT", "CRSNT"],
    "CRK": ["CREEK", "CRK"],
    "CRSE": ["COURSE", "CRSE"],
    "CRST": ["CREST"],
    "CSWY": ["CAUSEWAY", "CAUSWA", "CSWY"],
    "CT": ["COURT", "CT"],
    "CTR": ["CEN", "CENT", "CENTER", "CENTR", "CENTRE", "CNTER", "CNTR", "CTR"],
    "CTRS": ["CENTERS"],
    "CTS": ["COURTS", "CTS"],
    "CURV": ["CURVE"],
    "CV": ["COVE", "CV"],
    "CVS": ["COVES"],
    "CYN": ["CANYN", "CANYON", "CNYN"],
    "DL": ["DALE", "DL"],
    "DM": ["DAM", "DM"],
    "DR": ["DR", "DRIV", "DRIVE", "DRV"],
    "DRS": ["DRIVES"],
    "DV": ["DIV", "DIVIDE", "DV", "DVD"],
    "EST": ["EST", "ESTATE"],
    "ESTS": ["ESTATES", "ESTS"],
    "EXPY": ["EXP", "EXPR", "EXPRESS", "EXPRESSWAY", "EXPW", "EXPY"],
    "EXT": ["EXT", "EXTENSION", "EXTN", "EXTNSN"],
    "EXTS": ["EXTS"],
    "FALL": ["FALL"],
    "FLD": ["FIELD", "FLD"],
    "FLDS": ["FIELDS", "FLDS"],
    "FLS": ["FALLS", "FLS"],
    "FLT": ["FLAT", "FLT"],
    "FLTS": ["FLATS", "FLTS"],
    "FRD": ["FORD", "FRD"],
    "FRDS": ["FORDS"],
    "FRG": ["FORG", "FORGE", "FRG"],
    "FRGS": ["FORGES"],
    "FRK": ["FORK", "FRK"],
    "FRKS": ["FORKS", "FRKS"],
    "FRST": ["FOREST", "FORESTS", "FRST"],
    "FRY": ["FERRY", "FRRY", "FRY"],
    "FT": ["FORT", "FRT", "FT"],
    "FWY": ["FREEWAY", "FREEWY", "FRWAY", "FRWY", "FWY"],
    "GDN": ["GARDEN", "GARDN", "GRDEN", "GRDN"],
    "GDNS": ["GARDENS", "GDNS", "GRDNS"],
    "GLN": ["GLEN", "GLN"],
    "GLNS": ["GLENS"],
    "GRN": ["GREEN", "GRN"],
    "GRNS": ["GREENS"],
    "GRV": ["GROV", "GROVE", "GRV"],
    "GRVS": ["GROVES"],
    "GTWY": ["GATEWAY", "GATEWY", "GATWAY", "GTWAY", "GTWY"],
    "HBR": ["HARB", "HARBOR", "HARBR", "HBR", "HRBOR"],
    "HBRS": ["HARBORS"],
    "HL": ["HILL", "HL"],
    "HLS": ["HILLS", "HLS"],
    "HOLW": ["HLLW", "HOLLOW", "HOLLOWS", "HOLW", "HOLWS"],
    "HTS": ["HT", "HTS"],
    "HVN": ["HAVEN", "HVN"],
    "HWY": ["HIGHWAY", "HIGHWY", "HIWAY", "HIWY", "HWAY", "HWY"],
    "INLT": ["INLT"],
    "IS": ["IS", "ISLAND", "ISLND"],
    "ISLE": ["ISLE", "ISLES"],
    "ISS": ["ISLANDS", "ISLNDS", "ISS"],
    "JCT": ["JCT", "JCTION", "JCTN", "JUNCTION", "JUNCTN", "JUNCTON"],
    "JCTS": ["JCTNS", "JCTS", "JUNCTIONS"],
    "KNL": ["KNL", "KNOL", "KNOLL"],
    "KNLS": ["KNLS", "KNOLLS"],
    "KY": ["KEY", "KY"],
    "KYS": ["KEYS", "KYS"],
    "LAND": ["LAND"],
    "LCK": ["LCK", "LOCK"],
    "LCKS": ["LCKS", "LOCKS"],
    "LDG": ["LDG", "LDGE", "LODG", "LODGE"],
    "LF": ["LF", "LOAF"],
    "LGT": ["LGT", "LIGHT"],
    "LGTS": ["LIGHTS"],
    "LK": ["LK", "LAKE"],
    "LKS": ["LKS", "LAKES"],
    "LN": ["LANE", "LN"],
    "LNDG": ["LANDING", "LNDG", "LNDNG"],
    "LOOP": ["LOOP", "LOOPS"],
    "MALL": ["MALL"],
    "MDW": ["MEADOW"],
    "MDWS": ["MDW", "MDWS", "MEADOWS", "MEDOWS"],
    "MEWS": ["MEWS"],
    "ML": ["MILL"],
    "MLS": ["MILLS"],
    "MNR": ["MNR", "MANOR"],
    "MNRS": ["MANORS", "MNRS"],
    "MSN": ["MISSN", "MSSN"],
    "MT": ["MNT", "MT", "MOUNT"],
    "MTN": ["MNTAIN", "MNTN", "MOUNTAIN", "MOUNTIN", "MTIN", "MTN"],
    "MTNS": ["MNTNS", "MOUNTAINS"],
    "MTWY": ["MOTORWAY"],
    "NCK": ["NCK", "NECK"],
    "OPAS": ["OVERPASS"],
    "ORCH": ["ORCH", "ORCHARD", "ORCHRD"],
    "OVAL": ["OVAL", "OVL"],
    "PARK": ["PARK", "PRK", "PARKS"],
    "PASS": ["PASS"],
    "PATH": ["PATH", "PATHS"],
    "PIKE": ["PIKE", "PIKES"],
    "PKWY": ["PARKWAY", "PARKWY", "PKWAY", "PKWY", "PKY", "PARKWAYS", "PKWYS"],
    "PL": ["PL"] + ["PLACE"],  # 'place' as 'pl' is a thing we see
    "PLN": ["PLAIN", "PLN"],
    "PLNS": ["PLAINS", "PLNS"],
    "PLZ": ["PLAZA", "PLZ", "PLZA"],
    "PNE": ["PINE"],
    "PNES": ["PINES", "PNES"],
    "PR": ["PR", "PRAIRIE", "PRR"],
    "PRT": ["PORT", "PRT"],
    "PRTS": ["PORTS", "PRTS"],
    "PSGE": ["PASSAGE"],
    "PT": ["POINT", "PT"],
    "PTS": ["POINTS", "PTS"],
    "RADL": ["RAD", "RADIAL", "RADIEL", "RADL"],
    "RAMP": ["RAMP"],
    "RD": ["RD", "ROAD"],
    "RDG": ["RDG", "RDGE", "RIDGE"],
    "RDGS": ["RDGS", "RIDGES"],
    "RDS": ["ROADS", "RDS"],
    "RIV": ["RIV", "RIVER", "RVR", "RIVR"],
    "RNCH": ["RANCH", "RANCHES", "RNCH", "RNCHS"],
    "ROW": ["ROW"],
    "RPD": ["RAPID", "RPD"],
    "RPDS": ["RAPIDS", "RPDS"],
    "RST": ["REST", "RST"],
    "RTE": ["ROUTE"],
    "RUE": ["RUE"],
    "RUN": ["RUN"],
    "SHL": ["SHL", "SHOAL"],
    "SHLS": ["SHLS", "SHOALS"],
    "SHR": ["SHOAR", "SHORE", "SHR"],
    "SHRS": ["SHOARS", "SHORES", "SHRS"],
    "SKWY": ["SKYWAY"],
    "SMT": ["SMT", "SUMIT", "SUMITT", "SUMMIT"],
    "SPG": ["SPG", "SPNG", "SPRING", "SPRNG"],
    "SPGS": ["SPGS", "SPNGS", "SPRINGS", "SPRNGS"],
    "SPUR": ["SPUR", "SPURS"],
    "SQ": ["SQ", "SQR", "SQRE", "SQU", "SQUARE"],
    "SQS": ["SQRS", "SQUARES"],
    "ST": ["STREET", "STRT", "ST", "STR"],
    "STA": ["STA", "STATION", "STATN", "STN"],
    "STRA": ["STRA", "STRAV", "STRAVEN", "STRAVENUE", "STRAVN", "STRVN", "STRVNUE"],
    "STRM": ["STREAM", "STREME", "STRM"],
    "STS": ["STREETS"],
    "TER": ["TER", "TERR", "TERRACE"],
    "TPKE": ["TRNPK", "TURNPIKE", "TURNPK"],
    "TRAK": ["TRACK", "TRACKS", "TRAK", "TRK", "TRKS"],
    "TRCE": ["TRACE", "TRACES", "TRCE"],
    "TRFY": ["TRAFFICWAY"],
    "TRL": ["TRAIL", "TRAILS", "TRL", "TRLS"],
    "TRLR": ["TRAILER", "TRLR", "TRLRS"],
    "TRWY": ["THROUGHWAY"],
    "TUNL": ["TUNEL", "TUNL", "TUNLS", "TUNNEL", "TUNNELS", "TUNNL"],
    "UN": ["UN", "UNION"],
    "UNS": ["UNIONS"],
    "UPAS": ["UNDERPASS"],
    "VIA": ["VDCT", "VIA", "VIADCT", "VIADUCT"],
    "VIS": ["VIS", "VIST", "VISTA", "VST", "VSTA"],
    "VL": ["VILLE", "VL"],
    "VLG": ["VILL", "VILLAG", "VILLAGE", "VILLG", "VILLIAGE", "VLG"],
    "VLGS": ["VILLAGES", "VLGS"],
    "VLY": ["VALLEY", "VALLY", "VLLY", "VLY"],
    "VLYS": ["VALLEYS", "VLYS"],
    "VW": ["VIEW", "VW"],
    "VWS": ["VIEWS", "VWS"],
    "WALK": ["WALK", "WALKS"],
    "WALL": ["WALL"],
    "WAY": ["WY", "WAY"],
    "WAYS": ["WAYS"],
    "WL": ["WELL"],
    "WLS": ["WELLS", "WLS"],
    "XING": ["CROSSING", "CRSSNG", "XING"],
    "XRD": ["CROSSROAD"],
    "XRDS": ["CROSSROADS"],
}

# {k1: [v1, v2], k2: [v3]} => {v1: k1, v2: k1, v3: k2}
ADDRESS_SUFFIX_LOOKUPS = {
    value.lower(): key.lower()
    for key, items in ADDRESS_SUFFIX_SIMPLIFICATIONS.items()
    for value in items
}
RE_ADDRESS_SUFFIXES = re.compile(
    r"\b({})\b".format("|".join(ADDRESS_SUFFIX_LOOKUPS.keys()).lower())
)
ADDRESS_DIRECTION_LOOKUPS = {
    "north": "n",
    "south": "s",
    "east": "e",
    "west": "w",
    "northwest": "nw",
    "northeast": "ne",
    "southwest": "sw",
    "southeast": "se",
}
RE_DIRECTIONS = re.compile(r"\b({})\b".format("|".join(ADDRESS_DIRECTION_LOOKUPS.keys())))


def import_certification(certification, **kwargs):
    """Calls `find_axis_home()` then `ensure_axis_home()` on the certification object.

    A traceback is saved on the certification's `import_traceback` field."""

    log = kwargs.get("log", logging.getLogger(__name__))

    # if certification.home:
    #     log.info('Certification already imported, no changes will be made: %r', certification)
    #     return

    home = certification.find_axis_home()
    if certification.home:
        log.warning("Home already resolved: %r", certification.home)
        return
    if home is False:
        log.warning(
            "Multiple candidates, not associating an Axis home (%s): %r",
            certification.id,
            certification,
        )
        return

    try:
        home = certification.ensure_axis_home(home=home)
    except Exception as exception:  # pylint: disable=broad-except
        log.exception("Unable to generate a new Axis home: %r", certification)
        certification.home = None
        certification.import_failed = True
        certification.import_error = "{}".format(exception)
        certification.import_traceback = "".join(traceback.format_tb(sys.exc_info()[-1]))
        certification.save()


def generate_home_data(obj, rater_org, home=None, builder_org=None, subdivision=None):  # noqa: C901
    """
    Takes a Certification model instance and tries to turn it into a Home instance.  If the home
    already exists, then this will make sure the an HIRL homestatus is created on it.
    An error will be raised if the data is incomplete or needs special attention.
    """

    # This is designed to be safe to call multiple times on a Certification instance.

    # NOTE: We expect exceptions to be raised here if something goes wrong.  Handling is done by
    # the caller.

    from axis.eep_program.models import EEPProgram
    from axis.home.models import Home, EEPProgramHomeStatus
    from axis.annotation.models import Annotation
    from axis.relationship.utils import create_or_update_spanning_relationships
    from django.contrib.contenttypes.models import ContentType
    from axis.customer_hirl.models import HIRLRaterUser

    customer_hirl_app = apps.get_app_config("customer_hirl")
    company = rater_org

    slug = None
    if hasattr(obj, "PROGRAM_NAMES"):
        try:
            name = obj.PROGRAM_NAMES[getattr(obj, obj.PROGRAM_NAME)]
        except AttributeError:
            name = obj.PROGRAM_NAMES[obj.PROGRAM_NAME]
        eep_program = EEPProgram.objects.get(name=name)
    elif hasattr(obj, "scoring_path"):
        slug = customer_hirl_app.NGBS_PROGRAM_NAMES[obj.scoring_path]
        eep_program = EEPProgram.objects.get(slug=slug)
    ct_homestatus = ContentType.objects.get_for_model(EEPProgramHomeStatus)
    city = resolve_city(
        name=getattr(obj, "city"),
        county=getattr(obj, "county"),
        state_abbreviation=getattr(obj, "state_abbreviation"),
        country=getattr(obj, "country", "US"),
    )
    if not builder_org and hasattr(obj, "builder"):
        builder_org = obj.find_axis_builder()
    if not subdivision and hasattr(obj, "community_project"):
        subdivision = obj.find_axis_subdivision()

    verifier_company = None
    if hasattr(obj, "verifier_id"):
        hirl_internal_rater_user = HIRLRaterUser.objects.filter(hirl_id=obj.verifier_id).first()

        if hirl_internal_rater_user:
            verifier_company = hirl_internal_rater_user.user.company

    # Checks for data compatibility when giving explicit object to usum_itemse
    if (builder_org and subdivision) and (builder_org.id != subdivision.builder_org.id):
        # log.error('Builder mismatch for specified subdivision: %r', home)
        raise ValueError("Builder mismatch for specified subdivision.")
    if home:
        existing_builder_org = home.get_company_by_type("builder")
        if (existing_builder_org and builder_org) and (existing_builder_org.id != builder_org.id):
            # Even if the desired builder_org is None at this point (i.e., can't be discovered as
            # an existing Company), we still want to flag this as a problem, because it implies that
            # the method is going to create a new builder company while the one we would expect it
            # to have found is already assigned.  We won't put a second builder on the home.
            # log.error('Builder mismatch for existing builder relationship on home: %r', home)
            raise ValueError("Builder mismatch for existing builder relationship on home.")

        if (subdivision and home.subdivision) and (subdivision != home.subdivision):
            # As with the builder above, if subdivision is None it implies we're about to create a
            # new one when the real issue is that the discovery phase didn't find what Axis would
            # expect.
            # log.error('Subdivision mismatch for specified home: %r', home)
            raise ValueError("Subdivision mismatch for specified home.")

    home = home or obj.home
    with transaction.atomic():
        # Finalize related objects
        if not builder_org:
            builder_org = obj.ensure_axis_builder()
        if not subdivision:
            subdivision = obj.ensure_axis_subdivision()

        # Consolidate final data fields
        home_data = {
            "subdivision": subdivision,
            "street_line1": obj.street_line1,
            "city": city,
            "zipcode": obj.zipcode,
            "is_multi_family": obj.get_is_multifamily(),
        }
        relationships = [x for x in [company, builder_org, eep_program.owner] if x is not None]
        if verifier_company:
            relationships.append(verifier_company)
        home_status_data = {
            "eep_program": eep_program,
            "company": eep_program.owner,
            "state": "complete",
        }
        home_status_data_defaults = {
            "certification_date": obj.certification_date,
        }
        annotation_data = obj.get_annotation_data()

        log.info(
            "Writing and updating... program: %s, annotations: %d, relationships: %s",
            eep_program.slug,
            len(annotation_data),
            ", ".join([c.slug for c in relationships]),
        )

        if not home:
            home = Home(**home_data)
            home.save()
            do_blind_geocode(home, **home_data)
            # log.warning('New home created: id=%s %r', home.id, home)
        else:
            pass
            # log.info('♻️ id=%s %r', home.id, home)
        obj.home = home

        create_or_update_spanning_relationships(relationships, home)

        home_status, _ = home.homestatuses.get_or_create(
            defaults=home_status_data_defaults, **home_status_data
        )

        if annotation_data:
            log.info("Adding %d annotations", len(annotation_data))
        for annotation_type, content in annotation_data.items():
            if content is None:
                continue
            Annotation.objects.get_or_create(
                **{
                    "type": annotation_type,
                    "content": content,
                    "content_type": ct_homestatus,
                    "object_id": home_status.id,
                }
            )

        # We want to create an association to this competing company
        if company.company_type == home_status.eep_program.owner.company_type:
            if company.id != home_status.eep_program.owner.id:
                associate_companies_by_county(obj, company)

        obj.import_failed = False
        obj.import_error = None
        obj.import_traceback = None
        obj.save()

    return home


# NOTE: This should be promoted to a home utility if we are going to commit to this strategy
def profile_address(street_line1):
    """
    Create a value which simplifies a string to something queryable for fuzzy matches.  In practice,
    we're reducing the address to the sum of its parts, where string length increases the score more
    dramatically than the value of the individual characters.
    """

    # This is an imperfect method of arriving at a 'profile' value, but it yields results that can
    # be fuzzy-queried with ease directly from the database.  The prime benefit of this general
    # approach is that the profile value is independent of any context, so it can be used in
    # comparisons with any other address, and can therefore be stored for repeated use.  By
    # contrast, a levenshtein score is only valuable in the context of a specific comparison, and so
    # cannot be stored for arbitrary other comparisons.

    # Remove noise in the string that could be omitted in user strings and meant to be equivalent.
    # In this case, we aim to reduce curled quotes, odd spaces, and character accents to their
    # simpler versions, rather than have them stripped from the string altogether.
    street_line1 = unidecode(street_line1)

    # Sum the character values.
    # TODO: Possibly organize the alphabet in our own scoring list rather than its ord value.
    # We would be able to tune it to condense the number space (remove the built-in ord offset, etc)
    profile = sum(map(ord, street_line1.lower()))

    return profile


def is_within_profile_threshold(profile1, profile2, threshold=ADDRESS_PROFILE_THRESHOLD):
    """Return True if `profile1` is with +/-`threshold` from `profile2`."""

    return (profile2 - threshold) < profile1 < (profile2 + threshold)


def is_within_levenshtein_threshold(address1, address2, threshold=ADDRESS_LEVENSHTEIN_THRESHOLD):
    """Return True if the transformations required from `address1` to `address2` is
    less than or equal to integer `threshold`.
    """

    return get_levenshtein_distance(address1, address2) <= threshold


def normalize_address(street_line1):
    """Return lowercase `street_line1` with postal system street suffixes and compass directions
    normalized for comparisons to other equivalent addresses.
    """

    def _rep_suffix(match):
        return ADDRESS_SUFFIX_LOOKUPS[match.group(1)]

    def _rep_direction(match):
        return ADDRESS_DIRECTION_LOOKUPS[match.group(1)]

    s = street_line1.lower()
    s = RE_ADDRESS_SUFFIXES.sub(_rep_suffix, s)
    s = RE_DIRECTIONS.sub(_rep_direction, s)
    return s


def get_levenshtein_distance(s1, s2):
    """Computes a difference score for how many mutations it takes to get from s1 to s2."""
    if len(s1) < len(s2):
        s2, s1 = s1, s2
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def associate_companies_by_county(obj, *companies):
    """Publish shared access via Association to Certification `obj`'s.
    When no companies are passed as `*args`, the company list becomes the set of companies
    operating in `obj.home`'s county.
    """

    from axis.relationship.utils import associate_companies_to_obj

    home = obj.home
    if not home:
        raise ValueError(
            "Certification instance is not related to an Axis home, can't be associated: %r"
            % (obj,)
        )
    if not companies:
        raise ValueError("At least one company is required.")

    if hasattr(obj, "PROGRAM_NAMES"):
        homestatus = home.homestatuses.filter(
            eep_program__name__in=obj.PROGRAM_NAMES.values()
        ).first()
    else:
        homestatus = home.homestatuses.filter(eep_program__name__in=obj.PROGRAMS.values()).first()

    if not homestatus:
        raise ValueError(
            "HIRL instance does not have an NGBS program (not correctly imported?): %r" % (obj,)
        )

    try:
        owner = app.get_customer_company()
    except AttributeError:
        owner = homestatus.eep_program.owner

    associate_companies_to_obj(homestatus, owner, *companies)
