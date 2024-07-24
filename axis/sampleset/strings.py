"""strings.py: Django sampleset"""


import logging

from django.conf import settings

__author__ = "Steven Klass"
__date__ = "7/21/14 9:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

HELP_TEXT_TEST_HOMES = """Homes contributing answers to the sample set."""
HELP_TEXT_SAMPLED_HOMES = """Homes receiving answers contributed via the test homes."""
HELP_TEXT_METRO_SAMPLED = """Toggles whether the sample set is forced to contain items only in the subdivision, or only in the larger metro area."""

SAMPLESET_FULL = "You cannot have more than {max_size} homes in a sampleset."

INVALID_GLOBAL = """{company} is globally restricted form sampling"""
INVALID_SAMPLING_COMPANY_TYPE = """Only raters and providers can sample"""
COMPANY_NOT_APPROVED_BY_PROVIDER = """{company} is has not been approved by provider {provider}"""
PROGRAM_DOES_NOT_ALLOW_SAMPLING = "{program} does not allow sampling"
PROGRAM_DOES_NOT_ALLOW_METRO_SAMPLING = "{program} does not allow metro sampling"
PROGRAM_RESNET_SAMPLING_PROVIDER = (
    "{program} requires an active RESNET sampling provider. {} is "
    "not active with RESENT or has not been linked in Axis"
)

ADVANCE_NOT_AVAILABLE = (
    """{sampleset} must contain a test home and must be free of outstanding failing answers."""
)
CERTIFICATION_NOT_AVAILABLE = (
    """{sampleset} must contain uncertified homes to be eligible for certification."""
)

# Sampleset builder UI messages received from API.
METRO_SAMPLING_UNSUPPORTED_BY_PROGRAM = (
    "The program {program} does not allow metro sampling, but "
    "the provided homes use more than one subdivision."
)
METRO_SAMPLING_IN_USE = "This sample set uses metro sampling."
MISMATCHED_PROGRAMS = "Multiple programs in use."
MISMATCHED_BUILDERS = "Sample set uses more than one builder."
MISMATCHED_METROS = "Multiple metro areas are represented."

MULTIPLE_METROS_IN_USE = """Multiple metro areas are represented in this sample set: {metros}"""
MISSING_SUBDIVISION = """Sampling requires a subdivision and one has not been specified."""
INCOMPATIBLE_BUILDER_ORG = (
    "The {home_builder} should match the sample set builder {sampleset_builder}"
)
INCOMPATIBLE_SUBDIVISION = """Sample set {sampleset} is attempting use metro Sampling.  Subdivision <a href="{url}" target="_blank">{subdivision}</a> does not allow metro sampling.  Make sure Metro sampling is enabled if applicable."""
MISMATCHED_METROS_SUBDIVISIONS = """Subdivision <a href="{url}" target="_blank">{subdivision}</a> identified metro "{metro}" does not align with sampleset identified metro "{ss_metro}"""

# Bulk uploader
SAMPLESET_UUID_CONFLICT = """The Sample Set name {sampleset} is already used by another company."""
FOUND_SAMPLESET = """Used existing sample set <a href="{url}">{sampleset}</a>"""
CREATED_SAMPLESET = """Created sampleset <a href="{url}">{sampleset}</a>"""
ONLY_SAMPLED_HOMES = """Sample Set '{sampleset}' has only sampled homes identified in this spreadsheet and no corresponding test homes in either this spreadsheet."""
ONLY_TEST_HOMES = """Sample Set '{sampleset}' has only test homes identified in this spreadsheet and no corresponding sampled homes in this spreadsheet."""
NO_SAMPLED_HOMES = """Sample Set '{sampleset}' does not have any sample homes."""
NO_TEST_HOMES = """Sample Set '{sampleset}' does not have any sample test homes. Sample Set cannot be certified until it contains a Sample Test Home."""
SAMPLESET_EXCEEDED_IF_CERTIFICATION_PROCESSES = (
    """Sample Set {sampleset} cannot be processed, more than %(SAMPLING_MAX_SIZE)s homes have been identified."""
    % {"SAMPLING_MAX_SIZE": settings.SAMPLING_MAX_SIZE}
)
CANNOT_MOVE_HOME_FROM_CERTIFIED_SAMPLESET = """Home is already in a confirmed sample set %(old_sampleset)r and cannot be moved to %(new_sampleset)r."""
