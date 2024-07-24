"""admin.py: """


# from axis.customer_hirl.models import VerifierAgreement, ProvidedService
# from django.contrib import admin
# from django.contrib.admin.decorators import register
#
__author__ = "Artem Hruzd"
__date__ = "04/20/2020 15:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

# __all__ = ['VerifierAgreementAdmin', ]
#
#
# @register(VerifierAgreement)
# class VerifierAgreementAdmin(admin.ModelAdmin):
#     raw_id_fields = ('mailing_geocode',
#                      'shipping_geocode',
#                      'verifier_signed_agreement',
#                      'verifier_certifying_document',
#                      'officer_signed_agreement',
#                      'officer_certifying_document',
#                      'hirl_signed_agreement',
#                      'hirl_certifying_document',
#                      'owner',
#                      'verifier')
#     filter_horizontal = ('provided_services', )
#     list_display = ('verifier', )
#     readonly_fields = ('verifier', )
#     search_fields = ('verifier__first_name',
#                      'verifier__last_name',
#                      'verifier__email',)
#
#
# @register(ProvidedService)
# class ProvidedServiceAdmin(admin.ModelAdmin):
#     pass
