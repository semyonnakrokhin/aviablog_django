from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, CreateView, FormView, UpdateView
from .forms import AddFlightForm, TrackImageForm
from .services import FlightInformationService, PassengerService, PassengerProfileService, FlightDetailService

from .models import *
from pprint import pprint



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
        data, files, _ = FlightDetailService.get_flight_details(self.kwargs['usertripslug'])
        return {**data, **files}


class FlightUpdateView(View):
    template_name = 'flights/add_flight.html'
    form_class = AddFlightForm

    def get(self, request, usertripslug):
        data, files, _ = FlightDetailService.get_flight_details(usertripslug)

        form = AddFlightForm(initial={**data, **files})

        context = {
            'form': form,
            'title': 'Edit Flight',
            'view_name': 'flight_update',
            'url_args': usertripslug
        }
        return render(request, self.template_name, context=context)

    def post(self, request, usertripslug):
        _, files, id_dict = FlightDetailService.get_flight_details(usertripslug)


        # TrackImageFormset = formset_factory(TrackImageForm, extra=2)
        # formset = TrackImageFormset()

        pprint(request.POST)
        print('_____________')
        print('FILES BEFORE adding request.FILES')
        pprint(files)

        files.update(request.FILES.dict())

        print('FILES AFTER adding request.FILES')
        pprint(files)

        form = AddFlightForm(request.POST, files)

        if form.is_valid():
            form.save(user=request.user, **id_dict)
            return redirect('flight', usertripslug=usertripslug)
        else:
            # Если форма не прошла валидацию, выведите ошибку в консоль
            print(form.errors)

        context = {
            'title': 'Edit Flight',
            'form': form,
            'view_name': 'flight_update',
            'url_args': usertripslug
        }
        return render(request, self.template_name, context=context)


class AddFlightView(LoginRequiredMixin, FormView):
    form_class = AddFlightForm
    template_name = 'flights/add_flight.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save(user=self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_name'] = 'add_flight'
        context['url_args'] = ''
        context['title'] = 'Add New Flight'
        return context

