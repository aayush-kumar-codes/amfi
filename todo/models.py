from django.db import models
from django.db.models import Q

from rest_framework import serializers

import todo.util

import datetime
import re
from math import ceil


class MFDownload(models.Model):
    amc_id = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=True)
    retry = models.IntegerField(null=False, default=0)
    has_data = models.BooleanField(null=False, default=True)

# https://medium.com/@MicroPyramid/django-model-managers-and-properties-564ef668a04c


class AMCManager(models.Manager):
    def match_amc_with_short_name(self, short_name):
        amcs = self.filter(name__icontains=short_name)
        if amcs.count() > 0:
            return amcs.first()
        else:
            return False
    pass


class AMC(models.Model):
    name = models.CharField(max_length=255, unique=True)
    amc_no = models.IntegerField(null=False, unique=True)
    parsed = models.BooleanField(null=False, default=False)
    next_amc_no = models.IntegerField(null=False, default=0)

    objects = AMCManager()


class SchemeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(scheme_category='Open Ended Schemes')
        # for now working with open ended schems only

    def get_actual_scheme_names_for_amc(self, amc):
        pass


class Scheme(models.Model):
    amc = models.ForeignKey(
        'AMC',
        on_delete=models.CASCADE,
    )
    # this is mainly for open ended or close ended
    scheme_category = models.CharField(max_length=255, null=False)
    # this is for equity debt etc
    scheme_type = models.CharField(max_length=255, null=False)
    # this is for type i.e mid cap, large cap etc
    scheme_sub_type = models.CharField(max_length=255, null=False)
    fund_code = models.CharField(
        max_length=255, null=False, unique=True)  # amfi code
    fund_name = models.CharField(max_length=255, null=False)  # name
    fund_option = models.CharField(
        max_length=255, null=False)  # grown or what kind
    fund_type = models.CharField(
        max_length=255, null=False)  # direct or regular
    object = SchemeManager

    def get_category_types(self):
        return ["Equity", "Debt", "Hybrid", "Others", "Solution"]

    def get_clean_name(self):
        name = getattr(self, "fund_name")
        name = re.sub("[\(\[].*?[\)\]]", "", name)
        name = name.replace("Direct", "")
        name = name.replace("Growth", "")
        name = name.replace("Plan", "")
        name = name.strip()
        return name
    # clean_name = property(get_clean_name)

    def is_closed_ended(self):
        s_cat = getattr(self, "scheme_category")
        if s_cat.contains("Closed"):
            return True

        return False

    def is_open_ended(self):
        s_cat = getattr(self, "scheme_category")
        if "Open" in s_cat:
            return True

        return False

    def is_debt(self):
        s_type = getattr(self, "scheme_type")
        if "Debt" in s_type:
            return True

        return False

    def is_equity(self):
        s_type = getattr(self, "scheme_type")
        if "Equity" in s_type:
            return True

        return False

    def is_index(self):
        s_type = getattr(self, "scheme_type")
        s_sub_type = getattr(self, "scheme_sub_type")

        if "Index" in s_sub_type:
            return True

        return False

    def previous_yr_abs(self, years=1, start_year=0):
        # years how many years to go back
        # start_year which year to start from
        # abs weather absolute return or annulized return

        # this is for calcuation's with basement reference of any year but 1st and last of year
        end_date = datetime.date(datetime.date.today(
        ).year - start_year, 1, 1) - datetime.timedelta(days=1)
        # 1 DAY BECAUSE we need to find the date 31 dec instead of 1jan of the previous

        start_date = end_date - datetime.timedelta(days=365*years)

        ret = self.abs_return(start_date, end_date)
        if years > 1:
            cagr = todo.util.cagr(
                ret["start_nav"], ret["end_nav"], years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)

        return ret

    def previous_yr_abs_today(self, years=1, offset_days=0):
        # how many years to go back
        # offset in days, if start from today or few days back
        # abs weather absolute return or annulized return

        # this has all caculate with base reference as today
        end_date = datetime.date.today() - datetime.timedelta(days=offset_days)
        start_date = end_date - datetime.timedelta(days=365*years)

        ret = self.abs_return(start_date, end_date)

        if years > 1:
            cagr = todo.util.cagr(
                ret["start_nav"], ret["end_nav"], years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)

        return ret

    def ytd_abs(self):
        end_date = datetime.date.today()
        start_date = datetime.date(datetime.date.today().year, 1, 1)

        return self.abs_return(start_date, end_date)

    def abs_return(self, start_date, end_date):
        start_nav = Nav.get_nav_for_date(self, start_date)
        end_nav = Nav.get_nav_for_date(self, end_date)

        pct = (end_nav - start_nav) / (start_nav)

        return {
            "start_nav": start_nav,
            "start_date": start_date,
            "end_nav": end_nav,
            "end_date": end_date,
            "pct": todo.util.float_round(pct*100, 2, ceil)
        }

    class Meta:
        unique_together = ("amc", "fund_code")


class Nav(models.Model):
    scheme = models.ForeignKey(
        'Scheme',
        on_delete=models.CASCADE,
    )
    nav = models.FloatField(null=False)
    date = models.DateField(null=False)

    class Meta:
        unique_together = ("scheme", "date")

    @staticmethod
    def get_nav_for_date(scheme, date):
        # this function will get nav for date and will interpolate if nav doesn't exist
        try:
            navs = Nav.objects.get(scheme=scheme, date=date)
            start_nav = navs.nav
            # data exists problem solved
        except Nav.DoesNotExist:
            # data doesn't exist. we need to find nearest set of data's and interpolate based on it
            print("nav doesn't existing will intrapolate")

            date_delta_end = date - datetime.timedelta(days=3)
            date_delta_start = date + datetime.timedelta(days=3)
            f = Q(date__gt=date_delta_end) & Q(
                date__lt=date_delta_start) & Q(scheme=scheme)

            navs = Nav.objects.filter(f)
            if navs.count() > 0:
                ser = NavSerializer(navs, many=True)
                df = todo.util.get_date_index_data(ser.data)
                print(df)

                start_date = date_delta_end
                end_date = date_delta_start

                df = todo.util.fill_date_frame_data(df, start_date, end_date)
                # print(df)
                start_nav = df.loc[date.strftime("%Y-%m-%d")]["nav"]
            else:
                raise ValueError(
                    "unable to get nav value at all, check your date", date)

        return start_nav


class NavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nav
        fields = '__all__'


class Index(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    parsed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "type")


class IndexData(models.Model):
    index = models.ForeignKey(
        'Index',
        on_delete=models.CASCADE
    )
    date = models.DateField(null=False)
    open = models.FloatField(null=False)
    close = models.FloatField(null=False)
    high = models.FloatField(null=False)
    low = models.FloatField(null=False)
    pe = models.FloatField(null=True)
    pb = models.FloatField(null=True)
    div = models.FloatField(null=True)
