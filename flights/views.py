from django.db.models import Count, Prefetch
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, CreateView, FormView
from .forms import AddFlightForm
from .services import FlightInformationService, PassengerService, PassengerProfileService, FlightDetailService

from .models import *


class HomeView(ListView):
    template_name = 'flights/index.html'
    queryset = FlightInformationService.get_latest_cards()
    context_object_name = 'latest_cards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_users'] = FlightInformationService.get_top_users()
        context['site_information'] = FlightInformationService.get_site_information()

        return context


class PassengersView(ListView):
    template_name = 'flights/passengers.html'
    context_object_name = 'passengers'

    def get_queryset(self):
        return PassengerService.get_all_passengers_with_statistic()


class ProfileView(DetailView):
    template_name = 'flights/profile.html'
    slug_field = 'passenger__username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flights'] = PassengerProfileService.get_passenger_flights(self.kwargs['username'])

        return context

    def get_object(self):
        return PassengerProfileService.get_profile_information(self.kwargs['username'])


class FlightView(DetailView):
    template_name = 'flights/flight.html'
    slug_url_kwarg = 'usertripslug'
    context_object_name = 'flight'

    def get_object(self):
        return FlightDetailService.get_flight_details(self.kwargs['usertripslug'])


class AddFlightView(FormView):
    form_class = AddFlightForm
    template_name = 'flights/add_flight.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        print('Before save')
        form.save()
        print('After save')
        return super().form_valid(form)

    def form_invalid(self, form):
        print('Form is invalid:')
        for field, errors in form.errors.items():
            field_label = form.fields[field].label
            print(f"Field: {field} ({field_label})")
            for error in errors:
                print(f"Error: {error}")
        return super().form_invalid(form)


# def add_flight(request):
#     form = AddFlightForm()
#     context = {
#         'form': form
#     }
#     return render(request, 'flights/add_flight.html', context=context)
