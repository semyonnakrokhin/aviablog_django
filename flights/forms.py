from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import formset_factory

from .models import (Flight,
                     Airline,
                     AircraftType,
                     Airframe,
                     UserTrip,
                     Meal,
                     FlightInfo,
                     TrackImage)


class AircraftTypeForm(forms.Form):
    # existing_manufacturers = AircraftType.objects.values_list('manufacturer', flat=True)
    # existing_generic_types = AircraftType.objects.values_list('generic_type', flat=True)

    manufacturer = forms.CharField(widget=forms.TextInput(attrs={'list': 'manufacturer_choices'}))
    generic_type = forms.CharField(widget=forms.TextInput(attrs={'list': 'generic_type_choices'}))

    def save_aircraft_type(self):
        data_for_aircraft_type = {
            'manufacturer': self.cleaned_data['manufacturer'],
            'generic_type': self.cleaned_data['generic_type']
        }
        aircraft_type_instance, _ = AircraftType.objects.get_or_create(**data_for_aircraft_type)
        return aircraft_type_instance


class AirlineForm(forms.Form):
    # existing_airlines = Airline.objects.values_list('name', flat=True)

    name = forms.CharField(label='Airline name',
                           widget=forms.TextInput(attrs={'list': 'airline_choices'}))

    def save_airline(self):
        data_for_airline = {
            'name': self.cleaned_data['name']
        }
        airline_instance, _ = Airline.objects.get_or_create(**data_for_airline)
        return airline_instance


class AirframeForm(forms.Form):
    airframe_photo = forms.ImageField(label='Фото ВС', required=True)
    serial_number = forms.CharField(required=True)
    registration_number = forms.CharField(required=True)

    def save_airframe(self, aircraft_type: AircraftType, airline: Airline):
        data_for_airframe = {
            'serial_number': self.cleaned_data['serial_number'],
            'registration_number': self.cleaned_data['registration_number'],
            'photo': self.cleaned_data['airframe_photo'],
            'aircraft_type': aircraft_type,
            'airline': airline
        }
        airframe_instance, _ = Airframe.objects.get_or_create(**data_for_airframe)
        return airframe_instance


class FlightForm(forms.Form):
    flight_number = forms.CharField(required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    flight_time = forms.TimeField(required=False)

    def save_flight(self, airframe: Airframe):
        data_for_flight = {
            'flight_number': self.cleaned_data['flight_number'],
            'date': self.cleaned_data['date'],
            'flight_time': self.cleaned_data['flight_time'],
            'airframe': airframe
        }
        flight_instance, _ = Flight.objects.get_or_create(**data_for_flight)
        return flight_instance


class UserTripForm(forms.Form):
    ticket_price = forms.DecimalField(label='Цена билета', required=False)
    user = forms.ModelChoiceField(label='Пользователь', queryset=User.objects.all(), required=True)
    seat = forms.CharField(required=False)
    neighbors = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), required=False)
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': 70}), required=False)

    def save_user_trip(self, flight: Flight):
        data_for_user_trip = {
            'seat': self.cleaned_data['seat'],
            'neighbors': self.cleaned_data['neighbors'],
            'comments': self.cleaned_data['comments'],
            'price': self.cleaned_data['ticket_price'],
            'passenger': self.cleaned_data['user'],
            'flight': flight
        }
        user_trip_instance, _ = UserTrip.objects.get_or_create(**data_for_user_trip)
        return user_trip_instance


class MealForm(forms.Form):
    meal_price = forms.DecimalField(label='Цена питания', required=False)
    meal_photo = forms.ImageField(label='Фото питания', required=False)
    drinks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), initial='Вода')
    appertize = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), required=False)
    main_course = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 70}), required=False)
    desert = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), required=False)

    def save_meal(self, trip: UserTrip):
        data_for_meal = {
            'drinks': self.cleaned_data['drinks'],
            'appertize': self.cleaned_data['appertize'],
            'main_course': self.cleaned_data['main_course'],
            'desert': self.cleaned_data['desert'],
            'price': self.cleaned_data['meal_price'],
            'photo': self.cleaned_data['meal_photo'],
            'trip': trip
        }
        meal_instance, _ = Meal.objects.get_or_create(**data_for_meal)
        return meal_instance


# class FlightInfoForm(forms.Form):
#     status = forms.CharField()
#     airport_code = forms.CharField()
#     metar = forms.CharField()
#     gate = forms.CharField()
#     is_boarding_bridge = forms.BooleanField()
#     schedule_time = forms.TimeField()
#     actual_time = forms.TimeField()
#     runway = forms.CharField()
#
#     def add_prefix(self, field_name):
#         prefix = getattr(self, 'prefix', None)
#         if prefix:
#             return f"{prefix}_{field_name}"
#         return field_name
#
#     def save_flight_info(self, flight: Flight):
#         data_for_flight_info = {
#             'status': self.cleaned_data['status'],
#             'airport_code': self.cleaned_data['airport_code'],
#             'metar': self.cleaned_data['metar'],
#             'gate': self.cleaned_data['gate'],
#             'is_boarding_bridge': self.cleaned_data['is_boarding_bridge'],
#             'schedule_time': self.cleaned_data['schedule_time'],
#             'actual_time': self.cleaned_data['actual_time'],
#             'flight': flight
#         }
#         flight_info_instance, _ = FlightInfo.objects.get_or_create(**data_for_flight_info)
#         return flight_info_instance


# def add_prefix_to_fields(prefix):
#     def decorator(cls):
#         new_fields = {}
#         for field_name, field in cls.base_fields.items():
#             field_name_with_prefix = f"{prefix}_{field_name}"
#             new_fields[field_name_with_prefix] = field
#
#         cls.base_fields = new_fields
#         return cls
#     return decorator
#
#
# @add_prefix_to_fields('departure')
# class DepartureFlightInfoForm(FlightInfoForm, forms.Form):
#     pass

# 'class': 'form-control small-input'
class DepartureFlightInfoForm(forms.Form):
    departure_airport_code = forms.CharField(
        label='Airport IATA',
        widget=forms.TextInput(attrs={'placeholder': 'Departure airport'}),
        required=True
    )
    departure_metar = forms.CharField(label='METAR', required=False)
    departure_gate = forms.CharField(label='Gate', required=False)
    departure_is_boarding_bridge = forms.BooleanField(label='Through jet bridge?', required=False)
    departure_schedule_time = forms.TimeField(label='Schedule time', required=False)
    departure_actual_time = forms.TimeField(label='Actual time', required=False)
    departure_runway = forms.CharField(label='Active runway', required=True)

    def save_departure_flight_info(self, flight: Flight):
        data_for_flight_info = {
            'status': 'Departure',
            'airport_code': self.cleaned_data['departure_airport_code'],
            'metar': self.cleaned_data['departure_metar'],
            'gate': self.cleaned_data['departure_gate'],
            'is_boarding_bridge': self.cleaned_data['departure_is_boarding_bridge'],
            'schedule_time': self.cleaned_data['departure_schedule_time'],
            'actual_time': self.cleaned_data['departure_actual_time'],
            'runway': self.cleaned_data['departure_runway'],
            'flight': flight
        }
        flight_info_instance, _ = FlightInfo.objects.get_or_create(**data_for_flight_info)
        return flight_info_instance


class ArrivalFlightInfoForm(forms.Form):
    arrival_airport_code = forms.CharField(
        label='Airport IATA',
        widget=forms.TextInput(attrs={'placeholder': 'Arrival airport'}),
        required=True
    )
    arrival_metar = forms.CharField(label='METAR', required=False)
    arrival_gate = forms.CharField(label='Gate', required=False)
    arrival_is_boarding_bridge = forms.BooleanField(label='Through jet bridge?', required=False)
    arrival_schedule_time = forms.TimeField(label='Schedule time', required=False)
    arrival_actual_time = forms.TimeField(label='Actual time', required=False)
    arrival_runway = forms.CharField(label='Active runway', required=True)

    def save_arrival_flight_info(self, flight: Flight):
        data_for_flight_info = {
            'status': 'Arrival',
            'airport_code': self.cleaned_data['arrival_airport_code'],
            'metar': self.cleaned_data['arrival_metar'],
            'gate': self.cleaned_data['arrival_gate'],
            'is_boarding_bridge': self.cleaned_data['arrival_is_boarding_bridge'],
            'schedule_time': self.cleaned_data['arrival_schedule_time'],
            'actual_time': self.cleaned_data['arrival_actual_time'],
            'runway': self.cleaned_data['arrival_runway'],
            'flight': flight
        }
        flight_info_instance, _ = FlightInfo.objects.get_or_create(**data_for_flight_info)
        return flight_info_instance


class TrackImageForm(forms.Form):
    track_img = forms.ImageField(label='Фото трэка', required=False)

    # def save_track_img(self, trip: UserTrip):
    #     data_for_track = {
    #         'track_img': self.cleaned_data['track_img'],
    #         'trip': trip
    #     }
    #     track_img_instance, _ = FlightInfo.objects.get_or_create(**data_for_track)
    #     return track_img_instance

    def save_track_images(self, trip: UserTrip):
        track_image_instances = []

        for field_name, uploaded_file in self.files.items():
            print(field_name, field_name.startswith('track_image'), self.files.items())
            if field_name.startswith('track_image'):
                track_image_instance, _ = TrackImage.objects.get_or_create(
                    track_img=uploaded_file,
                    trip=trip
                )
                track_image_instances.append(track_image_instance)
                print('save one track')
        return track_image_instances


class AddFlightForm(AircraftTypeForm,
                    AirlineForm,
                    AirframeForm,
                    FlightForm,
                    UserTripForm,
                    MealForm,
                    DepartureFlightInfoForm,
                    ArrivalFlightInfoForm,
                    TrackImageForm,
                    forms.Form,
                    ):

    def save(self):
        with transaction.atomic():
            # tab1
            aircraft_type_instance = self.save_aircraft_type()
            airline_instance = self.save_airline()
            airframe_instance = self.save_airframe(aircraft_type_instance, airline_instance)
            flight_instance = self.save_flight(airframe_instance)

            # tab2
            user_trip_instance = self.save_user_trip(flight_instance)

            # tab3
            meal_instance = self.save_meal(user_trip_instance)

            # tab4
            departure_flight_info_instance = self.save_departure_flight_info(flight_instance)
            arrival_flight_info_instance = self.save_arrival_flight_info(flight_instance)

            # tab5
            track_image_instances = self.save_track_images(user_trip_instance)