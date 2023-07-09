from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.forms import modelformset_factory
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, CreateView, FormView, UpdateView
from .forms import AddFlightForm, MealForm
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
        data, files, id_dict = FlightDetailService.get_flight_details(usertripslug)
        track_images_in_db = data.get('track_images')
        meal = get_object_or_404(Meal, pk=id_dict['meal_id'])

        TrackImageFormset = modelformset_factory(TrackImage, fields=('track_img',), extra=2)
        formset = TrackImageFormset(queryset=track_images_in_db)
        form = AddFlightForm(initial={**data, **files})
        form_meal = MealForm(instance=meal)

        context = {
            'form_meal': form_meal,
            'form': form,
            'formset': formset,
            'title': 'Edit Flight',
            'view_name': 'flight_update',
            'url_args': usertripslug
        }
        return render(request, self.template_name, context=context)

    def get_files(self, request, usertripslug: str):
        _, files, _ = FlightDetailService.get_flight_details(usertripslug)
        files.update(request.FILES.dict())
        return files

    def post(self, request, usertripslug):
        _, files, id_dict = FlightDetailService.get_flight_details(usertripslug)
        trip = get_object_or_404(UserTrip, slug=usertripslug)
        meal = get_object_or_404(Meal, pk=id_dict['meal_id'])

        form = AddFlightForm(data=request.POST, files=self.get_files(request, usertripslug))

        TrackImageFormset = modelformset_factory(TrackImage, fields=('track_img',), extra=2)
        formset = TrackImageFormset(request.POST or None, request.FILES or None)

        form_meal = MealForm(data=request.POST, files=request.FILES, instance=meal)

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():
                usertrip_instance = form.save(user=request.user, **id_dict)
                form_meal.save(trip=usertrip_instance)

                for index, f in enumerate(formset):
                    if f.cleaned_data:

                        if f.cleaned_data.get('id') is None:
                            # Мы загрузили новое изображение в форму

                            track_image_instance = TrackImage(trip=trip, track_img=f.cleaned_data.get('track_img'))
                            track_image_instance.save()
                        elif f.cleaned_data.get('track_img') is False:
                            # Мы поставили галочку напротив очистить
                            id = f.cleaned_data.get('id').id

                            track_image_instance = TrackImage.objects.get(pk=id)
                            track_image_instance.delete()
                        else:
                            # Если изображение было загружено ранее (то есть у него уже есть id в бд)
                            id = f.cleaned_data.get('id').id

                            track_image_instance_in_db = TrackImage.objects.get(pk=id)
                            track_image_instance_in_db.track_img = \
                                TrackImage(trip=trip, track_img=f.cleaned_data.get('track_img')).track_img
                            track_image_instance_in_db.save()

            return redirect('flight', usertripslug=usertripslug)
        else:
            print(formset.errors)
            print(formset.non_form_errors())

        context = {
            'title': 'Edit Flight',
            'form_meal': form_meal,
            'form': form,
            'formset': formset,
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
