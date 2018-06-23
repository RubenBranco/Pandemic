from django.contrib import admin
from django_countries.filters import CountryFilter as BaseCountryFilter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from chat.models import Chat
from accounts.models import District, Municipality, UserProfile
from django.utils.encoding import force_text
from django.utils import timezone
from django.db import models
from game.models import Session, SessionState, PlayerState, CardState, CityState, CureState, DiseaseState
import datetime


class CountryFilter(BaseCountryFilter):

    def choices(self, changelist):
        value = self.used_parameters.get(self.field.name)
        yield {
            'selected': value is None,
            'query_string': changelist.get_query_string(
                {}, [self.field.name]),
            'display': ('All'),
        }
        for lookup, title in self.lookup_choices(changelist):
            yield {
                'selected': value == force_text(lookup),
                'query_string': changelist.get_query_string(
                    {"userprofile__country__exact": lookup}, []),
                'display': title,
            }

    def lookup_choices(self, changelist):
        qs = changelist.model._default_manager.all()
        codes = set(
            qs.distinct()
            .order_by("userprofile__{}".format(self.field.name))
            .values_list("userprofile__{}".format(self.field.name), flat=True))
        for k, v in self.field.get_choices(include_blank=False):
            if k in codes:
                yield k, v

class DobFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field_generic = '%s__' % field_path
        self.date_params = {k: v for k, v in params.items() if k.startswith(self.field_generic)}

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:       # field is a models.DateField
            today = now.date()
        
        nineteen_ten = today.replace(year=1910, month=1, day=1)
        nineteen_twenties = today.replace(year=1920, month=1, day=1)
        nineteen_thirties = today.replace(year=1930, month=1, day=1)
        nineteen_forties = today.replace(year=1940, month=1, day=1)
        nineteen_fifties = today.replace(year=1950, month=1, day=1)
        nineteen_sixties = today.replace(year=1960, month=1, day=1)
        nineteen_seventies = today.replace(year=1970, month=1, day=1)
        nineteen_eighties = today.replace(year=1980, month=1, day=1)
        nineteen_nineties = today.replace(year=1990, month=1, day=1)
        two_thousands = today.replace(year=2000, month=1, day=1)
        two_thousand_ten = today.replace(year=2010, month=1, day=1)
        two_thousand_twenty = today.replace(year=2020, month=1, day=1)

        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_until = '%s__lt' % field_path
        self.links = (
            (('Any date'), {}),
            (("1910's"), {
                self.lookup_kwarg_since: str(nineteen_ten),
                self.lookup_kwarg_until: str(nineteen_twenties),
            }),
            (("1920's"), {
                self.lookup_kwarg_since: str(nineteen_twenties),
                self.lookup_kwarg_until: str(nineteen_thirties),
            }),
            (("1930's"), {
                self.lookup_kwarg_since: str(nineteen_thirties),
                self.lookup_kwarg_until: str(nineteen_forties),
            }),
            (("1940's"), {
                self.lookup_kwarg_since: str(nineteen_forties),
                self.lookup_kwarg_until: str(nineteen_fifties),
            }),
            (("1950's"), {
                self.lookup_kwarg_since: str(nineteen_fifties),
                self.lookup_kwarg_until: str(nineteen_sixties),
            }),
            (("1960's"), {
                self.lookup_kwarg_since: str(nineteen_sixties),
                self.lookup_kwarg_until: str(nineteen_seventies),
            }),
            (("1970's"), {
                self.lookup_kwarg_since: str(nineteen_seventies),
                self.lookup_kwarg_until: str(nineteen_eighties),
            }),
            (("1980's"), {
                self.lookup_kwarg_since: str(nineteen_eighties),
                self.lookup_kwarg_until: str(nineteen_nineties),
            }),
            (("1990's"), {
                self.lookup_kwarg_since: str(nineteen_nineties),
                self.lookup_kwarg_until: str(two_thousands),
            }),
            (("2000's"), {
                self.lookup_kwarg_since: str(two_thousands),
                self.lookup_kwarg_until: str(two_thousand_ten),
            }),
            (("2010's"), {
                self.lookup_kwarg_since: str(two_thousand_ten),
                self.lookup_kwarg_until: str(two_thousand_twenty),
            })
        )
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = 'Date of Birth'

    def expected_parameters(self):
        params = [self.lookup_kwarg_since, self.lookup_kwarg_until]
        return params

    def choices(self, changelist):
        for title, param_dict in self.links:
            yield {
                'selected': self.date_params == param_dict,
                'query_string': changelist.get_query_string(param_dict, [self.field_generic]),
                'display': title,
    }

admin.FieldListFilter.register(lambda f: isinstance(f, models.DateField), DobFilter)

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class PlayerStateInline(admin.StackedInline):
    model = PlayerState
    can_delete = False
    verbose_name_plural = 'Player State'

class CardStateInline(admin.StackedInline):
    model = CardState
    can_delete = False
    verbose_name_plural = 'Card State'

class CityStateInline(admin.StackedInline):
    model = CityState
    can_delete = False
    verbose_name_plural = 'City State'

class CureStateInline(admin.StackedInline):
    model = CureState
    can_delete = False
    verbose_name_plural = 'Cure State'

class DiseaseStateInline(admin.StackedInline):
    model = DiseaseState
    can_delete = False
    verbose_name_plural = 'Disease State'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_filter = ('is_staff', 'is_superuser', 'is_active', ('userprofile__country', CountryFilter), 'userprofile__district', 'userprofile__county', ('userprofile__dob', DobFilter))

class SessionAdmin(admin.ModelAdmin):
    empty_value_display = '--empty--'
    list_filter = ('has_started',)
    search_fields = ('name', 'description', 'owner__username',)

class SessionStateAdmin(admin.ModelAdmin):
    inlines = (PlayerStateInline, CardStateInline, CityStateInline, CureStateInline, DiseaseStateInline)
    list_filter = ('has_ended',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Chat)
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Session, SessionAdmin)
admin.site.register(SessionState, SessionStateAdmin)

